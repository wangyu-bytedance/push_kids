"""Real upload -> numbered analysis -> confirmation -> scoped source projection."""

import json
import subprocess
from datetime import timedelta

from push_kids.agent_processing.contracts import EvidenceReference
from push_kids.agent_processing.providers import DeterministicTestProvider
from push_kids.persistence.models import (
    KnowledgeItem,
    ReviewItem,
)
from push_kids.platform.time import utcnow

from tests.integration.test_todo_provenance import PNG, _todo_items


class NumberedProvider(DeterministicTestProvider):
    def _analyze(self, data, search_history):
        result = super()._analyze(data, search_history)
        for point in result.knowledge_points:
            point.direct_evidence = [
                EvidenceReference(source="parent_text", detail="合成家长说明"),
                EvidenceReference(source="image", image_index=2, detail=f"{data.text}的照片2"),
            ]
        return result


def test_numbered_photos_remain_bound_to_original_submission(client, app, family_headers, child):
    app.state.worker.provider = NumberedProvider()
    confirmed = []
    for label in ("数学，加法", "数学，减法"):
        created = client.post(
            "/api/v1/submissions/upload",
            headers=family_headers,
            data={
                "child_id": child["id"],
                "occurred_at": (utcnow() - timedelta(days=4)).isoformat(),
                "input_text": label,
            },
            files=[
                ("files", (f"page-{i}.png", PNG + label.encode() + bytes([i]), "image/png"))
                for i in range(3)
            ],
        )
        assert created.status_code == 202, created.text
        sid = created.json()["id"]
        assert app.state.worker.process_one()
        submission = client.get(f"/api/v1/submissions/{sid}", headers=family_headers).json()
        assert submission["state"] == "pending_confirmation", submission
        assert (
            submission["proposal"]["knowledge_points"][0]["direct_evidence"][1]["image_index"] == 2
        )
        result = client.post(
            f"/api/v1/submissions/{sid}/confirm",
            headers=family_headers,
            json={"proposal": submission["proposal"]},
        )
        assert result.status_code == 200, result.text
        confirmed.append((sid, result.json()["review_item_ids"]))
    items = _todo_items(client, family_headers, child["id"])
    media_ids = []
    for sid, reviews in confirmed:
        selected = [i for i in items if i["review_id"] in reviews]
        assert selected and all(
            i["source_submission_id"] == sid and i["source_image_index"] == 2 for i in selected
        )
        response = client.get(
            f"/api/v1/children/{child['id']}/history/{sid}", headers=family_headers
        )
        assert response.status_code == 200
        detail = response.json()
        assert [m["index"] for m in detail["media"]] == [1, 2, 3]
        media_ids.append(detail["media"][1]["id"])
        # Feed real HTTP projections into the shipped component, across both numbered batches.
        subprocess.run(
            [
                "node",
                "-e",
                r"""
const fs = require('node:fs'), vm = require('node:vm'), assert = require('node:assert/strict');
const { item, detail, childId } = JSON.parse(fs.readFileSync(0, 'utf8'));
const calls = [], downloads = [], previews = [];
let component;
const api = {
  async request(url) { calls.push(url); return url.includes('/history/') ? detail : { url }; },
  async downloadPreview(value) { downloads.push(value.url); return 'private-preview'; },
  removePreview() {}
};
const source = fs.readFileSync('apps/miniprogram/components/submission-materials/index.js', 'utf8');
vm.runInNewContext(source, {
  Component(value) { component = value; }, require() { return api; },
  wx: { previewImage(value) { previews.push(value); } }
});
const instance = { ...component.methods, data: { ...component.data, childId,
  submissionId: item.source_submission_id,
  highlightIndex: item.source_image_index, exactSource: true } };
instance.setData = updates => Object.entries(updates).forEach(([key, value]) => {
  const parts = key.replace(/\[(\d+)\]/g, '.$1').split('.'); let target = instance.data;
  for (const part of parts.slice(0, -1)) target = target[part]; target[parts.at(-1)] = value;
});
(async () => {
  await instance.load();
  assert.equal(instance.data.media.length, 1);
  assert.equal(instance.data.media[0].id, detail.media[1].id);
  assert.equal(instance.data.text, '');
  await instance.preview({ currentTarget: { dataset: { id: detail.media[1].id } } });
  assert.equal(calls.length, 3);
  for (const url of calls.slice(1)) {
    const mediaPath = `/submissions/${item.source_submission_id}/media/${detail.media[1].id}`;
    assert.equal(url, `${mediaPath}/preview?child_id=${childId}`);
  }
  assert.equal(downloads.length, 2);
  assert.deepEqual(Array.from(previews[0].urls), ['private-preview']);
})().catch(error => { console.error(error); process.exitCode = 1; });
""",
            ],
            input=json.dumps({"item": selected[0], "detail": detail, "childId": child["id"]}),
            text=True,
            capture_output=True,
            check=True,
            timeout=10,
        )
    assert media_ids[0] != media_ids[1]
    denied = client.get(
        f"/api/v1/submissions/{confirmed[0][0]}/media/{media_ids[1]}/preview",
        headers=family_headers,
        params={"child_id": child["id"]},
    )
    assert denied.status_code == 404
    dashboard = client.get(
        f"/api/v1/children/{child['id']}/dashboard", headers=family_headers
    ).json()
    assert all(
        i["source_image_index"] == 2
        for s in dashboard["review_selection"]["sessions"]
        for i in s["items"]
    )

    # A legacy gap filled from another submission is not proof of an A image, even at index 2.
    with app.state.database.session_factory() as db:
        review = db.get(ReviewItem, confirmed[0][1][0])
        knowledge = db.get(KnowledgeItem, review.knowledge_item_id)
        knowledge.evidence_json = json.dumps(
            [{"source": "image", "image_index": 2, "detail": "来自其他批次"}]
        )
        db.commit()
    item = next(
        i
        for i in _todo_items(client, family_headers, child["id"])
        if i["review_id"] == confirmed[0][1][0]
    )
    assert item["source_image_index"] is None
    assert item["source_summary"] is None
