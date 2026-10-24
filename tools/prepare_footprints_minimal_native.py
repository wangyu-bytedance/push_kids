"""Prepare an offline native copy for the approved footprint UI reduction."""

import hashlib
import json
from pathlib import Path

import prepare_record_type_native as base


def main():
    base.OUT = Path("/private/tmp/push-kids-footprints-minimal-native-20261024")
    base.main()
    config = base.OUT / "project.config.json"
    value = json.loads(config.read_text())
    value["projectname"] = "push-kids-footprints-minimal-synthetic"
    config.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    api = base.OUT / "utils/api.js"
    api.write_text(
        api.read_text().replace(
            "if(url.startsWith('/children?')||url==='/children')return [child];",
            "if(url.startsWith('/children?')||url==='/children')return [child,"
            "{...child,id:'synthetic-archive',name:'合成旧档案',active:false}];",
        )
    )
    files = [
        "pages/records/record-types.js",
        "pages/records/index.js",
        "pages/records/index.wxml",
        "pages/records/index.wxss",
        "pages/footprints/controller.js",
        "pages/footprints/imports.js",
        "pages/footprints/index.wxml",
        "pages/footprints/index.wxss",
        "pages/footprints/embedded.js",
    ]
    manifest = {
        "scope": "synthetic read-only transport plus applyGeometryFixture only; no business writes",
        "source_sha256": {
            file: hashlib.sha256((base.ROOT / "apps/miniprogram" / file).read_bytes()).hexdigest()
            for file in files
        },
    }
    (base.OUT / "minimal-source-sha256.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
