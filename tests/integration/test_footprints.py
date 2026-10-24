"""Synthetic pixels only: parent confirmation, lifecycle and tenant boundaries."""

from datetime import datetime, timedelta
from io import BytesIO

import pytest
from PIL import Image
from push_kids.footprints.models import FootprintPhoto
from push_kids.platform.time import utcnow

ROOT = "/api/v1/footprints"


def image_bytes(with_date=True):
    stream = BytesIO()
    exif = Image.Exif()
    if with_date:
        exif[36867] = "2024:02:03 14:05:06"
        exif[36881] = "+08:00"
    Image.new("RGB", (400, 300), "green").save(stream, "JPEG", exif=exif)
    return stream.getvalue()


def create_batch(client, headers, child_id, count=1, key="batch"):
    response = client.post(
        ROOT + "/imports",
        headers={**headers, "Idempotency-Key": key},
        json={"child_id": child_id, "count": count, "consented": True},
    )
    assert response.status_code == 201, response.text
    return response.json()


def upload(client, headers, child_id, photo_id, with_date=True):
    response = client.post(
        f"{ROOT}/photos/{photo_id}/upload?child_id={child_id}",
        headers=headers,
        files={"file": ("synthetic.jpg", image_bytes(with_date), "image/jpeg")},
    )
    assert response.status_code == 200, response.text
    return response.json()


def get_photo(client, headers, child_id, photo_id):
    response = client.get(f"{ROOT}/photos/{photo_id}?child_id={child_id}", headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


def patch(client, headers, child_id, photo, **values):
    response = client.patch(
        f"{ROOT}/photos/{photo['id']}?child_id={child_id}",
        headers=headers,
        json={"version": photo["version"], **values},
    )
    assert response.status_code == 200, response.text
    return response.json()


def confirm(client, headers, child_id, batch_id, photos):
    return client.post(
        f"{ROOT}/imports/{batch_id}/confirm?child_id={child_id}",
        headers=headers,
        json={
            "photos": [{"id": p["id"], "version": p["version"]} for p in photos],
            "confirm_actual_visit": True,
        },
    )


def test_photo_exif_confirmation_album_and_private_media(client, app, child, family_headers):
    cid, headers = child["id"], family_headers
    batch = create_batch(client, headers, cid)
    initial = upload(client, headers, cid, batch["photos"][0]["id"])
    assert datetime.fromisoformat(initial["draft_expires_at"]) - datetime.fromisoformat(
        initial["received_at"]
    ) == timedelta(hours=168)
    assert client.get(f"{ROOT}/summary?child_id={cid}", headers=headers).json()["photos"] == 0
    assert app.state.footprint_worker.process_one()
    photo = get_photo(client, headers, cid, initial["id"])
    assert photo["local_date"] == "2024-02-03"
    assert photo["occurred_at"] == "2024-02-03T06:05:06Z"
    assert photo["time_source"] == "exif" and photo["has_display"]
    assert photo["latitude"] is None and not photo["candidates"]
    endpoint = f"{ROOT}/photos/{photo['id']}/preview?child_id={cid}"
    preview = client.get(endpoint, headers=headers)
    assert preview.headers["cache-control"] == "no-store"
    content = client.get("/api/v1" + preview.json()["download_path"], headers=headers)
    assert content.status_code == 200
    with Image.open(BytesIO(content.content)) as display:
        assert display.size == (400, 300)
        assert not display.getexif()
    assert client.get(endpoint, headers={"X-Family-ID": "other"}).status_code == 404
    first = confirm(client, headers, cid, batch["id"], [photo])
    assert first.status_code == 200, first.text
    assert confirm(client, headers, cid, batch["id"], [photo]).status_code == 200
    summary = client.get(f"{ROOT}/summary?child_id={cid}", headers=headers).json()
    assert (summary["photos"], summary["visit_days"], summary["unlocated_photos"]) == (1, 1, 1)
    assert not client.get(f"{ROOT}/map?child_id={cid}", headers=headers).json()["items"]
    assert len(client.get(f"{ROOT}/visits?child_id={cid}", headers=headers).json()["items"]) == 1


def test_unknown_date_never_falls_back_to_upload_time(client, app, child, family_headers):
    cid = child["id"]
    batch = create_batch(client, family_headers, cid)
    p = upload(client, family_headers, cid, batch["photos"][0]["id"], with_date=False)
    app.state.footprint_worker.process_one()
    p = get_photo(client, family_headers, cid, p["id"])
    assert p["local_date"] is None and p["occurred_at"] is None
    assert confirm(client, family_headers, cid, batch["id"], [p]).status_code == 409
    p = patch(client, family_headers, cid, p, local_date="2020-03-01")
    assert p["occurred_at"] is None
    assert confirm(client, family_headers, cid, batch["id"], [p]).status_code == 200


def test_upload_replay_rejects_different_bytes(client, child, family_headers):
    cid, h = child["id"], family_headers
    batch = create_batch(client, h, cid)
    photo_id = batch["photos"][0]["id"]
    first = upload(client, h, cid, photo_id)
    assert upload(client, h, cid, photo_id)["draft_expires_at"] == first["draft_expires_at"]
    response = client.post(
        f"{ROOT}/photos/{photo_id}/upload?child_id={cid}",
        headers=h,
        files={"file": ("other.jpg", image_bytes(False), "image/jpeg")},
    )
    assert response.status_code == 409


def test_child_deletion_purges_footprint_media_and_rows_only_in_scope(client, app):
    from pathlib import Path

    from sqlalchemy import func, select

    from tests.integration.test_data_deletion import _actor, _child, _family

    actor = "footprint-delete-parent"
    _family(client, actor)
    target, sibling = _child(client, actor, "合成甲"), _child(client, actor, "合成乙")
    h = _actor(actor)
    ids, refs = {}, {}
    for current in (target, sibling):
        cid = current["id"]
        batch = create_batch(client, h, cid, key=cid)
        photo = upload(client, h, cid, batch["photos"][0]["id"])
        assert app.state.footprint_worker.process_one()
        photo = get_photo(client, h, cid, photo["id"])
        assert confirm(client, h, cid, batch["id"], [photo]).status_code == 200
        ids[cid] = photo["id"]
        with app.state.database.session_factory() as db:
            row = db.get(FootprintPhoto, photo["id"])
            refs[cid] = [Path(row.original_ref), Path(row.display_ref), Path(row.thumbnail_ref)]
    cid = target["id"]
    response = client.post(
        f"/api/v1/children/{cid}/deletion-requests",
        headers={**h, "Idempotency-Key": "delete-footprints"},
        json={"confirmation_name": target["name"]},
    )
    assert response.status_code == 202
    assert client.get(f"{ROOT}/photos/{ids[cid]}?child_id={cid}", headers=h).status_code == 409
    assert app.state.deletion_worker.process_one()
    assert not any(path.exists() for path in refs[cid])
    assert all(path.exists() for path in refs[sibling["id"]])
    with app.state.database.session_factory() as db:
        assert (
            db.scalar(
                select(func.count())
                .select_from(FootprintPhoto)
                .where(FootprintPhoto.child_id == cid)
            )
            == 0
        )
    assert get_photo(client, h, sibling["id"], ids[sibling["id"]])["state"] == "confirmed"


def test_visit_days_corrections_deletions_recompute_all_views(client, app, child, family_headers):
    cid, h = child["id"], family_headers
    batch = create_batch(client, h, cid, count=2)
    photos = []
    for item in batch["photos"]:
        upload(client, h, cid, item["id"])
        app.state.footprint_worker.process_one()
        p = get_photo(client, h, cid, item["id"])
        photos.append(
            patch(
                client,
                h,
                cid,
                p,
                place_name="公园",
                city="北京",
                country="中国",
                latitude=39.9,
                longitude=116.4,
                coordinate_system="gcj02",
                precision="poi",
            )
        )
    result = confirm(client, h, cid, batch["id"], photos)
    assert result.status_code == 200, result.text
    photos = result.json()["confirmed"]
    summary = client.get(f"{ROOT}/summary?child_id={cid}", headers=h).json()
    assert (
        summary["photos"],
        summary["visit_days"],
        summary["places"],
        summary["cities"],
        summary["countries"],
    ) == (2, 1, 1, 1, 1)
    second = patch(client, h, cid, photos[1], local_date="2024-02-04")
    points = client.get(f"{ROOT}/map?child_id={cid}", headers=h).json()["items"]
    assert len(points) == 1 and points[0]["place_key"] and points[0]["visit_days"] == 2
    playback = client.get(f"{ROOT}/playback?child_id={cid}", headers=h).json()
    assert [p["local_date"] for p in playback["items"]] == ["2024-02-03", "2024-02-04"]
    endpoint = f"{ROOT}/photos/{second['id']}?child_id={cid}&version={second['version']}"
    assert client.delete(endpoint, headers=h).status_code == 204
    assert client.delete(endpoint, headers=h).status_code == 204
    assert client.get(f"{ROOT}/photos/{second['id']}?child_id={cid}", headers=h).status_code == 410
    assert client.get(f"{ROOT}/summary?child_id={cid}", headers=h).json()["photos"] == 1
    assert len(client.get(f"{ROOT}/playback?child_id={cid}", headers=h).json()["items"]) == 1
    assert (
        client.get(
            f"{ROOT}/playback?child_id={cid}&revision={playback['revision']}", headers=h
        ).status_code
        == 409
    )


def test_fixed_expiry_denies_late_confirmation_and_clears_metadata(
    client, app, child, family_headers
):
    cid, h = child["id"], family_headers
    batch = create_batch(client, h, cid)
    initial = upload(client, h, cid, batch["photos"][0]["id"])
    app.state.footprint_worker.process_one()
    p = get_photo(client, h, cid, initial["id"])
    updated = patch(client, h, cid, p, place_name="测试地点")
    assert updated["draft_expires_at"] == initial["draft_expires_at"]
    with app.state.database.session_factory() as db:
        row = db.get(FootprintPhoto, p["id"])
        row.draft_expires_at = utcnow() - timedelta(seconds=1)
        display = row.display_ref
        db.commit()
    assert confirm(client, h, cid, batch["id"], [updated]).status_code == 410
    data = client.get(f"{ROOT}/imports/{batch['id']}?child_id={cid}", headers=h).json()
    assert data["photos"][0]["state"] == "expired" and "place_name" not in data["photos"][0]
    assert app.state.footprint_worker.cleanup_one()
    with app.state.database.session_factory() as db:
        row = db.get(FootprintPhoto, p["id"])
        assert row.state == "expired" and row.original_ref is None and row.local_date is None
        assert row.place_name is None and row.sha256 is None
    with app.state.media_store.materialize(display) as path:
        assert not path.exists()


def test_confirmed_media_survives_original_cleanup_and_day_seven(
    client, app, child, family_headers
):
    cid, h = child["id"], family_headers
    batch = create_batch(client, h, cid)
    p = upload(client, h, cid, batch["photos"][0]["id"])
    app.state.footprint_worker.process_one()
    p = get_photo(client, h, cid, p["id"])
    assert confirm(client, h, cid, batch["id"], [p]).status_code == 200
    with app.state.database.session_factory() as db:
        row = db.get(FootprintPhoto, p["id"])
        assert row.original_delete_after is not None
        row.original_delete_after = utcnow() - timedelta(seconds=1)
        row.draft_expires_at = utcnow() - timedelta(days=1)
        db.commit()
    assert app.state.footprint_worker.cleanup_one()
    with app.state.database.session_factory() as db:
        row = db.get(FootprintPhoto, p["id"])
        assert row.original_ref is None and row.derived_ready and row.state == "confirmed"
    assert get_photo(client, h, cid, p["id"])["has_display"]


def test_manual_and_import_idempotency_and_validation(client, child, family_headers):
    cid, h = child["id"], family_headers
    body = {"child_id": cid, "local_date": "2024-01-01", "place_name": "上海"}
    headers = {**h, "Idempotency-Key": "manual"}
    response = client.post(ROOT + "/manual", headers=headers, json=body)
    assert response.status_code == 201, response.text
    assert (
        client.post(ROOT + "/manual", headers=headers, json=body).json()["id"]
        == response.json()["id"]
    )
    assert (
        client.post(
            ROOT + "/manual", headers=headers, json={**body, "place_name": "北京"}
        ).status_code
        == 409
    )
    batch = response.json()
    assert confirm(client, h, cid, batch["id"], batch["photos"]).status_code == 200
    summary = client.get(f"{ROOT}/summary?child_id={cid}", headers=h).json()
    assert summary["photos"] == 0 and summary["visit_days"] == 1
    assert (
        client.post(
            ROOT + "/imports",
            headers=headers,
            json={"child_id": cid, "count": 21, "consented": True},
        ).status_code
        == 422
    )
    assert client.get(f"{ROOT}/map?child_id={cid}&west=100", headers=h).status_code == 400
    assert (
        client.get(
            f"{ROOT}/visits?child_id={cid}&start=2025-01-01&end=2024-01-01", headers=h
        ).status_code
        == 400
    )


def test_archived_child_old_slots_continue_but_new_import_denied(
    client, app, child, family_headers
):
    cid, h = child["id"], family_headers
    batch = create_batch(client, h, cid)
    assert client.post(f"/api/v1/children/{cid}/archive", headers=h).status_code == 200
    response = client.post(
        ROOT + "/imports",
        headers={**h, "Idempotency-Key": "new"},
        json={"child_id": cid, "count": 1, "consented": True},
    )
    assert response.status_code == 409
    p = upload(client, h, cid, batch["photos"][0]["id"])
    app.state.footprint_worker.process_one()
    p = get_photo(client, h, cid, p["id"])
    assert confirm(client, h, cid, batch["id"], [p]).status_code == 200


def test_ai_opt_in_is_only_candidate_never_formal_and_manual_location_skips(
    client, app, child, family_headers
):
    from push_kids.agent_processing.footprint_provider import LocationHint, LocationHints

    class Recording:
        calls = 0

        def locate(self, path):
            self.calls += 1
            with Image.open(path) as image:
                assert not image.getexif()
            return LocationHints(
                candidates=[LocationHint(name="候选公园", city="北京", country="中国")]
            )

    provider = Recording()
    app.state.footprint_worker.provider = provider
    cid, h = child["id"], family_headers
    client.patch(ROOT + "/preferences", headers=h, json={"ai_enabled": True, "consented": True})
    batch = create_batch(client, h, cid, count=2)
    for photo in batch["photos"]:
        upload(client, h, cid, photo["id"])
    p = get_photo(client, h, cid, batch["photos"][0]["id"])
    patch(client, h, cid, p, place_name="家长已填地点")
    assert app.state.footprint_worker.process_one()
    assert app.state.footprint_worker.process_one()
    assert provider.calls == 1
    p = get_photo(client, h, cid, batch["photos"][1]["id"])
    assert p["place_name"] is None and p["candidates"][0]["place_name"] == "候选公园"
    assert client.get(f"{ROOT}/summary?child_id={cid}", headers=h).json()["photos"] == 0


@pytest.mark.parametrize("value", [float("inf"), float("nan")])
def test_place_rejects_nonfinite_numbers(value):
    from push_kids.footprints.schemas import Place
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        Place(latitude=value, longitude=0, coordinate_system="gcj02")


def test_same_day_playback_uses_time_and_parent_order(client, app, child, family_headers):
    cid, h = child["id"], family_headers
    batch = create_batch(client, h, cid, count=3)
    photos = []
    for index, hour in enumerate(["14:00", "10:00", "12:00"]):
        photo = batch["photos"][index]
        upload(client, h, cid, photo["id"])
        app.state.footprint_worker.process_one()
        photo = get_photo(client, h, cid, photo["id"])
        photos.append(
            patch(
                client,
                h,
                cid,
                photo,
                local_time=hour,
                place_name=f"地点{hour}",
                latitude=39.9 + index,
                longitude=116.4,
                coordinate_system="gcj02",
            )
        )
    assert confirm(client, h, cid, batch["id"], photos).status_code == 200
    result = client.get(f"{ROOT}/playback?child_id={cid}", headers=h).json()
    assert [p["local_time"] for p in result["items"]] == ["10:00:00", "12:00:00", "14:00:00"]
    last = result["items"][-1]
    response = client.patch(
        f"{ROOT}/visits/{last['id']}/order?child_id={cid}",
        headers=h,
        json={"revision": result["revision"], "day_order": -1},
    )
    assert response.status_code == 200, response.text
    reordered = client.get(f"{ROOT}/playback?child_id={cid}", headers=h).json()
    assert reordered["items"][0]["id"] == last["id"]


def test_cleanup_failed_is_visible_and_recoverable(client, app, child, family_headers, monkeypatch):
    cid, h = child["id"], family_headers
    batch = create_batch(client, h, cid)
    photo = upload(client, h, cid, batch["photos"][0]["id"])
    store = app.state.media_store
    original_delete = store.delete

    def fail(_ref):
        raise OSError("synthetic transient storage outage")

    monkeypatch.setattr(store, "delete", fail)
    for _ in range(3):
        with app.state.database.session_factory() as db:
            row = db.get(FootprintPhoto, photo["id"])
            row.draft_expires_at = utcnow() - timedelta(seconds=1)
            if row.cleanup_state == "pending":
                row.cleanup_after = utcnow() - timedelta(seconds=1)
            db.commit()
        assert app.state.footprint_worker.cleanup_one()
    failures = client.get(f"{ROOT}/cleanup?child_id={cid}", headers=h).json()
    assert failures["total"] == 1 and failures["items"][0]["attempts"] == 3
    assert not app.state.footprint_worker.cleanup_one()
    monkeypatch.setattr(store, "delete", original_delete)
    response = client.post(
        f"{ROOT}/photos/{photo['id']}/cleanup-retry?child_id={cid}&version={failures['items'][0]['version']}",
        headers=h,
    )
    assert response.status_code == 200, response.text
    assert app.state.footprint_worker.cleanup_one()
    assert client.get(f"{ROOT}/cleanup?child_id={cid}", headers=h).json()["total"] == 0
    with app.state.database.session_factory() as db:
        row = db.get(FootprintPhoto, photo["id"])
        assert row.original_ref is None and row.cleanup_state == "succeeded"


def test_frozen_child_does_not_starve_another_family(client, app, child, family_headers):
    from push_kids.persistence.models import Child

    first = create_batch(client, family_headers, child["id"])
    upload(client, family_headers, child["id"], first["photos"][0]["id"])
    with app.state.database.session_factory() as db:
        db.get(Child, child["id"]).deleting = True
        db.commit()
    headers = {"X-Family-ID": "another-synthetic-family"}
    other = client.post("/api/v1/children", headers=headers, json={"name": "合成孩子"}).json()
    second = create_batch(client, headers, other["id"], key="second")
    photo = upload(client, headers, other["id"], second["photos"][0]["id"])
    assert app.state.footprint_worker.process_one()
    assert get_photo(client, headers, other["id"], photo["id"])["has_display"]


def test_late_metadata_never_overwrites_parent_edit(
    client, app, child, family_headers, monkeypatch
):
    from push_kids.footprints import worker

    cid, h = child["id"], family_headers
    batch = create_batch(client, h, cid)
    photo = upload(client, h, cid, batch["photos"][0]["id"])
    original_prepare = worker.prepare

    def edit_during_decode(*args):
        values = original_prepare(*args)
        current = get_photo(client, h, cid, photo["id"])
        patch(client, h, cid, current, local_date="2020-01-02", place_name="家长修正地点")
        return values

    monkeypatch.setattr(worker, "prepare", edit_during_decode)
    assert app.state.footprint_worker.process_one()
    updated = get_photo(client, h, cid, photo["id"])
    assert updated["local_date"] == "2020-01-02" and updated["place_name"] == "家长修正地点"
    assert updated["has_display"] and updated["time_source"] == "parent"


def test_parent_confirm_between_worker_candidate_and_lock_remains_formal(
    client, app, child, family_headers, monkeypatch
):
    from push_kids.footprints import access

    cid, h = child["id"], family_headers
    batch = create_batch(client, h, cid)
    photo = upload(client, h, cid, batch["photos"][0]["id"])
    assert app.state.footprint_worker.process_one()
    photo = get_photo(client, h, cid, photo["id"])
    with app.state.database.session_factory() as db:
        row = db.get(FootprintPhoto, photo["id"])
        row.job_state, row.available_at = "queued", utcnow()
        db.commit()
    original, fired = access.guard, False

    def parent_wins(*args, **kwargs):
        nonlocal fired
        if not fired:
            fired = True
            assert confirm(client, h, cid, batch["id"], [photo]).status_code == 200
        return original(*args, **kwargs)

    monkeypatch.setattr(access, "guard", parent_wins)
    assert app.state.footprint_worker.process_one() is False
    final = get_photo(client, h, cid, photo["id"])
    assert final["state"] == "confirmed" and final["version"] == photo["version"] + 1


def test_authenticated_viewer_cannot_mutate_and_member_preferences_are_isolated(client):
    from tests.integration.test_notification_channel import _actor, _create_family, _join

    _create_family(client)
    request_id = _join(client, "viewer", "家人")
    approved = client.post(
        f"/api/v1/family-requests/{request_id}/approve",
        headers={**_actor("parent-a"), "Idempotency-Key": "footprint-viewer-approval"},
        json={"role": "viewer"},
    )
    assert approved.status_code == 200, approved.text
    cid = client.get("/api/v1/children", headers=_actor("parent-a")).json()[0]["id"]
    assert client.get(f"{ROOT}/summary?child_id={cid}", headers=_actor("viewer")).status_code == 200
    assert (
        client.post(
            ROOT + "/imports",
            headers={**_actor("viewer"), "Idempotency-Key": "forbidden"},
            json={"child_id": cid, "count": 1, "consented": True},
        ).status_code
        == 403
    )
    assert (
        client.patch(
            ROOT + "/preferences",
            headers=_actor("parent-a"),
            json={"ai_enabled": True, "consented": True},
        ).status_code
        == 200
    )
    assert not client.get(ROOT + "/preferences", headers=_actor("viewer")).json()["ai_enabled"]
