#!/usr/bin/env python3
"""Read-only, family-scoped historical replay. Reports contain aggregate metrics only.

Historical review state is not versioned: replay deliberately omits present-day Todo state.
Confirmed names are lexical comparison references, NOT independent semantic truth.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import subprocess
import sys
import tempfile
from collections import Counter
from hashlib import sha256
from pathlib import Path
from time import monotonic

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps/api/src"))

import pymysql  # noqa: E402
from dotenv import dotenv_values  # noqa: E402
from push_kids.agent_processing.contracts import (  # noqa: E402
    AnalysisInput,
    AnalysisOutputValidationError,
    ExistingKnowledgeContext,
    RecentLearningContext,
    analysis_failure_disposition,
)
from push_kids.agent_processing.history_search import knowledge_search_terms  # noqa: E402
from push_kids.agent_processing.pipeline import StagedPipeline  # noqa: E402
from push_kids.agent_processing.providers import ArkAnalysisProvider  # noqa: E402
from push_kids.agent_processing.stage_contracts import PIPELINE_REVISION  # noqa: E402
from push_kids.agent_processing.stage_provider import StagedArkProvider  # noqa: E402
from push_kids.knowledge.normalization import normalize_knowledge_name  # noqa: E402
from push_kids.platform.config import Settings  # noqa: E402


def snapshot(job_id, count, directory):
    config = dotenv_values(ROOT / ".env")
    host, _, port = config["MYSQL_ADMIN_ADDRESS"].rpartition(":")
    connection = pymysql.connect(
        host=host,
        port=int(port),
        user=config["MYSQL_ADMIN_USERNAME"],
        password=config["MYSQL_ADMIN_PASSWORD"],
        database="push_kids",
        connect_timeout=5,
        read_timeout=10,
        write_timeout=10,
        cursorclass=pymysql.cursors.DictCursor,
    )
    cases, downloads = [], []
    try:
        with connection.cursor() as q:
            q.execute("SET TRANSACTION ISOLATION LEVEL REPEATABLE READ")
            q.execute("START TRANSACTION READ ONLY")
            q.execute(
                "SELECT family_id,submission_id FROM agent_jobs WHERE id=%s LIMIT 1", (job_id,)
            )
            scope = q.fetchone()
            if not scope:
                raise ValueError("job_missing")
            family = scope["family_id"]
            q.execute(
                "SELECT s.*, (SELECT COUNT(*) FROM submission_media m WHERE "
                "m.submission_id=s.id) image_count FROM learning_submissions s WHERE "
                "s.family_id=%s AND s.state IN ('confirmed','failed') "
                "ORDER BY s.created_at DESC,s.id LIMIT 64",
                (family,),
            )
            rows = q.fetchall()
            selected = [r for r in rows if r["id"] == scope["submission_id"]]
            for layer in range(9):
                selected.extend(
                    [r for r in rows if r["image_count"] == layer and r not in selected][:1]
                )
            selected.extend(r for r in rows if r not in selected)
            for number, row in enumerate(selected[:count], 1):
                child, cutoff = row["child_id"], row["created_at"]
                q.execute(
                    "SELECT grade FROM children WHERE family_id=%s AND id=%s LIMIT 1",
                    (family, child),
                )
                grade = q.fetchone()["grade"]
                q.execute(
                    "SELECT name FROM subjects WHERE family_id=%s AND child_id=%s "
                    "AND kind='learning' "
                    "AND created_at<%s ORDER BY name LIMIT 30",
                    (family, child, cutoff),
                )
                subjects = list(
                    dict.fromkeys(["语文", "数学", "英语"] + [s["name"] for s in q.fetchall()])
                )
                q.execute(
                    "SELECT m.path,m.content_type,m.byte_size,o.sha256 FROM submission_media m "
                    "JOIN learning_submissions s ON s.id=m.submission_id LEFT JOIN media_objects o "
                    "ON o.id=m.media_object_id AND o.family_id=s.family_id WHERE s.family_id=%s "
                    "AND s.id=%s ORDER BY m.sort_order,m.created_at,m.id LIMIT 10",
                    (family, row["id"]),
                )
                media = q.fetchall()
                if len(media) > 9:
                    raise ValueError("media_limit")
                paths = []
                for i, m in enumerate(media):
                    suffix = (
                        ".png"
                        if m["content_type"] == "image/png"
                        else ".webp"
                        if m["content_type"] == "image/webp"
                        else ".jpg"
                    )
                    destination = directory / f"case{number}-image{i}{suffix}"
                    paths.append(destination)
                    downloads.append(
                        dict(
                            ref=m["path"],
                            bytes=m["byte_size"],
                            sha=m["sha256"],
                            destination=str(destination),
                        )
                    )
                q.execute(
                    "SELECT k.id knowledge_id,k.name,k.category,s.name subject_name "
                    "FROM knowledge_items k "
                    "JOIN subjects s ON s.id=k.subject_id AND s.family_id=k.family_id "
                    "WHERE k.family_id=%s AND k.child_id=%s AND k.created_at<%s "
                    "ORDER BY k.created_at DESC,k.id LIMIT 101",
                    (family, child, cutoff),
                )
                history = q.fetchall()
                # Bounded snapshot is explicit; never silently truncate the evaluation corpus.
                if len(history) > 100:
                    raise ValueError("history_snapshot_cap")
                q.execute(
                    "SELECT r.id record_id,s.name subject_name,r.summary,r.occurred_at "
                    "FROM learning_records r JOIN subjects s "
                    "ON s.id=r.subject_id AND s.family_id=r.family_id "
                    "WHERE r.family_id=%s AND r.child_id=%s "
                    "AND r.created_at<%s AND r.submission_id<>%s "
                    "ORDER BY r.created_at DESC,r.id LIMIT 6",
                    (family, child, cutoff, row["id"]),
                )
                recent = [
                    RecentLearningContext(**{**r, "occurred_at": str(r["occurred_at"])})
                    for r in q.fetchall()
                ]
                q.execute(
                    "SELECT DISTINCT k.name,s.name subject_name FROM knowledge_occurrences o "
                    "JOIN learning_records r ON r.id=o.learning_record_id "
                    "AND r.family_id=o.family_id "
                    "JOIN knowledge_items k ON k.id=o.knowledge_item_id "
                    "AND k.family_id=o.family_id "
                    "JOIN subjects s ON s.id=k.subject_id AND s.family_id=k.family_id "
                    "WHERE r.family_id=%s AND r.child_id=%s AND r.submission_id=%s LIMIT 201",
                    (family, child, row["id"]),
                )
                reference = {
                    (r["subject_name"], normalize_knowledge_name(r["name"])) for r in q.fetchall()
                }
                cases.append(
                    dict(
                        alias=f"case{number:02}",
                        source_digest=sha256(row["id"].encode()).hexdigest(),
                        original_failed=row["state"] == "failed",
                        data=AnalysisInput(
                            text=row["input_text"],
                            grade=grade,
                            image_paths=paths,
                            occurred_at=str(row["occurred_at"]),
                            analysis_subjects=subjects,
                            recent_learning=recent,
                        ),
                        history=[ExistingKnowledgeContext(**h) for h in history],
                        reference=reference,
                    )
                )
    finally:
        connection.rollback()
        connection.close()
    manifest = directory / "downloads.json"
    manifest.write_text(json.dumps(downloads), encoding="utf-8")
    os.chmod(manifest, 0o600)
    result = subprocess.run(
        ["node", str(ROOT / "tools/download_replay_media.cjs"), str(manifest)],
        capture_output=True,
        timeout=max(30, len(downloads) * 20),
    )
    if result.returncode:
        # Never forward SDK stderr: it can contain credentials, URLs or material paths.
        print("read_only_media_download_failed", file=sys.stderr)
        raise RuntimeError("media_download_failed")
    return cases


def run_case(case, arm, settings):
    data = case["data"].model_copy(deep=True)
    counts = Counter()
    searched = set()

    def search(request):
        counts["queries"] += 1
        if counts["queries"] > 20:
            raise AnalysisOutputValidationError(["history_search.tool_budget"])
        searched.add((request.subject_name, normalize_knowledge_name(request.candidate_key)))
        terms = {t for t, _ in knowledge_search_terms(request.candidate_key)}
        ranked = sorted(
            (h for h in case["history"] if h.subject_name == request.subject_name),
            key=lambda h: len(terms & {t for t, _ in knowledge_search_terms(h.name)}),
            reverse=True,
        )
        rows = [h for h in ranked if terms & {t for t, _ in knowledge_search_terms(h.name)}][:20]
        known = {h.knowledge_id for h in data.existing_knowledge}
        data.existing_knowledge.extend(h for h in rows if h.knowledge_id not in known)
        return [h.model_dump() for h in rows]

    started = monotonic()
    try:
        if arm in {"A", "B"}:
            provider = ArkAnalysisProvider(settings)
            original = provider.client.responses.create

            def create(**kwargs):
                counts["requests"] += 1
                if arm == "B":
                    kwargs.update(
                        max_output_tokens=8192,
                        extra_body={
                            **kwargs.get("extra_body", {}),
                            "thinking": {"type": "disabled"},
                        },
                    )
                response = original(**kwargs)
                if response.usage:
                    counts["input_tokens"] += response.usage.input_tokens
                    counts["output_tokens"] += response.usage.output_tokens
                    details = response.usage.output_tokens_details
                    counts["reasoning_tokens"] += details.reasoning_tokens if details else 0
                return response

            provider.client.responses.create = create

            def validate_final(proposal):
                if any(
                    (p.subject_name or proposal.subject_name, normalize_knowledge_name(p.name))
                    not in searched
                    for p in proposal.knowledge_points
                ):
                    raise AnalysisOutputValidationError(["history_search.incomplete"])
                return data.validate_proposal(proposal)

            try:
                proposal = provider.analyze_with_history(
                    data, search, max_turns=8, deadline=started + 270, validate_final=validate_final
                )
            finally:
                provider.client.close()
        else:
            provider = StagedArkProvider(
                settings.model_copy(update={"analysis_concurrency": 1 if arm == "C" else 2})
            )

            class Metrics:
                def info(self, event, **fields):
                    if event == "analysis_stage_completed":
                        counts["requests"] += 1
                        for k in ("input_tokens", "output_tokens", "reasoning_tokens"):
                            counts[k] += fields.get(k) or 0

                def warning(self, *args, **kwargs):
                    pass

            proposal = asyncio.run(
                StagedPipeline(provider, Metrics()).run(data, search, started + 270)
            )
        proposal = data.validate_proposal(proposal)
        points = {
            (p.subject_name or proposal.subject_name, normalize_knowledge_name(p.name))
            for p in proposal.knowledge_points
        }
        points.update(
            (p.subject_name, normalize_knowledge_name(p.knowledge_name))
            for p in proposal.todo_matches
        )
        result = dict(
            success=True,
            points=len(points),
            reference_points=len(case["reference"]),
            lexical_overlap=len(points & case["reference"]),
            evidence_count=sum(len(p.direct_evidence) for p in proposal.knowledge_points),
        )
    except Exception as exc:
        disposition = analysis_failure_disposition(exc)
        result = dict(success=False, reason=disposition.reason, code=disposition.code)
    return dict(
        case=case["alias"],
        arm=arm,
        images=len(data.image_paths),
        original_failed=case["original_failed"],
        seconds=round(monotonic() - started, 2),
        **counts,
        **result,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--job-id", required=True)
    parser.add_argument("--samples", type=int, default=12, choices=range(1, 65))
    parser.add_argument("--repeats", type=int, default=3, choices=range(1, 4))
    parser.add_argument("--arms", default="ABCD")
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()
    if not set(args.arms) <= set("ABCD"):
        parser.error("unknown arm")
    logging.disable(logging.CRITICAL)
    settings = Settings()
    results = []
    args.report.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="push-kids-historical-replay-") as temporary:
        cases = snapshot(args.job_id, args.samples, Path(temporary))
        manifest = {c["alias"]: c["source_digest"] for c in cases}
        implementation = sha256(
            b"".join(
                (ROOT / "apps/api/src/push_kids/agent_processing" / p).read_bytes()
                for p in ["pipeline.py", "stage_provider.py", "stage_contracts.py", "providers.py"]
            )
        ).hexdigest()
        if args.resume:
            previous = json.loads(args.report.read_text())
            if (
                previous.get("sample_manifest") != manifest
                or previous.get("implementation") != implementation
            ):
                raise ValueError("resume_manifest_or_implementation_changed")
            results = previous["results"]
        completed = {(r["case"], r["arm"], r["repeat"]) for r in results}
        print(
            json.dumps(
                {"selected": len(cases), "images": sum(len(c["data"].image_paths) for c in cases)}
            ),
            flush=True,
        )
        for repeat in range(args.repeats):
            for case in cases:
                arms = args.arms[repeat % len(args.arms) :] + args.arms[: repeat % len(args.arms)]
                for arm in arms:
                    if (case["alias"], arm, repeat + 1) in completed:
                        continue
                    result = run_case(case, arm, settings)
                    result["repeat"] = repeat + 1
                    results.append(result)
                    args.report.write_text(
                        json.dumps(
                            {
                                "model": settings.ark_model,
                                "pipeline_revision": PIPELINE_REVISION,
                                "sample_manifest": manifest,
                                "implementation": implementation,
                                "observation_unit": "one pipeline attempt; no durable retries",
                                "scope": "read-only; no production writes; no current Todo state; "
                                "lexical references only",
                                "results": results,
                            },
                            ensure_ascii=False,
                            indent=2,
                        )
                        + "\n"
                    )
                    print(json.dumps(result), flush=True)


if __name__ == "__main__":
    main()
