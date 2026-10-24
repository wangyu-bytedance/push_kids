"""Malformed optional metadata remains independent; decoder execution is bounded."""

import subprocess

import pytest
from push_kids.footprints.metadata import _extract, prepare_bounded


def test_bad_date_does_not_discard_valid_gps():
    class Exif(dict):
        def get_ifd(self, tag):
            return {1: "N", 2: (39, 54, 0), 3: "E", 4: (116, 24, 0)} if tag == 34853 else {}

    class Image:
        def getexif(self):
            return Exif({36867: "malformed", 34853: True})

    values = _extract(Image())
    assert "local_date" not in values
    assert values["latitude"] == 39.9 and values["longitude"] == 116.4


def test_decoder_timeout_is_sanitized(monkeypatch, tmp_path):
    def timeout(command, **kwargs):
        assert kwargs["timeout"] == 10
        raise subprocess.TimeoutExpired(command, 10, stderr="untrusted metadata")

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(ValueError, match="处理失败或超时") as error:
        prepare_bounded(tmp_path / "input", tmp_path / "display", tmp_path / "thumb")
    assert "untrusted" not in str(error.value)
