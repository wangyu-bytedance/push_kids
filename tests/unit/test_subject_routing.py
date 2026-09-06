"""Subject routing is pure string policy: it splits, matches and never invents a subject."""

from __future__ import annotations

from push_kids.agent_processing.contracts import AnalysisProposal, KnowledgeProposal
from push_kids.agent_processing.subject_routing import (
    is_merged_subject_label,
    match_subject,
    route_subjects,
    split_subject_label,
)

CATALOGUE = ["数学", "语文", "英语"]


def _proposal(subject_name: str, points: list[tuple[str, str | None]]) -> AnalysisProposal:
    return AnalysisProposal(
        summary="这次学过的内容",
        subject_name=subject_name,
        subject_kind="learning",
        source="照片",
        knowledge_points=[
            KnowledgeProposal(name=name, subject_name=subject) for name, subject in points
        ],
    )


def test_merged_labels_split_into_single_subjects():
    assert split_subject_label("数学.语文、英语", CATALOGUE) == ["数学", "语文", "英语"]
    assert split_subject_label("自定义：数学 语文", CATALOGUE) == ["数学", "语文"]
    assert split_subject_label("数学和语文", CATALOGUE) == ["数学", "语文"]
    assert is_merged_subject_label("数学、语文", CATALOGUE) is True
    assert is_merged_subject_label("数学", CATALOGUE) is False


def test_a_single_subject_name_is_never_shredded():
    # A conjunction or separator inside one real subject name must survive untouched.
    assert split_subject_label("道德与法治", CATALOGUE) == ["道德与法治"]
    assert split_subject_label("机器人编程·进阶", ["机器人编程·进阶"]) == ["机器人编程·进阶"]
    assert is_merged_subject_label("道德与法治", CATALOGUE) is False


def test_aliases_map_onto_the_configured_subject():
    assert match_subject("英文", CATALOGUE) == "英语"
    assert match_subject("math", CATALOGUE) == "数学"
    assert match_subject("围棋", CATALOGUE) is None


def test_points_are_grouped_by_their_own_subject():
    routing = route_subjects(
        CATALOGUE, _proposal("数学、语文", [("两位数加法", "数学"), ("生字听写", "语文")])
    )
    assert [(item.subject_name, item.knowledge_indexes) for item in routing.groups] == [
        ("数学", [0]),
        ("语文", [1]),
    ]
    assert routing.point_subjects == ["数学", "语文"]
    assert all(item.listed for item in routing.groups)
    assert routing.merged_label is True
    assert routing.assumed_points == []
    assert routing.has_unlisted is False
    assert routing.needs_review is True


def test_a_single_subject_batch_keeps_one_group_without_review():
    routing = route_subjects(CATALOGUE, _proposal("数学", [("两位数加法", None)]))
    assert [item.subject_name for item in routing.groups] == ["数学"]
    assert routing.needs_review is False


def test_an_unconfigured_subject_stays_unlisted_instead_of_being_created():
    routing = route_subjects(CATALOGUE, _proposal("科学", [("浮力小实验", None)]))
    assert [(item.subject_name, item.listed) for item in routing.groups] == [("科学", False)]
    assert routing.has_unlisted is True
    assert routing.needs_review is True


def test_a_merged_batch_without_point_subjects_reports_its_assumption():
    routing = route_subjects(CATALOGUE, _proposal("数学、语文", [("两位数加法", None)]))
    assert [item.subject_name for item in routing.groups] == ["数学"]
    assert routing.assumed_points == [0]
    assert routing.needs_review is True
