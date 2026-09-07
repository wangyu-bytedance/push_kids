"""Encrypted receiver identity.

The repository rule is that a raw OpenID never lands in the database or in logs, but the WeChat
subscribe-message API needs one as `touser` and the dispatcher runs without a request context. The
compromise recorded in the Spec is application-layer AES-GCM: the key lives only in runtime
configuration, the ciphertext lives in the row, and nothing is indexed by the plaintext.
"""

from __future__ import annotations

import base64
import hashlib
import hmac

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

NONCE_BYTES = 12
TAG_BYTES = 16
KEY_VERSION = "v1"


class DestinationCipherError(RuntimeError):
    """Raised when stored ciphertext cannot be authenticated with the configured key."""


class DestinationCipher:
    def __init__(self, secret: str, version: str = KEY_VERSION) -> None:
        if len(secret) < 32:
            raise ValueError("通知加密密钥至少需要 32 个字符")
        self._key = hashlib.sha256(f"push-kids-destination:{secret}".encode()).digest()
        self._index_key = hashlib.sha256(f"push-kids-destination-index:{secret}".encode()).digest()
        self.version = version

    def fingerprint(self, plaintext: str) -> str:
        """Keyed one-way lookup value for an external receiver id.

        WeChat pushes subscription events keyed by the plaintext OpenID, and AES-GCM ciphertext is
        randomised, so a row cannot be found by re-encrypting. This HMAC gives an equality-only
        index derived from a separate key: it is not reversible and reveals nothing on its own,
        which keeps the "no plaintext receiver in the database" rule intact.
        """
        return hmac.new(self._index_key, plaintext.encode(), hashlib.sha256).hexdigest()

    def encrypt(self, plaintext: str) -> str:
        cipher = AES.new(self._key, AES.MODE_GCM, nonce=get_random_bytes(NONCE_BYTES))
        body, tag = cipher.encrypt_and_digest(plaintext.encode())
        return base64.b64encode(bytes(cipher.nonce) + tag + body).decode()

    def decrypt(self, ciphertext: str) -> str:
        try:
            blob = base64.b64decode(ciphertext.encode())
        except (ValueError, TypeError) as exc:
            raise DestinationCipherError("通知接收标识无法解码") from exc
        if len(blob) <= NONCE_BYTES + TAG_BYTES:
            raise DestinationCipherError("通知接收标识长度不合法")
        nonce = blob[:NONCE_BYTES]
        tag = blob[NONCE_BYTES : NONCE_BYTES + TAG_BYTES]
        body = blob[NONCE_BYTES + TAG_BYTES :]
        cipher = AES.new(self._key, AES.MODE_GCM, nonce=nonce)
        try:
            return cipher.decrypt_and_verify(body, tag).decode()
        except (ValueError, KeyError) as exc:
            raise DestinationCipherError("通知接收标识校验失败") from exc
