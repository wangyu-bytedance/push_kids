"""Calendar boundaries and untrusted suggestion contracts, independent of storage."""

from datetime import date, timedelta

import pytest
from push_kids.agent_processing.suggestion_contracts import LearningSuggestionContent
from push_kids.learning_suggestions.generation import content_hash, validate_content
from push_kids.learning_suggestions.policy import eligibility
from push_kids.planning.early_review import early_eligible
from pydantic import ValidationError

DAY = date(2026, 10, 24)


@pytest.mark.parametrize(
    "last,observed,expected",
    [
        (None, 3, "eligible"),
        (3, 3, "eligible"),
        (None, 2, "warming_up"),
        (2, 5, "recent_new"),
        (1, 5, "recent_new"),
        (0, 5, "recent_new"),
        (3, 1, "warming_up"),
    ],
)
def test_two_complete_natural_days(last, observed, expected):
    context = dict(
        active=True,
        grade="小学二年级",
        subjects=[{}],
        knowledge=[{}],
        observed_since=(DAY - timedelta(days=observed)).isoformat(),
        last_new_confirmed_on=(DAY - timedelta(days=last)).isoformat()
        if last is not None
        else None,
    )
    assert eligibility(context, DAY, enabled=True) == expected
    assert eligibility(context, DAY, enabled=False, pending=True) == "pending"


@pytest.mark.parametrize(
    "elapsed,interval,count,offered,expected",
    [
        (8, 10, 1, None, True),
        (7, 10, 1, None, False),
        (2, 3, 1, None, False),
        (12, 15, 1, 2, True),
        (12, 16, 1, None, False),
        (8, 9, 0, None, False),
        (8, 9, 1, 1, False),
        (8, 9, 1, 2, True),
    ],
)
def test_early_review_exact_interval_boundaries(elapsed, interval, count, offered, expected):
    last = DAY - timedelta(days=elapsed)
    assert (
        early_eligible(
            target=DAY,
            due=last + timedelta(days=interval),
            last_reviewed=last,
            review_count=count,
            last_offered=DAY - timedelta(days=offered) if offered else None,
        )
        is expected
    )


def content(**overrides):
    return LearningSuggestionContent.model_validate(
        dict(
            title="用积木把加法换一个表示方法",
            instructions="摆出两组积木，试着用算式表示合起来的数量。",
            rationale="参考之前记录的加法",
            uncertainty="仅参考最近已确认内容，请家长核对是否合适。",
            subject_id="math",
            source_aliases=["K1"],
            estimated_minutes=12,
            **overrides,
        )
    )


@pytest.mark.parametrize(
    "change",
    [
        {"source_aliases": ["unknown"]},
        {"subject_id": "foreign"},
        {"source_aliases": ["K1", "K1"]},
        {"rationale": "孩子已经完全掌握"},
    ],
)
def test_provider_cannot_invent_reference_or_mastery(change):
    base = content().model_dump()
    base.update(change)
    with pytest.raises(ValueError):
        validate_content(LearningSuggestionContent.model_validate(base), CONTEXT)


CONTEXT = {
    "subjects": [{"id": "math", "name": "数学"}],
    "knowledge": [{"alias": "K1", "id": "real", "name": "十以内加法", "subject_id": "math"}],
}


def test_replacement_must_differ_and_learning_has_no_ten_minute_cap():
    result = validate_content(content(), CONTEXT)
    assert result["estimated_minutes"] == 12
    assert result["sources"] == [{"knowledge_id": "real", "name": "十以内加法"}]
    with pytest.raises(ValueError, match="repeated_content"):
        validate_content(content(), CONTEXT, content_hash(result))
    raw = content().model_dump()
    raw["review_date"] = "2026-10-25"
    with pytest.raises(ValidationError):
        LearningSuggestionContent.model_validate(raw)


@pytest.mark.parametrize(
    "title,valid",
    [
        ("", False),
        ("   ", False),
        ("数", True),
        ("题" * 20, True),
        ("题" * 21, False),
        ("题" * 120, False),
        ("  " + "题" * 20 + "  ", True),
        ("活动\n步骤", False),
        ("活动\r步骤", False),
        ("活动\u2028步骤", False),
        ("活动\u2029步骤", False),
        ("𠀀" * 20, True),
        ("𠀀" * 21, False),
    ],
)
def test_suggestion_title_contract_matches_model_and_edit(title, valid):
    from push_kids.learning_suggestions.schemas import Edit

    raw = content().model_dump()
    raw["title"] = title
    edit = {"expected_version": 1, "title": title, "instructions": "摆出两组积木"}
    if valid:
        assert LearningSuggestionContent.model_validate(raw).title == title.strip()
        assert Edit.model_validate(edit).title == title.strip()
    else:
        with pytest.raises(ValidationError):
            LearningSuggestionContent.model_validate(raw)
        with pytest.raises(ValidationError):
            Edit.model_validate(edit)


def test_suggestion_title_write_revalidates_unchecked_provider_instance():
    unchecked = content().model_copy(update={"title": "题" * 21})
    with pytest.raises(ValidationError):
        validate_content(unchecked, CONTEXT)


def test_suggestion_title_test_provider_bounds_long_untrusted_source():
    from push_kids.agent_processing.suggestion_provider import TestSuggestionProvider

    context = {"knowledge": [{**CONTEXT["knowledge"][0], "name": "长知识\n名称" * 20}]}
    provider = TestSuggestionProvider()
    original = provider.suggest(context)
    replacement = provider.suggest({**context, "excluded_content": original.model_dump()})
    assert len(original.title) <= 20 and "\n" not in original.title
    assert len(replacement.title) <= 20 and replacement.title != original.title
