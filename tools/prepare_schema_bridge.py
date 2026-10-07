"""Freeze the deployed 025 business code with the reviewed additive-schema allowlist.

This is a release artifact, never the new feature server. Do not broaden the allowlist
or change the pinned business revision without another compatibility review.
"""

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

from prepare_cloud_release import ROOT_FILES, SOURCE_DIRECTORY, prepare_release

BUSINESS_REVISION = "b3db219"
ACCEPTED_REVISIONS = (
    "20260913_0014",
    "20261006_0015",
    "20261006_0016",
    "20261007_0017",
    "20261007_0018",
)


def prepare_bridge(root: Path) -> Path:
    commit = subprocess.check_output(
        ["git", "rev-parse", f"{BUSINESS_REVISION}^{{commit}}"], cwd=root, text=True
    ).strip()
    names = subprocess.check_output(
        ["git", "ls-tree", "-r", "--name-only", commit, *ROOT_FILES, str(SOURCE_DIRECTORY)],
        cwd=root,
        text=True,
    ).splitlines()
    source = root / "dist" / "schema-bridge-source"
    for name in names:
        if name not in ROOT_FILES and not name.endswith(".py"):
            continue
        target = source / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(subprocess.check_output(["git", "show", f"{commit}:{name}"], cwd=root))
    database = source / SOURCE_DIRECTORY / "push_kids/platform/database.py"
    content = database.read_text()
    before = "if revision != self.expected_cloud_revision:"
    assert content.count(before) == 1
    database.write_text(content.replace(before, f"if revision not in {ACCEPTED_REVISIONS!r}:"))
    output = source / "dist" / "cloud-release"
    manifest = prepare_release(source, output)
    evidence = {
        "business_commit": commit,
        "accepted_revisions": ACCEPTED_REVISIONS,
        "only_patch": "Database.verify_cloud_schema exact additive revision allowlist",
        "database_sha256": hashlib.sha256(database.read_bytes()).hexdigest(),
        "manifest_sha256": hashlib.sha256(
            (output / "release-manifest.json").read_bytes()
        ).hexdigest(),
        "files": len(manifest),
        "bytes": sum(int(item["bytes"]) for item in manifest),
    }
    (root / "dist/schema-bridge-provenance.json").write_text(json.dumps(evidence, indent=2) + "\n")
    print(json.dumps(evidence, indent=2))
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args()
    prepare_bridge(Path(__file__).resolve().parents[1])
