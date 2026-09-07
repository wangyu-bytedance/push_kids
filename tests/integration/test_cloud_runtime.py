from __future__ import annotations

from datetime import UTC, datetime

import pytest
from push_kids.media.store import WeChatCloudMediaStore
from push_kids.notifications.providers import WeChatSubscribeSender
from push_kids.notifications.service import build_channel
from push_kids.persistence.models import (
    Family,
    FamilyMember,
    MediaObject,
    MediaState,
    WeChatActorBinding,
)
from push_kids.platform.config import Settings
from push_kids.platform.context import subject_hmac
from pydantic import SecretStr

from tests.conftest import NOTIFICATION_TEMPLATES


class _Body:
    def __init__(self, content: bytes) -> None:
        self.content = content

    def get_raw_stream(self):
        return self

    def read(self, _size: int) -> bytes:
        return self.content

    def close(self) -> None:
        return None


class _CosClient:
    def __init__(self, content: bytes) -> None:
        self.content = content
        self.deleted_keys: list[str] = []

    def head_object(self, **_kwargs):
        return {"x-cos-meta-fileid": "signed-meta"}

    def get_object(self, **_kwargs):
        return {"Body": _Body(self.content)}

    def delete_object(self, **kwargs):
        self.deleted_keys.append(kwargs["Key"])
        return {}


class FakeWeChatCloudMediaStore(WeChatCloudMediaStore):
    def __init__(self, settings: Settings, owner_openid: str) -> None:
        super().__init__(settings)
        self.owner_openid = owner_openid
        self.client = _CosClient(b"\x89PNG\r\n\x1a\nvalid-cloud-image")

    def _client(self):
        return self.client

    def _request_json(self, _url: str, body=None):
        assert body == {"metaid": "signed-meta"}
        return {
            "errcode": 0,
            "respdata": {
                "raw_data": {
                    "openid": self.owner_openid,
                    "bucket": self.bucket,
                    "path": "/" + self.expected_path,
                }
            },
        }


def _cloud_settings() -> Settings:
    return Settings(
        PUSH_KIDS_ENV="cloud",
        PUSH_KIDS_DATABASE_URL="sqlite:///:memory:",
        PUSH_KIDS_MEDIA_BACKEND="wechat_cloud",
        CBR_ENV_ID="prod-test",
        WECHAT_APP_ID="wx-test-app",
        WECHAT_SERVICE_NAME="push-kids",
        COS_BUCKET="bucket-test",
        COS_REGION="ap-guangzhou",
        PUSH_KIDS_ACTOR_HMAC_KEY="a" * 32,
        PUSH_KIDS_AI_PROVIDER="test",
    )


def _cloud_headers() -> dict[str, str]:
    return {
        "X-WX-SOURCE": "wx_client",
        "X-WX-OPENID": "openid-parent-a",
        "X-WX-APPID": "wx-test-app",
        "X-WX-ENV": "prod-test",
    }


@pytest.mark.parametrize("ark_api_key", [None, "", "   "])
def test_cloud_ark_requires_non_blank_runtime_secret(ark_api_key: str | None) -> None:
    settings = _cloud_settings()
    settings.database_url = "mysql+pymysql://app:secret@mysql.internal/push_kids"
    settings.ai_provider = "ark"
    settings.ark_api_key = SecretStr(ark_api_key) if ark_api_key is not None else None

    with pytest.raises(ValueError, match="ARK_API_KEY") as error:
        settings.validate_cloud_runtime()

    assert str(error.value) == "云环境使用 Ark 时必须配置 ARK_API_KEY"


def test_cloud_ark_accepts_masked_runtime_secret() -> None:
    sentinel = "ark-test-secret-sentinel"
    settings = _cloud_settings()
    settings.database_url = "mysql+pymysql://app:secret@mysql.internal/push_kids"
    settings.ai_provider = "ark"
    settings.ark_api_key = SecretStr(sentinel)

    settings.validate_cloud_runtime()

    assert sentinel not in repr(settings)


def test_cloud_notification_channel_requires_key_templates_and_a_tick_owner() -> None:
    """云环境不能只把开关打开：没有密钥、模板或调度所有者时必须拒绝启动。"""
    settings = _cloud_settings()
    settings.database_url = "mysql+pymysql://app:secret@mysql.internal/push_kids"
    settings.notification_channel = "recording"
    with pytest.raises(ValueError, match="recording"):
        settings.validate_cloud_runtime()

    settings.notification_channel = "wechat"
    with pytest.raises(ValueError, match="NOTIFICATION_SECRET_KEY"):
        settings.validate_cloud_runtime()

    secret = "notification-secret-sentinel-value-32"
    settings.notification_secret_key = SecretStr(secret)
    with pytest.raises(ValueError, match="NOTIFICATION_TEMPLATES"):
        settings.validate_cloud_runtime()

    settings.notification_templates = NOTIFICATION_TEMPLATES
    settings.validate_cloud_runtime()
    # 关掉进程内调度就必须有外部触发凭据，否则提醒永远不会被执行。
    settings.run_notification_scheduler = False
    with pytest.raises(ValueError, match="NOTIFICATION_TRIGGER_TOKEN"):
        settings.validate_cloud_runtime()
    settings.notification_trigger_token = SecretStr("trigger-token-sentinel")
    settings.validate_cloud_runtime()
    assert secret not in repr(settings)


def test_cloud_deployment_never_accepts_a_local_receiver() -> None:
    """云上只能绑定微信返回的接收标识，不能退回到本地调试身份。"""
    settings = _cloud_settings()
    settings.database_url = "mysql+pymysql://app:secret@mysql.internal/push_kids"
    settings.notification_channel = "wechat"
    settings.notification_secret_key = SecretStr("notification-secret-sentinel-value-32")
    settings.notification_templates = NOTIFICATION_TEMPLATES
    channel = build_channel(settings)
    assert channel.available is True
    assert channel.local_receiver_allowed is False
    assert isinstance(channel.sender, WeChatSubscribeSender)


def _bind_family(db, family_id: str) -> None:
    binding = WeChatActorBinding(
        app_id="wx-test-app",
        subject_hmac=subject_hmac("a" * 32, "wx-test-app", "openid-parent-a"),
        family_id=family_id,
    )
    db.add_all([Family(id=family_id, display_name="测试家庭"), binding])
    db.flush()
    db.add(
        FamilyMember(
            family_id=family_id,
            actor_binding_id=binding.id,
            active_actor_binding_id=binding.id,
            role="manager",
            relationship_label="家长",
        )
    )
    db.commit()


def test_cloud_storage_uses_platform_cos_variables_without_cloud_prefix() -> None:
    settings = _cloud_settings()
    settings.database_url = "mysql+pymysql://app:secret@mysql.internal/push_kids"

    settings.validate_cloud_runtime()

    assert settings.wechat_storage_bucket == "bucket-test"
    assert settings.wechat_storage_region == "ap-guangzhou"
    store = FakeWeChatCloudMediaStore(settings, "openid-parent-a")
    assert store._object_path("cloud://prod-test/uploads/example.png") == "uploads/example.png"


def test_cloud_identity_rejects_public_family_header_and_resolves_binding(
    client, app, family_headers, child
) -> None:
    settings = _cloud_settings()
    with app.state.database.session_factory() as db:
        _bind_family(db, family_headers["X-Family-ID"])
    app.state.settings = settings

    assert client.get("/api/v1/children").status_code == 401
    assert client.get("/api/v1/children", headers=family_headers).status_code == 403
    wrong = {**_cloud_headers(), "X-WX-APPID": "wx-other"}
    assert client.get("/api/v1/children", headers=wrong).status_code == 403
    response = client.get("/api/v1/children", headers=_cloud_headers())
    assert response.status_code == 200
    assert [item["id"] for item in response.json()] == [child["id"]]


def test_cloud_photo_ticket_upload_claim_and_finalize(client, app, family_headers, child) -> None:
    settings = _cloud_settings()
    with app.state.database.session_factory() as db:
        _bind_family(db, family_headers["X-Family-ID"])
    store = FakeWeChatCloudMediaStore(settings, "openid-parent-a")
    app.state.settings = settings
    app.state.media_store = store
    app.state.worker.media_store = store
    headers = _cloud_headers()

    legacy_upload = client.post(
        "/api/v1/submissions/upload",
        headers=headers,
        data={"child_id": child["id"], "occurred_at": datetime.now(UTC).isoformat()},
        files={"files": ("legacy.png", b"\x89PNG\r\n\x1a\nlegacy", "image/png")},
    )
    assert legacy_upload.status_code == 409
    assert legacy_upload.json()["error"]["message"] == "云环境请使用对象存储直传"

    draft = client.post(
        "/api/v1/submissions/photo-drafts",
        headers={**headers, "Idempotency-Key": "photo-cloud-batch-001"},
        json={
            "child_id": child["id"],
            "occurred_at": datetime.now(UTC).isoformat(),
            "input_text": "数学作业",
        },
    )
    assert draft.status_code == 202
    ticket = client.post(
        "/api/v1/media/upload-tickets",
        headers={**headers, "Idempotency-Key": "photo-cloud-batch-001-media-0"},
        json={
            "submission_id": draft.json()["id"],
            "content_type": "image/png",
            "byte_size": 25,
        },
    )
    assert ticket.status_code == 201
    store.expected_path = ticket.json()["cloud_path"]
    file_id = f"cloud://prod-test/{store.expected_path}"
    claimed = client.post(
        "/api/v1/media/claims",
        headers=headers,
        json={"ticket_id": ticket.json()["ticket_id"], "file_id": file_id},
    )
    assert claimed.status_code == 200
    assert claimed.json()["media_count"] == 1
    duplicate = client.post(
        "/api/v1/media/claims",
        headers=headers,
        json={"ticket_id": ticket.json()["ticket_id"], "file_id": file_id},
    )
    assert duplicate.status_code == 200
    finalized = client.post(f"/api/v1/submissions/{draft.json()['id']}/finalize", headers=headers)
    assert finalized.status_code == 200
    late_ticket = client.post(
        "/api/v1/media/upload-tickets",
        headers={**headers, "Idempotency-Key": "photo-cloud-batch-001-media-late"},
        json={
            "submission_id": draft.json()["id"],
            "content_type": "image/png",
            "byte_size": 25,
        },
    )
    assert late_ticket.status_code == 409
    assert app.state.worker.process_one() is True
    detail = client.get(f"/api/v1/submissions/{draft.json()['id']}", headers=headers)
    assert detail.json()["state"] == "pending_confirmation"
    cancelled = client.post(f"/api/v1/submissions/{draft.json()['id']}/cancel", headers=headers)
    assert cancelled.status_code == 200
    assert cancelled.json()["state"] == "cancelled"
    assert store.client.deleted_keys == [store.expected_path]
    with app.state.database.session_factory() as db:
        media_object = db.get(MediaObject, ticket.json()["ticket_id"])
        assert media_object is not None
        assert media_object.state == MediaState.deleted.value


def test_cloud_claim_rejects_metadata_owned_by_another_user(
    client, app, family_headers, child
) -> None:
    settings = _cloud_settings()
    with app.state.database.session_factory() as db:
        _bind_family(db, family_headers["X-Family-ID"])
    store = FakeWeChatCloudMediaStore(settings, "openid-other")
    app.state.settings = settings
    app.state.media_store = store
    headers = _cloud_headers()
    draft = client.post(
        "/api/v1/submissions/photo-drafts",
        headers={**headers, "Idempotency-Key": "photo-cloud-owner-001"},
        json={"child_id": child["id"], "occurred_at": datetime.now(UTC).isoformat()},
    ).json()
    ticket = client.post(
        "/api/v1/media/upload-tickets",
        headers={**headers, "Idempotency-Key": "photo-cloud-owner-001-media-0"},
        json={
            "submission_id": draft["id"],
            "content_type": "image/png",
            "byte_size": 25,
        },
    ).json()
    store.expected_path = ticket["cloud_path"]
    response = client.post(
        "/api/v1/media/claims",
        headers=headers,
        json={
            "ticket_id": ticket["ticket_id"],
            "file_id": f"cloud://prod-test/{store.expected_path}",
        },
    )
    assert response.status_code == 400
    assert response.json()["error"]["message"] == "上传文件归属校验失败"


def test_cloud_store_rejects_file_id_without_resource_prefix() -> None:
    store = FakeWeChatCloudMediaStore(_cloud_settings(), "openid-parent-a")

    try:
        store._object_path("cloud://uploads")
    except ValueError as exc:
        assert str(exc) == "非法云存储文件 ID"
    else:
        raise AssertionError("expected malformed file ID to be rejected")
