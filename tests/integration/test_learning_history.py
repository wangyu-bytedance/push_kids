from datetime import timedelta
from types import SimpleNamespace
from urllib.parse import quote

import pytest
from push_kids.media.store import WeChatCloudMediaStore
from push_kids.persistence.models import (
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    ReviewFeedback,
    ReviewItem,
    Subject,
)
from push_kids.platform.time import utcnow
from sqlalchemy import func, select


def confirmed(client, app, child, headers):
    sid = client.post(
        "/api/v1/submissions",
        headers=headers,
        json={
            "child_id": child["id"],
            "occurred_at": utcnow().isoformat(),
            "input_text": "数学原始加法文字",
        },
    ).json()["id"]
    app.state.worker.process_one()
    proposal = client.get(f"/api/v1/submissions/{sid}", headers=headers).json()["proposal"]
    proposal["summary"] = "家长确认后的总结"
    result = client.post(
        f"/api/v1/submissions/{sid}/confirm", headers=headers, json={"proposal": proposal}
    )
    assert result.status_code == 200
    return sid, result.json()


def test_history_pages_filters_detail_and_read_has_no_writes(client, app, child, family_headers):
    sid, result = confirmed(client, app, child, family_headers)
    with app.state.database.session_factory() as db:
        subject_id = db.get(LearningRecord, result["record_id"]).subject_id
        for n in range(105):
            occurred = utcnow() - timedelta(days=200 + n)
            submission = LearningSubmission(
                family_id=family_headers["X-Family-ID"],
                child_id=child["id"],
                occurred_at=occurred,
                state="confirmed",
                input_text=f"较早材料{n}",
            )
            db.add(submission)
            db.flush()
            db.add(
                LearningRecord(
                    family_id=submission.family_id,
                    child_id=child["id"],
                    subject_id=subject_id,
                    submission_id=submission.id,
                    occurred_at=occurred,
                    summary=f"历史内容{n}",
                    source="人工录入",
                )
            )
        db.commit()
        before = [
            db.scalar(select(func.count()).select_from(model))
            for model in (LearningRecord, KnowledgeOccurrence, ReviewItem, ReviewFeedback)
        ]
    base = f"/api/v1/children/{child['id']}/history"
    params = {"view": "confirmed", "limit": 20}
    items = []
    while True:
        response = client.get(base, headers=family_headers, params=params)
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data["items"]) <= 20
        items += data["items"]
        if not data["next_cursor"]:
            break
        params["cursor"] = data["next_cursor"]
    assert len(items) == len({i["submission_id"] for i in items}) == 106
    assert items[0]["summary"] == "家长确认后的总结"
    assert items[-1]["summary"] == "历史内容104"
    detail = client.get(f"{base}/{sid}", headers=family_headers).json()
    assert detail["record"]["summary"] == "家长确认后的总结"
    assert detail["input_text"] == "数学原始加法文字"
    assert detail["knowledge"]
    for q in ["原始", "家长确认", detail["knowledge"][0]["name"]]:
        assert client.get(
            base,
            headers={**family_headers, "X-History-Query": quote(q)},
            params={"view": "confirmed"},
        ).json()["items"]
    assert (
        client.get(
            base, headers={**family_headers, "X-History-Query": "%25"}, params={"view": "confirmed"}
        ).json()["items"]
        == []
    )
    assert (
        client.get(
            base,
            headers=family_headers,
            params={"view": "confirmed", "from": "2026-09-06", "to": "2026-09-05"},
        ).status_code
        == 400
    )
    assert (
        client.get(
            base, headers=family_headers, params={"view": "all", "cursor": params["cursor"]}
        ).status_code
        == 400
    )
    with app.state.database.session_factory() as db:
        after = [
            db.scalar(select(func.count()).select_from(model))
            for model in (LearningRecord, KnowledgeOccurrence, ReviewItem, ReviewFeedback)
        ]
    assert before == after


def test_history_scope_pending_counts_and_feedback_pagination(client, app, child, family_headers):
    sid, result = confirmed(client, app, child, family_headers)
    base = f"/api/v1/children/{child['id']}/history"
    client.post(
        "/api/v1/submissions/photo-drafts",
        headers=family_headers,
        json={
            "child_id": child["id"],
            "occurred_at": utcnow().isoformat(),
        },
    )
    pending = client.get(
        base,
        headers={**family_headers, "X-History-Query": "no%20match"},
        params={"view": "pending"},
    ).json()
    assert pending["items"] == [] and pending["pending_count"] == 1
    all_items = client.get(base, headers=family_headers, params={"view": "all"}).json()["items"]
    assert len(all_items) == 2
    rid = result["review_item_ids"][0]
    with app.state.database.session_factory() as db:
        review = db.get(ReviewItem, rid)
        review.due_date = utcnow().date() - timedelta(days=1)
        for n in range(7):
            db.add(
                ReviewFeedback(
                    family_id=family_headers["X-Family-ID"],
                    review_item_id=rid,
                    action="complete",
                    occurred_at=utcnow() - timedelta(days=n),
                )
            )
        db.commit()
    response = client.get(f"{base}/{sid}/reviews", headers=family_headers)
    assert response.status_code == 200, response.text
    first = next(i for i in response.json()["items"] if i["review_id"] == rid)
    assert first["is_due"] and len(first["feedback"]) == 3
    second = client.get(
        f"{base}/{sid}/reviews",
        headers=family_headers,
        params={"review_id": rid, "before": first["next_before"]},
    ).json()["items"][0]
    assert len(second["feedback"]) == 3
    assert not {f["id"] for f in first["feedback"]} & {f["id"] for f in second["feedback"]}
    assert (
        client.get(f"{base}/{sid}/reviews?review_id=unrelated", headers=family_headers).status_code
        == 404
    )
    for suffix in ["?view=all", f"/{sid}", f"/{sid}/reviews"]:
        assert client.get(base + suffix, headers={"X-Family-ID": "other-family"}).status_code == 404
    with app.state.database.session_factory() as db:
        review = db.get(ReviewItem, rid)
        review.active = False
        db.commit()
    closed = client.get(f"{base}/{sid}/reviews", headers=family_headers).json()["items"]
    assert not next(i for i in closed if i["review_id"] == rid)["is_due"]
    with app.state.database.session_factory() as db:
        knowledge = db.get(KnowledgeItem, review.knowledge_item_id)
        db.get(Subject, knowledge.subject_id).kind = "activity"
        db.commit()
    assert client.get(f"{base}/{sid}/reviews", headers=family_headers).json()["items"] == []


def test_original_media_is_authenticated_and_cancelled_media_is_gone(
    client, app, child, family_headers
):
    photo = b"\x89PNG\r\n\x1a\n" + b"synthetic-fixture"
    result = client.post(
        "/api/v1/submissions/upload",
        headers=family_headers,
        data={
            "child_id": child["id"],
            "occurred_at": utcnow().isoformat(),
            "defer_analysis": "true",
        },
        files={"files": ("fixture.png", photo, "image/png")},
    )
    assert result.status_code == 202
    sid = result.json()["id"]
    detail = client.get(
        f"/api/v1/children/{child['id']}/history/{sid}", headers=family_headers
    ).json()
    mid = detail["media"][0]["id"]
    path = f"/api/v1/submissions/{sid}/media/{mid}/preview?child_id={child['id']}"
    manifest = client.get(path, headers=family_headers)
    assert manifest.status_code == 200
    assert manifest.headers["cache-control"] == "no-store"
    content = "/api/v1" + manifest.json()["download_path"]
    assert client.get(content, headers=family_headers).content == photo
    assert client.get(content, headers={"X-Family-ID": "foreign"}).status_code == 404
    assert (
        client.get(path.replace(child["id"], "wrong-child"), headers=family_headers).status_code
        == 404
    )
    assert client.get(path.replace(mid, "wrong-media"), headers=family_headers).status_code == 404
    assert client.get(path, headers={"X-Family-ID": "foreign"}).status_code == 404
    assert (
        client.post(f"/api/v1/submissions/{sid}/cancel", headers=family_headers).status_code == 200
    )
    assert client.get(path, headers=family_headers).status_code == 410
    assert client.get(content, headers=family_headers).status_code == 410


def test_cloud_preview_signs_exact_get_with_short_expiry_and_session_token(monkeypatch):
    store = object.__new__(WeChatCloudMediaStore)
    store.bucket = "test-bucket"
    store.max_bytes = 1024
    calls = []
    client = SimpleNamespace(
        head_object=lambda **kwargs: {"Content-Length": "24"},
        get_conf=lambda: SimpleNamespace(_token="synthetic-session-token"),
        get_presigned_url=lambda **kwargs: calls.append(kwargs) or "https://test.invalid/preview",
    )
    monkeypatch.setattr(store, "_client", lambda: client)
    assert store.preview_url("cloud://test-bucket/private/fixture.png").startswith("https://")
    assert calls[0]["Method"] == "GET" and calls[0]["Expired"] == 60
    assert calls[0]["Key"] == "private/fixture.png"
    assert calls[0]["Params"]["x-cos-security-token"] == "synthetic-session-token"
    with pytest.raises(ValueError):
        store.preview_url("cloud://test-bucket/../other")


def test_viewer_original_preview_and_removed_member_denial(client, app):
    owner = {"X-Debug-Actor": "history-owner"}
    viewer = {"X-Debug-Actor": "history-viewer"}
    created = client.post(
        "/api/v1/families",
        headers={**owner, "Idempotency-Key": "history-family"},
        json={
            "display_name": "测试家庭",
            "relationship_label": "家长",
            "child": {"name": "测试档案"},
        },
    ).json()
    child_id = created["children"][0]["id"]
    invite = client.post(
        "/api/v1/families/current/invites",
        headers={**owner, "Idempotency-Key": "history-invite"},
        json={"expires_in_hours": 24},
    ).json()
    application = client.post(
        "/api/v1/family-requests",
        headers={**viewer, "Idempotency-Key": "history-request"},
        json={"token": invite["token"], "relationship_label": "家人"},
    ).json()
    approval = client.post(
        f"/api/v1/family-requests/{application['id']}/approve",
        headers={**owner, "Idempotency-Key": "history-approval"},
        json={"role": "viewer"},
    )
    assert approval.status_code == 200, approval.text
    upload = client.post(
        "/api/v1/submissions/upload",
        headers=owner,
        data={"child_id": child_id, "occurred_at": utcnow().isoformat(), "defer_analysis": "true"},
        files={"files": ("fixture.png", b"\x89PNG\r\n\x1a\nsynthetic", "image/png")},
    ).json()
    sid = upload["id"]
    url = f"/api/v1/children/{child_id}/history/{sid}"
    detail = client.get(url, headers=viewer)
    assert detail.status_code == 200
    mid = detail.json()["media"][0]["id"]
    preview = f"/api/v1/submissions/{sid}/media/{mid}/preview?child_id={child_id}"
    assert client.get(preview, headers=viewer).status_code == 200
    assert client.post(f"/api/v1/submissions/{sid}/cancel", headers=viewer).status_code == 403
    assert (
        client.delete(
            f"/api/v1/families/current/members/{approval.json()['id']}", headers=owner
        ).status_code
        == 204
    )
    assert client.get(url, headers=viewer).status_code == 403
    assert client.get(preview, headers=viewer).status_code == 403


def test_preview_limiter_is_bounded_and_recovers(monkeypatch):
    from push_kids.media.preview_limit import MediaPreviewLimiter
    from push_kids.platform.errors import TooManyRequestsError

    monkeypatch.setattr("push_kids.media.preview_limit.monotonic", lambda: 100.0)
    limiter = MediaPreviewLimiter()
    for _ in range(30):
        limiter.check("member")
    with pytest.raises(TooManyRequestsError):
        limiter.check("member")
    limiter.check("other-member")
    monkeypatch.setattr("push_kids.media.preview_limit.monotonic", lambda: 161.0)
    limiter.check("member")
