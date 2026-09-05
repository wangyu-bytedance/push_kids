from push_kids.agent_processing.contracts import AnalysisInput
from push_kids.agent_processing.providers import DeterministicTestProvider
from push_kids.knowledge.normalization import normalize_knowledge_name


def test_normalization_removes_cosmetic_variation() -> None:
    assert normalize_knowledge_name(" 进位 加法（两位数） ") == normalize_knowledge_name(
        "进位加法,两位数"
    )


def test_test_provider_is_deterministic_and_subject_aware() -> None:
    result = DeterministicTestProvider().analyze(AnalysisInput(text="数学：两位数进位加法，口算"))
    assert result.subject_name == "数学"
    assert result.knowledge_points[0].review_method == "口算与讲解"
    assert "数学" in result.summary
