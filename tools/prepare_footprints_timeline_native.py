"""Prepare an offline native copy for approved BUG-034 geometry verification."""

import hashlib
import json
from pathlib import Path

import prepare_record_type_native as base


def main():
    base.OUT = Path("/private/tmp/push-kids-footprints-timeline-native-20261024")
    base.main()
    controller = base.OUT / "pages/footprints/controller.js"
    controller.write_text(
        controller.read_text().replace(
            "applyGeometryFixture(serialized) { this.setData(JSON.parse(serialized)); }",
            "applyGeometryFixture(serialized) { const data=JSON.parse(serialized);"
            "if(data.visits)data.visits=data.visits.map(timelineVisit);this.setData(data); }",
        )
    )
    config = base.OUT / "project.config.json"
    value = json.loads(config.read_text())
    value["projectname"] = "push-kids-footprints-timeline-synthetic"
    config.write_text(json.dumps(value, ensure_ascii=False, indent=2))
    files = [
        "pages/footprints/controller.js",
        "pages/footprints/presentation.js",
        "pages/footprints/index.wxml",
        "pages/footprints/index.wxss",
        "pages/footprints/embedded.js",
        "pages/footprints/embedded.wxml",
        "pages/footprints/embedded.wxss",
        "pages/records/index.wxml",
        "pages/records/index.wxss",
        "styles/atoms.wxss",
        "styles/tokens.wxss",
    ]
    manifest = {
        "scope": "offline synthetic transport; fixture/scroll bindings only in copy",
        "source_sha256": {
            file: hashlib.sha256((base.ROOT / "apps/miniprogram" / file).read_bytes()).hexdigest()
            for file in files
        },
    }
    (base.OUT / "timeline-source-sha256.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    main()
