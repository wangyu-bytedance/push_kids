from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "apps" / "api" / "src" / "push_kids"
FORBIDDEN_DOMAIN_IMPORTS = {"fastapi", "sqlalchemy", "openai", "pydantic_settings"}


def imported_roots(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    roots = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            roots.add(node.module.split(".")[0])
    return roots


def main() -> None:
    policy_files = [
        SOURCE / "planning" / "domain.py",
        SOURCE / "knowledge" / "normalization.py",
        SOURCE / "notifications" / "domain.py",
    ]
    violations = []
    for path in policy_files:
        forbidden = imported_roots(path) & FORBIDDEN_DOMAIN_IMPORTS
        if forbidden:
            violations.append(f"{path.relative_to(ROOT)} imports {sorted(forbidden)}")
    dumping_grounds = [SOURCE / name for name in ("common", "utils", "helpers", "shared")]
    violations.extend(
        f"forbidden dumping-ground module: {path}" for path in dumping_grounds if path.exists()
    )
    if violations:
        print("ARCHITECTURE_INVALID")
        print("\n".join(violations))
        raise SystemExit(1)
    print(f"ARCHITECTURE_VALID checked={len(policy_files)}")


if __name__ == "__main__":
    main()
