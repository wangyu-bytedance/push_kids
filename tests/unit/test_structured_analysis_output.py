import pytest
from push_kids.agent_processing.contracts import (
    AnalysisInput,
    AnalysisProposal,
    KnowledgeProposal,
    infer_display_kind,
)
from push_kids.agent_processing.presentation import project_display_groups
from pydantic import ValidationError


def point(name: str, category: str, display_kind=None) -> KnowledgeProposal:
    return KnowledgeProposal(
        name=name,
        category=category,
        display_kind=display_kind,
        direct_evidence=[{"source": "parent_text", "detail": name}],
    )


def test_projects_atomic_points_into_ordered_parent_facing_groups() -> None:
    groups = project_display_groups(
        [
            point("20 以内加法", "计算", "arithmetic"),
            point("spring", "词汇", "word"),
            point("春", "汉字", "hanzi"),
            point("晓", "汉字", "hanzi"),
            point("《春晓》", "古诗", "poem"),
        ]
    )

    assert [group.kind for group in groups] == ["hanzi", "word", "poem", "arithmetic"]
    assert groups[0].model_dump() == {
        "kind": "hanzi",
        "label": "汉字",
        "items": ["春", "晓"],
    }
    assert groups[-1].items == ["20 以内加法"]


@pytest.mark.parametrize(
    ("name", "category", "expected"),
    [
        ("春", "生字", "hanzi"),
        ("spring", "词汇与表达", "word"),
        ("《春晓》", "字词与阅读", "poem"),
        ("两位数进位加法", "知识点", "arithmetic"),
        ("平行四边形", "图形", "concept"),
        ("跳绳", "课外活动", "activity"),
        ("待核对内容", "其他", "other"),
    ],
)
def test_legacy_categories_have_a_bounded_compatibility_mapping(
    name: str, category: str, expected: str
) -> None:
    assert infer_display_kind(name, category) == expected


def test_model_validation_fills_kind_but_keeps_parent_summary_compatibility() -> None:
    data = AnalysisInput(text="练习20以内加法")
    proposal = AnalysisProposal(
        summary="练习了20以内加法",
        subject_name="数学",
        knowledge_points=[point("20 以内加法", "计算")],
    )
    assert data.validate_proposal(proposal).knowledge_points[0].display_kind == "arithmetic"

    parent_edited = proposal.model_copy(update={"summary": "家长补充" * 40})
    assert len(parent_edited.summary) > 120
    assert AnalysisProposal.model_validate(parent_edited.model_dump())
    with pytest.raises(ValueError, match="summary is too long"):
        data.validate_proposal(parent_edited)


def test_display_kind_rejects_unbounded_model_labels() -> None:
    with pytest.raises(ValidationError):
        KnowledgeProposal(name="春", category="汉字", display_kind="模型自定义标签")
