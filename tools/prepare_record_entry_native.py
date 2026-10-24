"""Prepare the BUG-032 offline native fixture without changing production transport."""

import hashlib
import json
from pathlib import Path

import prepare_record_type_native as base


def main():
    base.OUT = Path("/private/tmp/push-kids-record-entry-native-20261024")
    base.main()
    config = base.OUT / "project.config.json"
    value = json.loads(config.read_text())
    value["projectname"] = "push-kids-record-entry-synthetic"
    config.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    api = base.OUT / "utils/api.js"
    api.write_text(
        api.read_text().replace(
            "if(url.startsWith('/footprints/visits?'))",
            "if(url.startsWith('/footprints/visits?')&&url.includes('cursor='))"
            "return {items:Array.from({length:20},(_,i)=>"
            "({...visit,id:'next-'+i,photos:[]})),next_cursor:null};\n"
            "if(url.startsWith('/footprints/visits?'))",
        )
    )
    files = [
        "pages/records/record-types.js",
        "pages/records/index.js",
        "pages/records/index.wxml",
        "pages/records/index.wxss",
        "pages/footprints/controller.js",
        "pages/footprints/maps.js",
        "pages/footprints/imports.js",
        "pages/footprints/index.wxml",
        "pages/footprints/index.wxss",
    ]
    manifest = {
        "scope": "synthetic transport plus applyGeometryFixture only; no business writes",
        "source_sha256": {
            file: hashlib.sha256((base.ROOT / "apps/miniprogram" / file).read_bytes()).hexdigest()
            for file in files
        },
    }
    (base.OUT / "record-entry-source-sha256.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
