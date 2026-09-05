import json
from types import SimpleNamespace

import pytest
from push_kids.agent_processing.context import material_fingerprint
from push_kids.agent_processing.contracts import AnalysisInput, AnalysisProposal
from push_kids.agent_processing.providers import ArkAnalysisProvider


def point(name="两位数进位加法", **kwargs):
    return {
        "name": name,
        "direct_evidence": [{"source": "parent_text", "detail": "28+17"}],
        **kwargs,
    }


def body(points, matches=None):
    return AnalysisProposal.model_validate(
        {
            "summary": "进位加法",
            "subject_name": "数学",
            "knowledge_points": points,
            "todo_matches": matches or [],
        }
    )


def test_canonical_knowledge_merges_synonyms_and_retains_evidence():
    data = AnalysisInput(
        text="28+17",
        existing_knowledge=[
            {
                "knowledge_id": "known",
                "subject_name": "数学",
                "name": "两位数进位加法",
                "category": "计算",
            }
        ],
        todo_candidates=[
            {
                "review_id": "review",
                "knowledge_name": "两位数进位加法",
                "step": 3,
                "due_date": "2026-09-06",
            }
        ],
    )
    matches = [{"review_id": "review", "knowledge_name": "两位数进位加法", "evidence": "28+17"}] * 6
    result = data.validate_proposal(
        body(
            [
                point("进位的两位数加法", existing_knowledge_id="known"),
                point("两位数加法进位", existing_knowledge_id="known"),
            ],
            matches,
        )
    )
    assert len(result.knowledge_points) == 1
    assert result.knowledge_points[0].name == "两位数进位加法"
    assert result.knowledge_points[0].category == "计算"
    assert len(result.todo_matches) == 1
    assert result.todo_matches[0].step == 3
    assert result.todo_matches[0].due_date == "2026-09-06"


@pytest.mark.parametrize("invalid", ["id", "subject", "no_evidence", "todo_evidence"])
def test_bad_identity_and_missing_evidence_are_rejected(invalid):
    data = AnalysisInput(
        text="28+17",
        existing_knowledge=[
            {
                "knowledge_id": "known",
                "subject_name": "英语" if invalid == "subject" else "数学",
                "name": "两位数进位加法",
                "category": "计算",
            }
        ],
        todo_candidates=[{"review_id": "review", "knowledge_name": "两位数进位加法"}],
    )
    row = point(existing_knowledge_id="foreign" if invalid == "id" else "known")
    if invalid == "no_evidence":
        row["direct_evidence"] = []
    matches = (
        [{"review_id": "review", "knowledge_name": "两位数进位加法"}]
        if invalid == "todo_evidence"
        else []
    )
    with pytest.raises(ValueError):
        data.validate_proposal(body([row], matches))


def test_duplicate_images_send_once_with_original_numbering(tmp_path):
    paths = [tmp_path / f"image{index}.png" for index in range(3)]
    for path, content in zip(paths, [b"same", b"same", b"different"], strict=True):
        path.write_bytes(content)
    captured = []
    result = body([point()]).model_dump()
    result["knowledge_points"][0]["direct_evidence"] = [
        {"source": "image", "image_index": 3, "detail": "28+17"}
    ]

    def respond(**kwargs):
        captured.append(kwargs)
        return SimpleNamespace(output_text=json.dumps(result))

    provider = object.__new__(ArkAnalysisProvider)
    provider.model = "synthetic"
    provider.client = SimpleNamespace(responses=SimpleNamespace(create=respond))
    output = provider.analyze(AnalysisInput(image_paths=paths))
    sent = captured[0]["input"][0]["content"]
    assert sum(item["type"] == "input_image" for item in sent) == 2
    assert any("原始照片3" in item.get("text", "") for item in sent)
    assert output.knowledge_points[0].direct_evidence[0].image_index == 3
    assert material_fingerprint(None, paths) == material_fingerprint(None, paths[::-1])
    assert material_fingerprint(None, paths) == material_fingerprint(None, [paths[0], paths[2]])
    assert material_fingerprint("另一次内容", paths) != material_fingerprint(None, paths)


def test_deployed_prompt_covers_core_content_and_missing_stage():
    prompt = ArkAnalysisProvider._prompt(
        AnalysisInput(text="今天只练进位", grade="小学二年级", occurred_at="2026-09-05T10:00:00Z")
    )
    for required in [
        "森林超市",
        "两位数进位加法",
        "装饰",
        "不能把以前学过的内容冒充本次学习",
        "小学二年级",
        "2026-09-05T10:00:00Z",
        "不代表掌握程度",
        "不得生成复习日期",
    ]:
        assert required in prompt
    # This asserts the deployed instruction contract, not live model semantic accuracy.
