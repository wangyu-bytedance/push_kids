"""Bind current design sources, coverage and exported evidence."""
import hashlib
import json
import struct
from datetime import datetime, timezone
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[4]
OUT=ROOT/"docs/design/frontend/snapshots/UI-001"/HERE.name


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n")


def main():
    v=json.loads((OUT/"verification.json").read_text())
    interactions=json.loads((OUT/"interaction-checks.json").read_text())
    assert len(v["checks"])==975
    assert all(not c["horizontal"] and not c["smallTargets"] and not c["bodyOverflow"] for c in v["checks"])
    assert not v["javascriptErrors"] and not v["externalRequests"]
    assert len(interactions["checks"])==15 and all(c["passed"] for c in interactions["checks"])
    assert not interactions["javascriptErrors"] and not interactions["externalRequests"]
    routes={}
    for line in (HERE/"FRONTEND-SPEC.md").read_text().splitlines():
        if line.startswith("| pages/"):
            parts=[x.strip() for x in line.split("|")[1:-1]]
            routes[parts[0]]=parts[1].split(", ")
    assert set(routes)==set(json.loads((ROOT/"apps/miniprogram/app.json").read_text())["pages"])
    assert {s["id"] for s in v["scenes"]}=={s for group in routes.values() for s in group}
    write("coverage.json",{"routes":routes,"routeCount":17,"sceneCount":65,"themes":v["themes"],"designCombinations":325,"viewportExports":975,"scenes":v["scenes"],"scope":"Current routes and representative key states; not all state permutations or native system UI."})
    historical=[]
    for path in sorted(OUT.parent.glob("DREV-20261106-UI-CONSISTENCY-" + "*" + "/manifest.json")):
        if path.parent==OUT:continue
        m=json.loads(path.read_text())
        items=m.get("sources",[])+m.get("files",m.get("exports",[]))
        failures=[x["path"] for x in items if not (ROOT/x["path"]).exists() or digest(ROOT/x["path"])!=x["sha256"]]
        historical.append({"revision":path.parent.name,"entries":len(items),"failures":failures})
    assert all(not x["failures"] for x in historical)
    assets=json.loads((HERE/"assets.json").read_text())
    assert all(digest(ROOT/a["path"])==a["sha256"]==digest(Path(a["source"])) for a in assets)
    before=json.loads((HERE/"production-before.json").read_text())
    after={str(p.relative_to(ROOT)):digest(p) for p in (ROOT/"apps").rglob("*") if p.is_file() and not any(s in p.parts for s in ["node_modules","__pycache__",".DS_Store"])}
    assert before==after
    write("integrity-check.json",{"checkedAt":datetime.now(timezone.utc).isoformat(),"historicalManifests":historical,"originalAssetsMatched":5,"productionFilesUnchanged":len(before),"passed":True})
    exports=[]
    for c in v["checks"]:
        w,h=c["viewport"];p=OUT/c["theme"]/f"{c['scene']}-{w}x{h}.png"
        assert struct.unpack(">II",p.read_bytes()[16:24])==(w,h)
        exports.append({"theme":c["theme"],"scene":c["scene"],"viewport":[w,h],"path":str(p.relative_to(ROOT)),"sha256":digest(p)})
    boards=[OUT/f"{t}-{b}.png" for t in v["themes"] for b in ["main","all"]]
    boards += [OUT/"overview.png",OUT/"gallery-1440x1050.png",OUT/"gallery-390x844.png"]
    exports += [{"path":str(p.relative_to(ROOT)),"sha256":digest(p)} for p in boards]
    names=["FRONTEND-SPEC.md","PROMPTS.md","build.py","themes.css","screens.js","gallery.js","index.html","export.py","verify.py","finalize.py","assets.json"]
    sources=[HERE/n for n in names]+[HERE/"assets"/f"{t}.png" for t in v["themes"]]+[HERE.parent/"DREV-20261106-UI-CONSISTENCY-02/index.html"]
    write("manifest.json",{"designRevision":HERE.name,"taskSpecRevision":"DESIGN-002-SPEC-06","status":"PENDING_FULL_INTERFACE_REVIEW","generatedAt":datetime.now(timezone.utc).isoformat(),"sources":[{"path":str(p.relative_to(ROOT)),"sha256":digest(p)} for p in sources],"exports":exports,"evidenceSha256":{n:digest(OUT/n) for n in ["verification.json","interaction-checks.json","coverage.json","integrity-check.json"]},"nativeAcceptance":"NOT_RUN"})
    print(json.dumps({"routes":17,"scenes":65,"designCombinations":325,"screenExports":975,"boardsAndGallery":len(boards),"sourceHashes":len(sources),"interactiveChecks":15,"productionFilesUnchanged":len(before),"passed":True}))


if __name__=="__main__":
    main()
