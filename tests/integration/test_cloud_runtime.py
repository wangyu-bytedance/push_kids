from __future__ import annotations

from datetime import UTC, datetime

from push_kids.media.store import WeChatCloudMediaStore
from push_kids.persistence.models import MediaObject, MediaState, WeChatActorBinding
from push_kids.platform.config import Settings
from push_kids.platform.context import subject_hmac


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
        WECHAT_STORAGE_BUCKET="bucket-test",
        WECHAT_STORAGE_CLOUD_PREFIX="cloud://prod-test",
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


def test_cloud_identity_rejects_public_family_header_and_resolves_binding(
    client, app, family_headers, child
) -> None:
    settings = _cloud_settings()
    with app.state.database.session_factory() as db:
        db.add(
            WeChatActorBinding(
                app_id="wx-test-app",
                subject_hmac=subject_hmac("a" * 32, "wx-test-app", "openid-parent-a"),
                family_id=family_headers["X-Family-ID"],
            )
        )
        db.commit()
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
        db.add(
            WeChatActorBinding(
                app_id="wx-test-app",
                subject_hmac=subject_hmac("a" * 32, "wx-test-app", "openid-parent-a"),
                family_id=family_headers["X-Family-ID"],
            )
        )
        db.commit()
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
        db.add(
            WeChatActorBinding(
                app_id="wx-test-app",
                subject_hmac=subject_hmac("a" * 32, "wx-test-app", "openid-parent-a"),
                family_id=family_headers["X-Family-ID"],
            )
        )
        db.commit()
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
