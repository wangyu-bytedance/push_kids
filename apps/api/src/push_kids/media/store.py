from __future__ import annotations

import hashlib
import json
import tempfile
from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import UploadFile

from push_kids.platform.config import Settings
from push_kids.platform.errors import DependencyError, GoneError

ALLOWED_IMAGE_TYPES = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def _matches_declared_image_type(content: bytes, content_type: str) -> bool:
    if content_type == "image/jpeg":
        return content.startswith(b"\xff\xd8\xff")
    if content_type == "image/png":
        return content.startswith(b"\x89PNG\r\n\x1a\n")
    if content_type == "image/webp":
        return len(content) >= 12 and content[:4] == b"RIFF" and content[8:12] == b"WEBP"
    return False


def _detected_image_type(content: bytes) -> tuple[str, str]:
    for content_type, suffix in ALLOWED_IMAGE_TYPES.items():
        if _matches_declared_image_type(content, content_type):
            return content_type, suffix
    raise ValueError("仅支持内容有效的 JPG、PNG 或 WebP 图片")


@dataclass(frozen=True)
class StoredMedia:
    path: str
    content_type: str
    byte_size: int


@dataclass(frozen=True)
class ClaimedMedia:
    storage_ref: str
    content_type: str
    byte_size: int
    sha256: str


class MediaStore(Protocol):
    @contextmanager
    def materialize(self, storage_ref: str) -> Iterator[Path]: ...

    def delete(self, storage_ref: str) -> None: ...


class LocalMediaStore:
    def __init__(self, root: Path, max_bytes: int) -> None:
        self.root = root.resolve()
        self.max_bytes = max_bytes

    async def save(self, family_id: str, submission_id: str, upload: UploadFile) -> StoredMedia:
        content_type = upload.content_type or ""
        if content_type not in ALLOWED_IMAGE_TYPES:
            raise ValueError("仅支持 JPG、PNG 或 WebP 图片")
        content = await upload.read(self.max_bytes + 1)
        if not content or len(content) > self.max_bytes:
            raise ValueError(f"单张图片需小于 {self.max_bytes // 1024 // 1024}MB")
        if not _matches_declared_image_type(content, content_type):
            raise ValueError("图片内容与格式不匹配")
        family_hash = hashlib.sha256(family_id.encode()).hexdigest()[:16]
        digest = hashlib.sha256(content).hexdigest()
        directory = (self.root / family_hash / submission_id).resolve()
        if self.root not in directory.parents:
            raise ValueError("非法存储路径")
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{digest}{ALLOWED_IMAGE_TYPES[content_type]}"
        path.write_bytes(content)
        return StoredMedia(str(path), content_type, len(content))

    @contextmanager
    def materialize(self, storage_ref: str) -> Iterator[Path]:
        path = Path(storage_ref).resolve()
        if self.root not in path.parents:
            raise ValueError("非法存储路径")
        yield path

    def delete(self, storage_ref: str) -> None:
        path = Path(storage_ref).resolve()
        if self.root not in path.parents:
            raise ValueError("非法存储路径")
        path.unlink(missing_ok=True)


class WeChatCloudMediaStore:
    auth_url = "http://api.weixin.qq.com/_/cos/getauth"
    decode_url = "http://api.weixin.qq.com/_/cos/metaid/decode"

    def __init__(self, settings: Settings) -> None:
        if not settings.wechat_storage_bucket:
            raise ValueError("微信云托管对象存储配置不完整")
        self.bucket = settings.wechat_storage_bucket
        self.region = settings.wechat_storage_region
        self.max_bytes = settings.upload_max_bytes

    @staticmethod
    def _request_json(url: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        payload = json.dumps(body).encode() if body is not None else None
        request = Request(
            url,
            data=payload,
            method="POST" if body is not None else "GET",
            headers={"Content-Type": "application/json"} if body is not None else {},
        )
        try:
            with urlopen(request, timeout=8) as response:  # noqa: S310 - fixed platform URL
                result = json.loads(response.read())
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise DependencyError("对象存储暂时不可用，请稍后重试") from exc
        if not isinstance(result, dict):
            raise DependencyError("对象存储返回了无效响应")
        return result

    def _client(self):
        from qcloud_cos import CosConfig, CosS3Client

        auth = self._request_json(self.auth_url)
        credentials = auth.get("Credentials") or auth
        try:
            config = CosConfig(
                Region=self.region,
                SecretId=credentials["TmpSecretId"],
                SecretKey=credentials["TmpSecretKey"],
                Token=credentials["Token"],
                Scheme="https",
            )
        except KeyError as exc:
            raise DependencyError("对象存储临时凭证缺少必要字段") from exc
        return CosS3Client(config)

    def _object_path(self, storage_ref: str) -> str:
        if not storage_ref.startswith("cloud://"):
            raise ValueError("非法云存储文件 ID")
        resource, separator, path = storage_ref.removeprefix("cloud://").partition("/")
        if not resource or not separator:
            raise ValueError("非法云存储文件 ID")
        if not path or path.startswith("/") or ".." in Path(path).parts:
            raise ValueError("非法云存储路径")
        return path

    @staticmethod
    def _read_body(response: dict[str, Any], max_bytes: int) -> bytes:
        body = response.get("Body")
        if body is None:
            raise DependencyError("对象存储下载响应缺少文件内容")
        stream = body.get_raw_stream() if hasattr(body, "get_raw_stream") else body
        content = stream.read(max_bytes + 1)
        if hasattr(stream, "close"):
            stream.close()
        if not content or len(content) > max_bytes:
            raise ValueError(f"单张图片需小于 {max_bytes // 1024 // 1024}MB")
        return content

    def _download(self, path: str) -> bytes:
        try:
            response = self._client().get_object(Bucket=self.bucket, Key=path)
            return self._read_body(response, self.max_bytes)
        except (ValueError, DependencyError):
            raise
        except Exception as exc:
            raise DependencyError("对象存储文件读取失败，请重新上传") from exc

    def claim(self, storage_ref: str, expected_path: str, uploader_openid: str) -> ClaimedMedia:
        path = self._object_path(storage_ref)
        if path != expected_path:
            raise ValueError("上传文件与签发路径不一致")
        try:
            head = self._client().head_object(Bucket=self.bucket, Key=path)
        except Exception as exc:
            raise DependencyError("对象存储文件不存在或暂不可读") from exc
        normalized_headers = {str(key).lower(): value for key, value in head.items()}
        metaid = normalized_headers.get("x-cos-meta-fileid")
        if not metaid:
            raise ValueError("上传文件缺少微信归属元数据")
        decoded = self._request_json(self.decode_url, {"metaid": metaid})
        if decoded.get("errcode") not in (None, 0):
            raise ValueError("上传文件归属元数据无效")
        raw = (decoded.get("respdata") or {}).get("raw_data") or {}
        decoded_path = str(raw.get("path") or "").lstrip("/")
        if (
            raw.get("openid") != uploader_openid
            or raw.get("bucket") != self.bucket
            or decoded_path != path
        ):
            raise ValueError("上传文件归属校验失败")
        content = self._download(path)
        content_type, _suffix = _detected_image_type(content)
        return ClaimedMedia(
            storage_ref=storage_ref,
            content_type=content_type,
            byte_size=len(content),
            sha256=hashlib.sha256(content).hexdigest(),
        )

    def delete_path(self, path: str) -> None:
        try:
            self._client().delete_object(Bucket=self.bucket, Key=path)
        except Exception as exc:
            raise DependencyError("对象存储清理失败") from exc

    def preview_url(self, storage_ref: str) -> str:
        """Issue a GET-only, one-object capability after application authorization."""
        path = self._object_path(storage_ref)
        try:
            client = self._client()
            head = client.head_object(Bucket=self.bucket, Key=path)
            size = int(head.get("Content-Length", head.get("ContentLength", 0)))
            if size > self.max_bytes:
                raise GoneError("图片超出允许大小")
            return client.get_presigned_url(
                Bucket=self.bucket,
                Key=path,
                Method="GET",
                Expired=60,
                Params={
                    "x-cos-security-token": client.get_conf()._token,
                    "response-cache-control": "no-store",
                },
            )
        except GoneError:
            raise
        except Exception as exc:
            if hasattr(exc, "get_status_code") and str(exc.get_status_code()) == "404":
                raise GoneError("原图已删除或不可用") from exc
            raise DependencyError("照片暂时无法读取，请重试") from exc

    def delete(self, storage_ref: str) -> None:
        self.delete_path(self._object_path(storage_ref))

    @contextmanager
    def materialize(self, storage_ref: str) -> Iterator[Path]:
        path = self._object_path(storage_ref)
        content = self._download(path)
        _content_type, suffix = _detected_image_type(content)
        with tempfile.TemporaryDirectory(prefix="push-kids-media-") as directory:
            local_path = Path(directory) / f"input{suffix}"
            local_path.write_bytes(content)
            try:
                yield local_path
            finally:
                local_path.unlink(missing_ok=True)


def build_media_store(settings: Settings) -> LocalMediaStore | WeChatCloudMediaStore:
    if settings.media_backend == "wechat_cloud":
        return WeChatCloudMediaStore(settings)
    return LocalMediaStore(settings.media_root, settings.upload_max_bytes)
