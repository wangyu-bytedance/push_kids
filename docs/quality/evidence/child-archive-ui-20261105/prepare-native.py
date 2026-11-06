"""Reuse the write-rejecting grade fixture with current child-edit presentation."""

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPT = ROOT / "tools/prepare_grade_confirmation_native.py"
SPEC = importlib.util.spec_from_file_location("archive_native_fixture", SCRIPT)
assert SPEC and SPEC.loader
fixture = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fixture)
fixture.OUT = Path("/private/tmp/push-kids-archive-native-20261105")
fixture.main()
