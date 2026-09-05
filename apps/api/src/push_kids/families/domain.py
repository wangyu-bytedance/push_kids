from __future__ import annotations


def requires_last_manager_protection(
    current_role: str, next_role: str | None, active_manager_count: int
) -> bool:
    return current_role == "manager" and next_role != "manager" and active_manager_count <= 1
