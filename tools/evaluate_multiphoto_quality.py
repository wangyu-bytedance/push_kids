#!/usr/bin/env python3
"""24 reproducible synthetic multi-photo cases, repeated three times by default.

Checks protocol/subject/source completeness; does not claim human semantic adjudication.
"""

from __future__ import annotations

import argparse
import json
import logging
import tempfile
from collections import Counter
from pathlib import Path
from time import monotonic

from evaluate_analysis_quality import (
    PIPELINE_REVISION,
    AnalysisProposal,
    AnalysisWorker,
    Database,
    LearningSubmission,
    LocalMediaStore,
    Settings,
    StagedArkProvider,
    SubmissionMedia,
    _formal_write_count,
    _process_case,
    _render_fixture,
    _seed_case,
)


def cases():
    math = [
        "数学：两位数进位加法，28+17。",
        "数学：两位数退位减法，52-28。",
        "数学：乘法口诀，4乘6。",
        "数学：平均分，12个圆分成3组。",
        "数学：比较分数二分之一和三分之一。",
        "数学：辨认长方形和三角形。",
        "数学：读取钟面7时30分。",
        "数学：用厘米测量铅笔长度。",
        "数学：观察数列2、5、8、11的规律。",
    ]
    for count in (2, 3, 6, 9):
        for mode in ("distinct", "mixed", "duplicates", "with_text", "cross_page", "dense"):
            pages = math[:count]
            subjects = {"数学"}
            text = None
            expected = set(range(1, count + 1))
            if mode == "mixed":
                pages = [
                    [
                        "数学：计算28+17。",
                        "语文：区分请、清、情并组词。",
                        "English: practise This is my friend.",
                    ][i % 3]
                    + f" 练习页{i + 1}"
                    for i in range(count)
                ]
                subjects = {"数学", "语文"} | ({"英语"} if count >= 3 else set())
            elif mode == "duplicates":
                pages = [math[0]] * count
                expected = {1}
            elif mode == "with_text":
                text = "另外练习英语颜色单词 red、blue、green。"
                subjects.add("英语")
            elif mode == "cross_page":
                pages[:2] = [
                    "数学应用题第1页：小明有一些铅笔，又买了一些。数量及问题见下一页。",
                    "接上一页数学应用题：原来有12支，又买了5支。现在一共有多少支铅笔？",
                ]
            elif mode == "dense":
                pages = [math[i] + " 写出计算过程，说明方法。" for i in range(count)]
            yield dict(
                id=f"multi-{count}-{mode}",
                subject=sorted(subjects),
                input_type="text",
                material=text or "",
                pages=pages,
                expected=expected,
            )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--repeats", type=int, default=3, choices=range(1, 4))
    parser.add_argument("--case", action="append", default=[], help="Exact synthetic case IDs")
    args = parser.parse_args()
    logging.disable(logging.CRITICAL)
    settings = Settings()
    results = []
    with tempfile.TemporaryDirectory(prefix="push-kids-multiphoto-") as temporary:
        directory = Path(temporary)
        database = Database(
            settings.model_copy(
                update={"env": "test", "database_url": f"sqlite:///{directory / 'quality.db'}"}
            )
        )
        database.create_schema()
        media = LocalMediaStore(directory, settings.upload_max_bytes)
        worker = AnalysisWorker(database, StagedArkProvider(settings), media)
        for repeat in range(args.repeats):
            for case in cases():
                if args.case and case["id"] not in args.case:
                    continue
                sid = _seed_case(database, case, directory)
                with database.session_factory() as db:
                    submission = db.get(LearningSubmission, sid)
                    submission.input_text = case["material"] or None
                    for i, page in enumerate(case["pages"], 1):
                        path = _render_fixture(f"{sid}-{i}", page, directory)
                        db.add(
                            SubmissionMedia(
                                submission_id=sid,
                                path=str(path),
                                sort_order=i,
                                content_type="image/png",
                                byte_size=path.stat().st_size,
                            )
                        )
                    db.commit()
                started = monotonic()
                code, attempts, empty = _process_case(
                    database, worker, media, sid, set(case["subject"])
                )
                # Cancel preserves the isolated proposal JSON, allowing source verification.
                with database.session_factory() as db:
                    stored = db.get(LearningSubmission, sid).proposal_json
                    if code is None and stored:
                        proposal = AnalysisProposal.model_validate_json(stored)
                        sources = {
                            e.image_index
                            for p in proposal.knowledge_points
                            for e in p.direct_evidence
                            if e.source == "image"
                        }
                        if sources != case["expected"]:
                            code = "evidence.coverage"
                result = dict(
                    case=case["id"],
                    repeat=repeat + 1,
                    images=len(case["pages"]),
                    success=code is None,
                    code=code,
                    attempts=attempts,
                    seconds=round(monotonic() - started, 2),
                    empty=empty,
                )
                results.append(result)
                report = dict(
                    scope="synthetic; source and subject checks; semantic review pending",
                    model=settings.ark_model,
                    pipeline_revision=PIPELINE_REVISION,
                    results=results,
                    formal_writes=_formal_write_count(database),
                    failures=dict(Counter(r["code"] for r in results if r["code"])),
                )
                args.report.parent.mkdir(parents=True, exist_ok=True)
                args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
                print(json.dumps(result), flush=True)
    return int(any(not r["success"] for r in results))


if __name__ == "__main__":
    raise SystemExit(main())
