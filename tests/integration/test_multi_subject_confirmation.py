"""A photo batch spanning subjects must produce one record per configured subject.

Before this behavior existed the confirmation flow could only create one record, which pushed
parents into inventing a merged subject such as "数学.语文、英语". Adding a subject that the family
never configured now needs an explicit parent answer.
"""

from __future__ import annotations

import json

from push_kids.persistence.models import LearningRecord, LearningSubmission, Subject
from push_kids.platform.time import utcnow
from sqlalchemy import select


def _subject(client, headers, child, name: str) -> dict:
    response = client.post(
        "/api/v1/subjects",
        headers=headers,
        json={"child_id": child["id"], "name": name, "kind": "learning"},
    )
    assert response.status_code == 201
    return response.json()


def _draft(client, app, child, headers, text: str) -> str:
    sid = client.post(
        "/api/v1/submissions",
        headers=headers,
        json={"child_id": child["id"], "occurred_at": utcnow().isoformat(), "input_text": text},
    ).json()["id"]
    app.state.worker.process_one()
    return sid


def _mixed_proposal(client, headers, sid: str) -> dict:
    proposal = client.get(f"/api/v1/submissions/{sid}", headers=headers).json()["proposal"]
    proposal["summary"] = "一次拍了数学和语文"
    proposal["subject_name"] = "数学、语文"
    proposal["knowledge_points"] = [
        {
            "name": "两位数加法",
            "category": "知识点",
            "review_method": "口头回顾",
            "estimated_minutes": 3,
            "subject_name": "数学",
        },
        {
            "name": "生字听写",
            "category": "知识点",
            "review_method": "口头回顾",
            "estimated_minutes": 3,
            "subject_name": "语文",
        },
    ]
    return proposal


def _store_proposal(app, sid: str, proposal: dict) -> None:
    """Simulate the model returning this draft, including a merged subject label."""
    with app.state.database.session_factory() as db:
        submission = db.get(LearningSubmission, sid)
        submission.proposal_json = json.dumps(proposal, ensure_ascii=False)
        submission.state = "pending_confirmation"
        db.commit()


def test_view_splits_a_mixed_draft_across_configured_subjects(client, app, child, family_headers):
    math = _subject(client, family_headers, child, "数学")
    chinese = _subject(client, family_headers, child, "语文")
    sid = _draft(client, app, child, family_headers, "数学加法和语文听写")
    proposal = _mixed_proposal(client, family_headers, sid)
    client.post(
        f"/api/v1/submissions/{sid}/confirm",
        headers=family_headers,
        json={
            "proposal": proposal,
            "groups": [
                {"subject_id": math["id"], "subject_name": "数学", "knowledge_indexes": [0]},
                {"subject_id": chinese["id"], "subject_name": "语文", "knowledge_indexes": [1]},
            ],
        },
    )
    with app.state.database.session_factory() as db:
        records = db.scalars(
            select(LearningRecord).where(LearningRecord.submission_id == sid)
        ).all()
        assert {record.subject_id for record in records} == {math["id"], chinese["id"]}
        names = db.scalars(select(Subject.name).where(Subject.child_id == child["id"])).all()
        # The merged label never becomes a subject.
        assert sorted(names) == ["数学", "语文"]


def test_pending_view_reports_the_split_and_asks_for_a_check(client, app, child, family_headers):
    math = _subject(client, family_headers, child, "数学")
    chinese = _subject(client, family_headers, child, "语文")
    sid = _draft(client, app, child, family_headers, "数学加法和语文听写")
    _store_proposal(app, sid, _mixed_proposal(client, family_headers, sid))
    view = client.get(f"/api/v1/submissions/{sid}", headers=family_headers).json()
    assert [
        (item["subject_name"], item["subject_id"], item["listed"], item["knowledge_indexes"])
        for item in view["subject_groups"]
    ] == [("数学", math["id"], True, [0]), ("语文", chinese["id"], True, [1])]
    assert view["subject_review_needed"] is True
    # Every point carries its routed subject so the client edits one field per point.
    assert [point["subject_name"] for point in view["proposal"]["knowledge_points"]] == [
        "数学",
        "语文",
    ]


def test_a_draft_naming_an_unconfigured_subject_is_marked_unlisted(
    client, app, child, family_headers
):
    _subject(client, family_headers, child, "数学")
    sid = _draft(client, app, child, family_headers, "科学课的浮力实验")
    proposal = _mixed_proposal(client, family_headers, sid)
    proposal["subject_name"] = "科学"
    proposal["knowledge_points"] = [proposal["knowledge_points"][0] | {"subject_name": "科学"}]
    _store_proposal(app, sid, proposal)
    view = client.get(f"/api/v1/submissions/{sid}", headers=family_headers).json()
    assert [
        (item["subject_name"], item["subject_id"], item["listed"])
        for item in view["subject_groups"]
    ] == [("科学", None, False)]
    assert view["subject_review_needed"] is True


def test_confirming_a_mixed_batch_creates_one_record_per_subject(
    client, app, child, family_headers
):
    _subject(client, family_headers, child, "数学")
    _subject(client, family_headers, child, "语文")
    sid = _draft(client, app, child, family_headers, "数学加法和语文听写")
    view = client.get(f"/api/v1/submissions/{sid}", headers=family_headers).json()
    assert view["subject_groups"], "a draft must always report which subjects it touches"
    proposal = _mixed_proposal(client, family_headers, sid)
    result = client.post(
        f"/api/v1/submissions/{sid}/confirm",
        headers=family_headers,
        json={
            "proposal": proposal,
            "groups": [
                {"subject_name": "数学", "summary": "数学：两位数加法", "knowledge_indexes": [0]},
                {"subject_name": "语文", "summary": "语文：生字听写", "knowledge_indexes": [1]},
            ],
        },
    )
    assert result.status_code == 200
    body = result.json()
    assert [item["subject_name"] for item in body["records"]] == ["数学", "语文"]
    assert body["record_id"] == body["records"][0]["record_id"]
    assert len(body["knowledge_item_ids"]) == 2
    detail = client.get(
        f"/api/v1/children/{child['id']}/history/{sid}", headers=family_headers
    ).json()
    assert [record["subject_name"] for record in detail["records"]] == ["数学", "语文"]
    assert [record["summary"] for record in detail["records"]] == [
        "数学：两位数加法",
        "语文：生字听写",
    ]
    assert [len(record["knowledge"]) for record in detail["records"]] == [1, 1]
    # The union keeps older readers and the review lookup working.
    assert len(detail["knowledge"]) == 2
    history = client.get(
        f"/api/v1/children/{child['id']}/history?view=confirmed", headers=family_headers
    ).json()
    # One row per subject record, each with its own stable row id.
    assert {item["subject_name"] for item in history["items"]} == {"数学", "语文"}
    assert len({item["id"] for item in history["items"]}) == 2
    assert {item["submission_id"] for item in history["items"]} == {sid}


def test_an_unconfigured_subject_needs_an_explicit_parent_answer(
    client, app, child, family_headers
):
    _subject(client, family_headers, child, "数学")
    sid = _draft(client, app, child, family_headers, "科学课的浮力实验")
    proposal = client.get(f"/api/v1/submissions/{sid}", headers=family_headers).json()["proposal"]
    proposal["subject_name"] = "科学"
    proposal["knowledge_points"] = [
        {
            "name": "浮力小实验",
            "category": "知识点",
            "review_method": "口头回顾",
            "estimated_minutes": 3,
        }
    ]
    asked = client.post(
        f"/api/v1/submissions/{sid}/confirm", headers=family_headers, json={"proposal": proposal}
    )
    assert asked.status_code == 409
    assert asked.json()["error"]["code"] == "consent_required"
    with app.state.database.session_factory() as db:
        names = db.scalars(select(Subject.name).where(Subject.child_id == child["id"])).all()
        assert list(names) == ["数学"], "a refused subject must not be created"
    added = client.post(
        f"/api/v1/submissions/{sid}/confirm",
        headers=family_headers,
        json={"proposal": proposal, "create_subject": True},
    )
    assert added.status_code == 200
    assert added.json()["records"][0]["subject_name"] == "科学"


def test_a_merged_subject_name_is_refused(client, app, child, family_headers):
    _subject(client, family_headers, child, "数学")
    _subject(client, family_headers, child, "语文")
    sid = _draft(client, app, child, family_headers, "数学加法和语文听写")
    proposal = _mixed_proposal(client, family_headers, sid)
    refused = client.post(
        f"/api/v1/submissions/{sid}/confirm",
        headers=family_headers,
        json={"proposal": proposal, "create_subject": True},
    )
    assert refused.status_code == 400
    assert "科目" in refused.json()["error"]["message"]
    with app.state.database.session_factory() as db:
        names = db.scalars(select(Subject.name).where(Subject.child_id == child["id"])).all()
        assert sorted(names) == ["数学", "语文"]


def test_an_alias_reuses_the_configured_subject(client, app, child, family_headers):
    english = _subject(client, family_headers, child, "英语")
    sid = _draft(client, app, child, family_headers, "英文单词练习")
    proposal = client.get(f"/api/v1/submissions/{sid}", headers=family_headers).json()["proposal"]
    proposal["subject_name"] = "英文"
    proposal["knowledge_points"] = [
        {
            "name": "颜色单词",
            "category": "知识点",
            "review_method": "口头回顾",
            "estimated_minutes": 3,
        }
    ]
    result = client.post(
        f"/api/v1/submissions/{sid}/confirm", headers=family_headers, json={"proposal": proposal}
    )
    assert result.status_code == 200
    assert result.json()["records"][0]["subject_id"] == english["id"]


def test_every_knowledge_point_must_be_grouped(client, app, child, family_headers):
    _subject(client, family_headers, child, "数学")
    _subject(client, family_headers, child, "语文")
    sid = _draft(client, app, child, family_headers, "数学加法和语文听写")
    proposal = _mixed_proposal(client, family_headers, sid)
    refused = client.post(
        f"/api/v1/submissions/{sid}/confirm",
        headers=family_headers,
        json={
            "proposal": proposal,
            "groups": [
                {"subject_name": "数学", "knowledge_indexes": [0]},
                {"subject_name": "语文", "knowledge_indexes": [0]},
            ],
        },
    )
    assert refused.status_code == 400
    with app.state.database.session_factory() as db:
        assert not db.scalars(
            select(LearningRecord).where(LearningRecord.submission_id == sid)
        ).all()
