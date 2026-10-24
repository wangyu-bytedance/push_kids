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


def module_graph() -> dict[str, set[str]]:
    """Include lazy imports and resolved from-import aliases, not just top-level domains."""
    files = {}
    for path in SOURCE.rglob("*.py"):
        parts = path.relative_to(SOURCE.parent).with_suffix("").parts
        module = ".".join(parts[:-1] if parts[-1] == "__init__" else parts)
        files[module] = path
    graph = {module: set() for module in files}
    for module, path in files.items():
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                graph[module].update(alias.name for alias in node.names if alias.name in files)
            elif isinstance(node, ast.ImportFrom) and node.module:
                for alias in node.names:
                    target = f"{node.module}.{alias.name}"
                    if target not in files:
                        target = node.module
                    if target in files and target != module:
                        graph[module].add(target)
    return graph


def dependency_violations(graph: dict[str, set[str]]) -> list[str]:
    violations, visited, active = [], set(), []

    def visit(module):
        if module in active:
            violations.append(
                "import cycle: " + " -> ".join(active[active.index(module) :] + [module])
            )
            return
        if module in visited:
            return
        active.append(module)
        for dependency in sorted(graph[module]):
            visit(dependency)
        active.pop()
        visited.add(module)

    for module in sorted(graph):
        visit(module)
        for target in graph[module]:
            owner, consumer = module.split(".")[1], target.split(".")[1]
            if owner == "footprints" and consumer in {"learning", "planning", "travel"}:
                violations.append(f"footprint boundary: {module} -> {target}")
            if owner in {"families", "children", "media"} and consumer == "footprints":
                violations.append(f"reverse footprint dependency: {module} -> {target}")
            if module.endswith("footprint_provider") and target.endswith("footprints.models"):
                violations.append(f"provider imports owned ORM: {module} -> {target}")
    return violations


def main() -> None:
    policy_files = [
        SOURCE / "planning" / "domain.py",
        SOURCE / "knowledge" / "normalization.py",
        SOURCE / "notifications" / "domain.py",
        SOURCE / "footprints" / "policies.py",
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
    graph = module_graph()
    violations.extend(dependency_violations(graph))
    if violations:
        print("ARCHITECTURE_INVALID")
        print("\n".join(violations))
        raise SystemExit(1)
    print(
        f"ARCHITECTURE_VALID policies={len(policy_files)} modules={len(graph)} (runtime/lazy DAG)"
    )


if __name__ == "__main__":
    main()
