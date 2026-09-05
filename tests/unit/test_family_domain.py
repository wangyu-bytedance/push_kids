from push_kids.families.domain import requires_last_manager_protection


def test_last_manager_cannot_be_removed_or_demoted() -> None:
    assert requires_last_manager_protection("manager", None, 1) is True
    assert requires_last_manager_protection("manager", "editor", 1) is True
    assert requires_last_manager_protection("manager", "manager", 1) is False
    assert requires_last_manager_protection("manager", None, 2) is False
    assert requires_last_manager_protection("editor", None, 1) is False
