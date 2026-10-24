"""Exercise public APIs, deterministic provider and actual confirmation saga."""

import json
from datetime import timedelta

import pytest
from push_kids.knowledge.learning_context import KnowledgeInputClock
from push_kids.learning_suggestions.models import RecordIntent, StudyTask
from push_kids.persistence.models import Child, KnowledgeItem, LearningRecord, ReviewItem, Subject
from push_kids.platform.time import local_date, utcnow
from sqlalchemy import func, select


@pytest.fixture
def suggestion_scope(app, client, child, family_headers):
    app.state.database.session_factory.configure(info={"learning_suggestions_enabled": True})
    with app.state.database.session_factory() as db:
        subject = Subject(
            family_id=family_headers["X-Family-ID"],
            child_id=child["id"],
            name="数学",
            kind="learning",
        )
        db.add(subject)
        db.flush()
        db.add(
            KnowledgeItem(
                family_id=subject.family_id,
                child_id=child["id"],
                subject_id=subject.id,
                name="十以内加法",
                normalized_name="十以内加法",
                category="知识点",
                estimated_minutes=3,
            )
        )
        db.add(
            KnowledgeInputClock(
                family_id=subject.family_id,
                child_id=child["id"],
                observed_since=local_date() - timedelta(days=5),
                last_new_confirmed_on=local_date() - timedelta(days=3),
            )
        )
        db.commit()
        sid = subject.id
    return f"/api/v1/children/{child['id']}/learning-suggestions", sid


def generate(client, app, root, headers):
    claim = client.post(
        root + "/automatic-prompt", headers=headers, json={"request_id": "prompt-first-001"}
    )
    assert claim.status_code == 200, claim.text
    assert claim.json()["can_auto_open"] is True
    assert app.state.suggestion_worker.process_one() is True
    current = client.get(root + "/current", headers=headers)
    assert current.status_code == 200, current.text
    assert current.json()["proposal"]
    return current.json()["proposal"]


def approve(client, root, headers, proposal):
    response = client.post(
        root + f"/{proposal['id']}/approve",
        headers=headers,
        json={"expected_version": proposal["version"]},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_suggestion_title_patch_boundaries_and_no_writes(
    app, client, family_headers, suggestion_scope
):
    from push_kids.learning_suggestions.models import Suggestion

    root, _ = suggestion_scope
    proposal = generate(client, app, root, family_headers)
    for title in ["题" * 21, "题" * 120, "活动\n步骤", "   "]:
        with app.state.database.session_factory() as db:
            row = db.get(Suggestion, proposal["id"])
            before = row.validated_content_json, row.version
        response = client.patch(
            root + f"/{proposal['id']}",
            headers=family_headers,
            json={
                "expected_version": proposal["version"],
                "title": title,
                "instructions": "保留具体操作",
                "estimated_minutes": 12,
            },
        )
        assert response.status_code == 422, response.text
        with app.state.database.session_factory() as db:
            row = db.get(Suggestion, proposal["id"])
            assert (row.validated_content_json, row.version) == before
            assert db.scalar(select(func.count()).select_from(StudyTask)) == 0
            assert db.scalar(select(func.count()).select_from(LearningRecord)) == 0
    response = client.patch(
        root + f"/{proposal['id']}",
        headers=family_headers,
        json={
            "expected_version": proposal["version"],
            "title": "  " + "𠀀" * 20 + "  ",
            "instructions": "保留具体操作",
            "estimated_minutes": None,
        },
    )
    assert response.status_code == 200, response.text
    assert response.json()["title"] == "𠀀" * 20


@pytest.mark.parametrize("action", ["edit", "record", "remove"])
def test_suggestion_title_legacy_read_and_parent_operations(
    action, app, client, child, family_headers, suggestion_scope
):
    from push_kids.learning_suggestions.models import Suggestion

    root, _ = suggestion_scope
    proposal = generate(client, app, root, family_headers)
    legacy_title = "题" * 120
    with app.state.database.session_factory() as db:
        row = db.get(Suggestion, proposal["id"])
        legacy = json.loads(row.validated_content_json)
        legacy["title"] = legacy_title
        row.validated_content_json = json.dumps(legacy, ensure_ascii=False)
        db.commit()
    proposal = client.get(root + "/current", headers=family_headers).json()["proposal"]
    assert proposal["title"] == legacy_title
    if action == "edit":
        response = client.patch(
            root + f"/{proposal['id']}",
            headers=family_headers,
            json={
                "expected_version": proposal["version"],
                "title": "用积木表示加法",
                "instructions": proposal["instructions"],
            },
        )
        assert response.status_code == 200 and response.json()["title"] == "用积木表示加法"
        return
    task = approve(client, root, family_headers, proposal)
    assert task["content"]["title"] == legacy_title
    assert (
        client.get(root + "/current", headers=family_headers).json()["task"]["content"]["title"]
        == legacy_title
    )
    if action == "remove":
        response = client.post(
            root + f"/tasks/{task['id']}/remove",
            headers={**family_headers, "Idempotency-Key": "legacy-remove-001"},
            json={"expected_version": task["version"]},
        )
        assert response.status_code == 202
    else:
        task["child_id"] = child["id"]
        intent, sid = actual_record(client, root, family_headers, task, mode="complete")
        response = client.post(
            root + f"/tasks/{task['id']}/records",
            headers=family_headers,
            json={"intent_id": intent["id"], "submission_id": sid},
        )
        assert response.status_code == 200 and response.json()["state"] == "recorded"
    with app.state.database.session_factory() as db:
        assert (
            json.loads(db.get(Suggestion, proposal["id"]).validated_content_json)["title"]
            == legacy_title
        )


def test_suggestion_title_invalid_provider_never_persists_and_retries_are_bounded(
    app, client, family_headers, suggestion_scope
):
    from push_kids.agent_processing.suggestion_provider import TestSuggestionProvider
    from push_kids.learning_suggestions.models import Suggestion, SuggestionJob

    root, _ = suggestion_scope
    current = client.get(root + "/current", headers=family_headers).json()
    job = client.post(
        root + "/generate",
        headers={**family_headers, "Idempotency-Key": "invalid-title-job-001"},
        json={"expected_version": current["version"]},
    ).json()

    class InvalidProvider:
        calls = 0

        def suggest(self, context):
            self.calls += 1
            return TestSuggestionProvider().suggest(context).model_copy(update={"title": "题" * 21})

    provider = InvalidProvider()
    app.state.suggestion_worker.provider = provider
    for attempt in range(1, 4):
        assert app.state.suggestion_worker.process_one()
        with app.state.database.session_factory() as db:
            row = db.get(SuggestionJob, job["id"])
            assert row.attempts == attempt
            assert row.state == ("failed" if attempt == 3 else "queued")
            assert row.safe_error_code == "generation_unavailable"
            for model in [Suggestion, StudyTask, LearningRecord]:
                assert db.scalar(select(func.count()).select_from(model)) == 0
            row.available_at = utcnow() - timedelta(seconds=1)
            db.commit()
    assert provider.calls == 3 and not app.state.suggestion_worker.process_one()


def actual_record(
    client,
    root,
    headers,
    task,
    *,
    mode="partial",
    text="比较两个加法算式",
    key="actual-first-001",
    occurred_at=None,
):
    response = client.post(
        root + f"/tasks/{task['id']}/record-intents",
        headers=headers,
        json={"expected_version": task["version"], "mode": mode, "request_id": key},
    )
    assert response.status_code == 201, response.text
    intent = response.json()
    submission = client.post(
        "/api/v1/submissions",
        headers={**headers, "Idempotency-Key": intent["submission_idempotency_key"]},
        json={
            "child_id": task["child_id"],
            "occurred_at": (occurred_at or utcnow() - timedelta(hours=1)).isoformat(),
            "input_text": text,
        },
    )
    assert submission.status_code == 202, submission.text
    sid = submission.json()["id"]
    confirmation = client.post(
        f"/api/v1/submissions/{sid}/confirm",
        headers=headers,
        json={
            "manual_entry": True,
            "subject_id": task["content"]["subject_id"],
            "proposal": {
                "summary": text,
                "subject_name": "数学",
                "source": "人工录入",
                "knowledge_points": [
                    {
                        "name": text,
                        "category": "知识点",
                        "review_method": "口头回顾",
                        "estimated_minutes": 3,
                    }
                ],
                "todo_matches": [],
            },
        },
    )
    assert confirmation.status_code == 200, confirmation.text
    return intent, sid


def test_shared_prompt_approval_zero_facts_partial_and_complete(
    app, client, child, family_headers, suggestion_scope
):
    root, _ = suggestion_scope
    proposal = generate(client, app, root, family_headers)
    repeat = client.post(
        root + "/automatic-prompt", headers=family_headers, json={"request_id": "prompt-device-002"}
    )
    assert repeat.json()["can_auto_open"] is False
    task = approve(client, root, family_headers, proposal)
    task["child_id"] = child["id"]
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(LearningRecord)) == 0
        assert db.scalar(select(func.count()).select_from(ReviewItem)) == 0
        assert db.scalar(select(func.count()).select_from(KnowledgeItem)) == 1
    intent, sid = actual_record(client, root, family_headers, task)
    linked = client.post(
        root + f"/tasks/{task['id']}/records",
        headers=family_headers,
        json={"intent_id": intent["id"], "submission_id": sid},
    )
    assert linked.status_code == 200, linked.text
    assert linked.json()["state"] == "planned"
    current = client.get(root + "/current", headers=family_headers).json()
    assert current["task"]["id"] == task["id"] and current["task"]["last_partial_at"]
    current["task"]["child_id"] = child["id"]
    intent2, sid2 = actual_record(
        client,
        root,
        family_headers,
        current["task"],
        mode="complete",
        text="用积木演示加法",
        key="actual-second-002",
    )
    # Simulate confirmation success followed by a lost association request.
    app.state.suggestion_worker.maintenance()
    with app.state.database.session_factory() as db:
        assert db.get(RecordIntent, intent2["id"]).state == "linked"
        assert db.get(StudyTask, task["id"]).state == "recorded"
        assert db.scalar(select(func.count()).select_from(LearningRecord)) == 2
    replay = client.post(
        root + f"/tasks/{task['id']}/records",
        headers=family_headers,
        json={"intent_id": intent2["id"], "submission_id": sid2},
    )
    assert replay.status_code == 200
    assert client.get(root + "/current", headers=family_headers).json()["task"] is None
    assert (
        len(
            client.get(root + f"/tasks/{task['id']}/records", headers=family_headers).json()[
                "items"
            ]
        )
        == 2
    )


def test_context_change_invalidates_proposal_scope_and_delete_reapproves(
    app, client, child, family_headers, suggestion_scope
):
    root, _ = suggestion_scope
    proposal = generate(client, app, root, family_headers)
    assert client.get(root + "/current", headers={"X-Family-ID": "other-family"}).status_code == 404
    with app.state.database.session_factory() as db:
        db.get(Child, child["id"]).grade = "小学三年级"
        db.commit()
    denied = client.post(
        root + f"/{proposal['id']}/approve", headers=family_headers, json={"expected_version": 0}
    )
    assert denied.status_code == 409
    current = client.get(root + "/current", headers=family_headers).json()
    generated = client.post(
        root + "/generate",
        headers={**family_headers, "Idempotency-Key": "regenerate-001"},
        json={"expected_version": current["version"]},
    )
    assert generated.status_code == 202, generated.text
    app.state.suggestion_worker.process_one()
    proposal = client.get(root + "/current", headers=family_headers).json()["proposal"]
    task = approve(client, root, family_headers, proposal)
    removed = client.post(
        root + f"/tasks/{task['id']}/remove",
        headers={**family_headers, "Idempotency-Key": "remove-first-001"},
        json={"expected_version": task["version"]},
    )
    assert removed.status_code == 202, removed.text
    assert removed.json()["removed"] is True
    app.state.suggestion_worker.process_one()
    current = client.get(root + "/current", headers=family_headers).json()
    assert current["task"] is None
    assert current["proposal"]["title"] != proposal["title"]
    assert current["proposal"]["status"] == "proposed"


def test_defer_reuses_same_proposal_next_day_and_ack_never_releases(
    app, client, child, family_headers, suggestion_scope, monkeypatch
):
    from push_kids.learning_suggestions import queries, service

    root, _ = suggestion_scope
    proposal = generate(client, app, root, family_headers)
    response = client.post(
        root + f"/{proposal['id']}/defer",
        headers=family_headers,
        json={"expected_version": proposal["version"]},
    )
    assert response.status_code == 200
    for suffix, body in [
        (
            "/prompt-displayed",
            {"prompt_on": local_date().isoformat(), "request_id": "lost-ack-001"},
        ),
        ("/automatic-prompt", {"request_id": "another-device-001"}),
    ]:
        result = client.post(root + suffix, headers=family_headers, json=body)
        assert result.status_code == 200 and result.json()["can_auto_open"] is False
    tomorrow = local_date() + timedelta(days=1)
    monkeypatch.setattr(service, "local_date", lambda: tomorrow)
    monkeypatch.setattr(queries, "local_date", lambda: tomorrow)
    reused = client.post(
        root + "/automatic-prompt",
        headers=family_headers,
        json={"request_id": "next-day-prompt-001"},
    ).json()
    assert reused["can_auto_open"] and reused["current"]["proposal"]["id"] == proposal["id"]


def test_expiry_and_generation_input_race_cancel_before_provider(
    app, client, child, family_headers, suggestion_scope
):
    from push_kids.learning_suggestions.models import Suggestion, SuggestionJob

    root, _ = suggestion_scope
    queued = client.post(
        root + "/automatic-prompt",
        headers=family_headers,
        json={"request_id": "race-job-first-001"},
    ).json()["current"]["job"]
    with app.state.database.session_factory() as db:
        db.get(
            KnowledgeInputClock, (family_headers["X-Family-ID"], child["id"])
        ).input_revision += 1
        db.commit()
    original = app.state.suggestion_worker.provider

    class ForbiddenProvider:
        def suggest(self, context):
            pytest.fail("stale job must be cancelled before a provider call")

    app.state.suggestion_worker.provider = ForbiddenProvider()
    assert app.state.suggestion_worker.process_one()
    app.state.suggestion_worker.provider = original
    with app.state.database.session_factory() as db:
        assert db.get(SuggestionJob, queued["id"]).state == "cancelled"
    current = client.get(root + "/current", headers=family_headers).json()
    assert (
        client.post(
            root + "/generate",
            headers={**family_headers, "Idempotency-Key": "after-race-001"},
            json={"expected_version": current["version"]},
        ).status_code
        == 202
    )
    app.state.suggestion_worker.process_one()
    proposal = client.get(root + "/current", headers=family_headers).json()["proposal"]
    with app.state.database.session_factory() as db:
        db.get(Suggestion, proposal["id"]).expires_at = utcnow() - timedelta(seconds=1)
        db.commit()
    assert (
        client.post(
            root + f"/{proposal['id']}/approve",
            headers=family_headers,
            json={"expected_version": proposal["version"]},
        ).status_code
        == 409
    )


def test_disabled_switch_preserves_actual_records_and_late_removal_audit(
    app, client, child, family_headers, suggestion_scope
):
    from push_kids.learning_suggestions.models import StudyTaskRecord, SuggestionState
    from push_kids.learning_suggestions.service import purge_data

    root, _ = suggestion_scope
    task = approve(client, root, family_headers, generate(client, app, root, family_headers))
    task["child_id"] = child["id"]
    intent, sid = actual_record(client, root, family_headers, task, mode="complete")
    app.state.database.session_factory.configure(info={"learning_suggestions_enabled": False})
    assert client.get(root + "/current", headers=family_headers).json()["task"]["id"] == task["id"]
    removed = client.post(
        root + f"/tasks/{task['id']}/remove",
        headers={**family_headers, "Idempotency-Key": "disabled-remove-001"},
        json={"expected_version": task["version"]},
    )
    assert removed.status_code == 202 and removed.json()["removed"]
    linked = client.post(
        root + f"/tasks/{task['id']}/records",
        headers=family_headers,
        json={"intent_id": intent["id"], "submission_id": sid},
    )
    assert linked.status_code == 200 and linked.json()["state"] == "removed"
    with app.state.database.session_factory() as db:
        assert db.scalar(select(func.count()).select_from(StudyTaskRecord)) == 1
        purge_data(db, family_headers["X-Family-ID"], child["id"])
        db.commit()
        assert db.scalar(select(func.count()).select_from(SuggestionState)) == 0
        assert db.scalar(select(func.count()).select_from(RecordIntent)) == 0
        assert db.scalar(select(func.count()).select_from(LearningRecord)) == 1


def test_confirmation_clock_repeat_backfill_delete_and_rollback(
    app, client, child, family_headers, suggestion_scope
):
    from push_kids.knowledge.learning_context import invalidate_input, record_confirmation

    root, _ = suggestion_scope
    task = approve(client, root, family_headers, generate(client, app, root, family_headers))
    task["child_id"] = child["id"]
    actual_record(client, root, family_headers, task, text="十以内加法")
    key = (family_headers["X-Family-ID"], child["id"])
    with app.state.database.session_factory() as db:
        old = local_date() - timedelta(days=3)
        assert db.get(KnowledgeInputClock, key).last_new_confirmed_on == old
        record_confirmation(db, *key, new_knowledge=True)
        db.flush()
        db.rollback()
        assert db.get(KnowledgeInputClock, key).last_new_confirmed_on == old
    # Historical occurred_at still creates first-new knowledge on confirmation day.
    actual_record(
        client,
        root,
        family_headers,
        task,
        text="一项首次确认的新知识",
        key="historical-new-001",
        occurred_at=utcnow() - timedelta(days=90),
    )
    with app.state.database.session_factory() as db:
        clock = db.get(KnowledgeInputClock, key)
        assert clock.last_new_confirmed_on == local_date()
        revision = clock.input_revision
        invalidate_input(db, *key)
        db.commit()
        assert clock.last_new_confirmed_on == local_date() and clock.input_revision > revision


def test_new_drafts_do_not_starve_confirmed_record_recovery(
    app, client, child, family_headers, suggestion_scope
):
    from push_kids.learning_suggestions.models import SuggestionJob

    root, _ = suggestion_scope
    proposal = generate(client, app, root, family_headers)
    task = approve(client, root, family_headers, proposal)
    task["child_id"] = child["id"]
    with app.state.database.session_factory() as db:
        for i in range(55):
            db.add(
                RecordIntent(
                    family_id=family_headers["X-Family-ID"],
                    child_id=child["id"],
                    task_id=task["id"],
                    task_version=task["version"],
                    mode="partial",
                    created_by="parent",
                    request_id=f"unconfirmed-{i:03}",
                    created_at=utcnow() - timedelta(days=1),
                    recovery_after=utcnow() - timedelta(minutes=1),
                )
            )
        db.commit()
    intent, _ = actual_record(client, root, family_headers, task, mode="complete")
    app.state.suggestion_worker.maintenance()
    app.state.suggestion_worker.maintenance()
    with app.state.database.session_factory() as db:
        assert db.get(RecordIntent, intent["id"]).state == "linked"
        assert db.get(StudyTask, task["id"]).state == "recorded"
        assert db.scalar(select(func.count()).select_from(SuggestionJob)) == 1


@pytest.mark.parametrize("command", ["automatic", "manual", "remove"])
def test_suggestion_command_sql_budget(
    app, client, child, family_headers, suggestion_scope, command
):
    from push_kids.learning_suggestions.service import automatic_prompt, remove_task
    from push_kids.learning_suggestions.service import generate as generate_command
    from sqlalchemy import event

    task = None
    if command == "remove":
        root, _ = suggestion_scope
        task = approve(client, root, family_headers, generate(client, app, root, family_headers))
    captured = []

    def capture(_conn, _cursor, sql, _params, _context, _many):
        captured.append(sql)

    engine = app.state.database.engine
    event.listen(engine, "before_cursor_execute", capture)
    try:
        with app.state.database.session_factory() as db:
            if command == "automatic":
                result = automatic_prompt(
                    db, family_headers["X-Family-ID"], child["id"], "parent", "budget-prompt-001"
                )
                assert result["can_auto_open"] and result["current"]["job"]
            elif command == "manual":
                result = generate_command(
                    db, family_headers["X-Family-ID"], child["id"], 0, "budget-manual-001"
                )
                assert result["state"] == "queued"
            else:
                result = remove_task(
                    db,
                    family_headers["X-Family-ID"],
                    child["id"],
                    task["id"],
                    task["version"],
                    "budget-remove-001",
                )
                assert result["removed"] and result["job"]
    finally:
        event.remove(engine, "before_cursor_execute", capture)
    assert len(captured) <= 15, [(sql.split()[0], sql.split("\n")[0]) for sql in captured]


def test_provider_retries_quota_and_idempotent_manual_replay(
    app, client, child, family_headers, suggestion_scope
):
    from push_kids.learning_suggestions.models import SuggestionJob

    root, _ = suggestion_scope
    current = client.get(root + "/current", headers=family_headers).json()
    headers = {**family_headers, "Idempotency-Key": "retry-budget-001"}
    body = {"expected_version": current["version"]}
    queued = client.post(root + "/generate", headers=headers, json=body)
    assert queued.status_code == 202
    jid = queued.json()["id"]

    class FailingProvider:
        calls = 0

        def suggest(self, _context):
            self.calls += 1
            raise RuntimeError("provider-private-payload-must-not-escape")

    provider = FailingProvider()
    app.state.suggestion_worker.provider = provider
    for attempt in range(1, 4):
        assert app.state.suggestion_worker.process_one()
        with app.state.database.session_factory() as db:
            job = db.get(SuggestionJob, jid)
            assert job.attempts == attempt
            assert job.state == ("failed" if attempt == 3 else "queued")
            assert job.safe_error_code == "generation_unavailable"
            assert job.lease_token is None and job.lease_until is None
            if attempt < 3:
                assert job.available_at > utcnow()
                job.available_at = utcnow() - timedelta(seconds=1)
                db.commit()
    assert provider.calls == 3 and not app.state.suggestion_worker.process_one()
    replay = client.post(root + "/generate", headers=headers, json=body)
    assert replay.status_code == 202 and replay.json()["id"] == jid
    current = client.get(root + "/current", headers=family_headers).json()
    denied = client.post(
        root + "/generate",
        headers={**family_headers, "Idempotency-Key": "over-quota-002"},
        json={"expected_version": current["version"]},
    )
    assert denied.status_code == 429 and provider.calls == 3


def test_real_member_role_downgrade_and_removal_block_mutations(
    app, client, child, family_headers, suggestion_scope
):
    import hashlib

    from push_kids.persistence.models import Family, FamilyMember, WeChatActorBinding

    root, _ = suggestion_scope
    proposal = generate(client, app, root, family_headers)
    with app.state.database.session_factory() as db:
        db.add(Family(id=family_headers["X-Family-ID"], display_name="合成测试家庭"))
        db.flush()
        binding = WeChatActorBinding(
            app_id="local-debug",
            subject_hmac=hashlib.sha256(b"local:v1:suggestion-viewer").hexdigest(),
            family_id=family_headers["X-Family-ID"],
        )
        db.add(binding)
        db.flush()
        member = FamilyMember(
            family_id=binding.family_id,
            actor_binding_id=binding.id,
            active_actor_binding_id=binding.id,
            role="editor",
            relationship_label="家长",
        )
        db.add(member)
        db.commit()
        mid = member.id
    headers = {"X-Debug-Actor": "suggestion-viewer"}
    task = approve(client, root, headers, proposal)
    with app.state.database.session_factory() as db:
        db.get(FamilyMember, mid).role = "viewer"
        db.commit()
    assert client.get(root + "/current", headers=headers).json()["task"]["id"] == task["id"]
    for suffix, body in [
        ("/automatic-prompt", {"request_id": "viewer-prompt-001"}),
        (
            f"/tasks/{task['id']}/record-intents",
            {
                "expected_version": task["version"],
                "mode": "complete",
                "request_id": "viewer-record-001",
            },
        ),
        (f"/tasks/{task['id']}/remove", {"expected_version": task["version"]}),
    ]:
        response = client.post(
            root + suffix, headers={**headers, "Idempotency-Key": "viewer-command-001"}, json=body
        )
        assert response.status_code == 403, response.text
    with app.state.database.session_factory() as db:
        db.get(FamilyMember, mid).status = "removed"
        db.commit()
    assert client.get(root + "/current", headers=headers).status_code == 403
