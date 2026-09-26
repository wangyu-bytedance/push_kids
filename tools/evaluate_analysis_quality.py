#!/usr/bin/env python3
"""Run the fixed, deidentified 40-case live Ark proposal-quality gate."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from push_kids.agent_processing.contracts import AnalysisProposal  # noqa: E402
from push_kids.agent_processing.providers import ArkAnalysisProvider  # noqa: E402
from push_kids.agent_processing.worker import AnalysisWorker  # noqa: E402
from push_kids.learning.service import LearningService  # noqa: E402
from push_kids.media.store import LocalMediaStore  # noqa: E402
from push_kids.persistence.models import (  # noqa: E402
    AgentJob,
    Child,
    JobState,
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    LearningSubmission,
    ReviewFeedback,
    ReviewItem,
    Subject,
    SubmissionMedia,
    SubmissionState,
)
from push_kids.platform.config import Settings  # noqa: E402
from push_kids.platform.database import Database  # noqa: E402
from push_kids.platform.time import utcnow  # noqa: E402
from sqlalchemy import func, select  # noqa: E402

PRESETS = ["语文", "数学", "英语"]
EVALUATION_FAMILY_ID = "analysis-quality-evaluation"
OPERATIONAL_FAILURE_CODES = frozenset({"analysis_failed"})


@dataclass(frozen=True)
class CaseResult:
    case_id: str
    expected: frozenset[str]
    failure_code: str | None
    attempts: int


def _font(size: int) -> ImageFont.FreeTypeFont:
    candidates = (
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
    )
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    raise RuntimeError("quality_fixture_font_unavailable")


def _render_fixture(case_id: str, material: str, directory: Path) -> Path:
    image = Image.new("RGB", (1280, 800), "white")
    draw = ImageDraw.Draw(image)
    font = _font(42)
    lines = [material[index : index + 28] for index in range(0, len(material), 28)]
    draw.multiline_text((80, 100), "\n".join(lines), fill="black", font=font, spacing=24)
    path = directory / f"{case_id}.png"
    image.save(path, format="PNG", optimize=True)
    return path


def _validate_cases(cases: list[dict[str, object]]) -> None:
    if len(cases) != 40 or len({str(item.get("id")) for item in cases}) != 40:
        raise ValueError("quality fixture must contain 40 unique cases")
    counts: Counter[str] = Counter()
    image_count = 0
    multi_count = 0
    for case in cases:
        subjects = case["subject"]
        if isinstance(subjects, str):
            counts[subjects] += 1
        else:
            multi_count += 1
        image_count += case["input_type"] == "image"
    if counts != Counter({"语文": 12, "数学": 12, "英语": 12}):
        raise ValueError("quality fixture must contain 12 cases per single subject")
    if multi_count != 4 or image_count < 30:
        raise ValueError("quality fixture requires 4 multi-subject and at least 30 image cases")


def _ordered_cases(cases: list[dict[str, object]]) -> list[dict[str, object]]:
    """Return the fixed cross-subject evaluation schedule.

    Input order is retained within each subject bucket, while the grouped fixture is
    transformed into a reproducible round-robin schedule. One multi-subject case is
    inserted after every three single-subject rounds.
    """
    single_subject = {
        subject: [case for case in cases if case["subject"] == subject] for subject in PRESETS
    }
    multi_subject = [case for case in cases if not isinstance(case["subject"], str)]
    if any(len(single_subject[subject]) != 12 for subject in PRESETS) or len(multi_subject) != 4:
        raise ValueError("quality fixture cannot produce the fixed evaluation schedule")

    ordered: list[dict[str, object]] = []
    for index in range(12):
        ordered.extend(single_subject[subject][index] for subject in PRESETS)
        if (index + 1) % 3 == 0:
            ordered.append(multi_subject[index // 3])
    return ordered


def _build_report(
    results: list[CaseResult],
    *,
    empty_pending_count: int,
    remaining_pending_count: int,
    formal_write_count: int,
) -> dict[str, object]:
    """Aggregate the availability and semantic quality gates without case content."""
    passed = sum(result.failure_code is None for result in results)
    semantic_passed: Counter[str] = Counter()
    semantic_total: Counter[str] = Counter()
    operational_codes: Counter[str] = Counter()
    failures: list[dict[str, object]] = []

    for result in results:
        if result.failure_code is not None:
            failures.append(
                {
                    "case_id": result.case_id,
                    "code": result.failure_code,
                    "attempts": result.attempts,
                }
            )
        if result.failure_code in OPERATIONAL_FAILURE_CODES:
            operational_codes[result.failure_code] += 1
            continue
        for subject in result.expected:
            semantic_total[subject] += 1
            if result.failure_code is None:
                semantic_passed[subject] += 1

    subject_semantic = {
        subject: {
            "passed": semantic_passed[subject],
            "total": semantic_total[subject],
            "rate": round(
                semantic_passed[subject] / semantic_total[subject],
                4,
            )
            if semantic_total[subject]
            else 0.0,
        }
        for subject in PRESETS
    }
    subject_rates = {subject: subject_semantic[subject]["rate"] for subject in PRESETS}
    overall_rate = round(passed / len(results), 4) if results else 0.0
    gate_passed = (
        bool(results)
        and passed * 100 >= len(results) * 95
        and all(
            subject_semantic[subject]["total"] > 0 and subject_semantic[subject]["rate"] >= 0.9
            for subject in PRESETS
        )
        and empty_pending_count == 0
        and remaining_pending_count == 0
        and formal_write_count == 0
    )
    return {
        "status": "passed" if gate_passed else "failed",
        "case_count": len(results),
        "passed": passed,
        "overall_rate": overall_rate,
        "end_to_end": {
            "passed": passed,
            "total": len(results),
            "rate": overall_rate,
        },
        "operational_failure_count": sum(operational_codes.values()),
        "operational_failure_codes": dict(sorted(operational_codes.items())),
        "subject_rates": subject_rates,
        "subject_semantic": subject_semantic,
        "empty_pending_count": empty_pending_count,
        "remaining_pending_count": remaining_pending_count,
        "formal_write_count": formal_write_count,
        "failures": failures,
    }


def _score(proposal: AnalysisProposal, expected: set[str]) -> str | None:
    if not proposal.knowledge_points and not proposal.todo_matches:
        return "proposal.actionable_items"
    if any(not point.direct_evidence for point in proposal.knowledge_points):
        return "evidence.missing"
    represented = {
        point.subject_name or proposal.subject_name for point in proposal.knowledge_points
    } | {item.subject_name for item in proposal.todo_matches if item.subject_name}
    if represented != expected:
        return "subject.mismatch"
    return None


def _seed_case(
    database: Database,
    case: dict[str, object],
    media_directory: Path,
) -> str:
    case_id = str(case["id"])
    material = str(case["material"])
    with database.session_factory() as db:
        child = Child(
            family_id=EVALUATION_FAMILY_ID,
            name=f"评测-{case_id}",
            grade="三年级",
        )
        db.add(child)
        db.flush()
        db.add_all(
            [
                Subject(
                    family_id=EVALUATION_FAMILY_ID,
                    child_id=child.id,
                    name=name,
                    kind="learning",
                    is_custom=False,
                )
                for name in ("语文", "数学")
            ]
        )
        is_image = case["input_type"] == "image"
        submission = LearningSubmission(
            family_id=EVALUATION_FAMILY_ID,
            child_id=child.id,
            occurred_at=utcnow(),
            input_text=None if is_image else material,
            source="photo" if is_image else "manual",
            state=SubmissionState.queued.value,
        )
        db.add(submission)
        db.flush()
        db.add(
            AgentJob(
                family_id=EVALUATION_FAMILY_ID,
                submission_id=submission.id,
                state=JobState.queued.value,
                available_at=utcnow(),
                max_attempts=3,
            )
        )
        if is_image:
            image_path = _render_fixture(case_id, material, media_directory)
            db.add(
                SubmissionMedia(
                    submission_id=submission.id,
                    path=str(image_path),
                    content_type="image/png",
                    byte_size=image_path.stat().st_size,
                    sort_order=1,
                )
            )
        db.commit()
        return str(submission.id)


def _process_case(
    database: Database,
    worker: AnalysisWorker,
    media_store: LocalMediaStore,
    submission_id: str,
    expected: set[str],
) -> tuple[str | None, int, bool]:
    """Drive durable worker retries, score its stored result, then cancel it."""
    failure_code: str | None = "analysis_failed"
    attempts = 0
    empty_pending = False
    for _ in range(3):
        if not worker.process_one():
            failure_code = "worker.no_runnable_job"
            break
        with database.session_factory() as db:
            submission = db.get(LearningSubmission, submission_id)
            job = db.scalar(select(AgentJob).where(AgentJob.submission_id == submission_id))
            if submission is None or job is None:
                failure_code = "worker.state_missing"
                break
            attempts = int(job.attempts or 0)
            if submission.state == SubmissionState.queued.value:
                job.available_at = utcnow()
                db.commit()
                continue
            if submission.state in (
                SubmissionState.pending_confirmation.value,
                SubmissionState.failed.value,
            ):
                break

    with database.session_factory() as db:
        submission = db.get(LearningSubmission, submission_id)
        job = db.scalar(select(AgentJob).where(AgentJob.submission_id == submission_id))
        if submission is not None and job is not None:
            attempts = int(job.attempts or 0)
            if submission.state == SubmissionState.pending_confirmation.value:
                try:
                    proposal = AnalysisProposal.model_validate_json(submission.proposal_json or "")
                except Exception:
                    failure_code = "proposal.stored_invalid"
                else:
                    empty_pending = not proposal.knowledge_points and not proposal.todo_matches
                    failure_code = _score(proposal, expected)
            elif submission.state == SubmissionState.failed.value:
                failure_code = submission.error_code or "analysis_failed"
            else:
                failure_code = f"worker.unexpected_state.{submission.state}"
            LearningService.cancel(
                db,
                media_store,
                EVALUATION_FAMILY_ID,
                submission_id,
            )
    return failure_code, attempts, empty_pending


def _formal_write_count(database: Database) -> int:
    models = (
        LearningRecord,
        KnowledgeItem,
        KnowledgeOccurrence,
        ReviewItem,
        ReviewFeedback,
    )
    with database.session_factory() as db:
        return sum(int(db.scalar(select(func.count(model.id))) or 0) for model in models)


def _pending_count(database: Database) -> int:
    with database.session_factory() as db:
        return int(
            db.scalar(
                select(func.count(LearningSubmission.id)).where(
                    LearningSubmission.state == SubmissionState.pending_confirmation.value
                )
            )
            or 0
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, required=True)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    cases = json.loads(args.cases.read_text(encoding="utf-8"))
    _validate_cases(cases)

    settings = Settings()
    if not settings.ark_api_key or not settings.ark_api_key.get_secret_value().strip():
        result = {"status": "not_run", "reason": "ark_api_key_missing", "case_count": 40}
        print(json.dumps(result, separators=(",", ":")))
        return 2

    provider = ArkAnalysisProvider(settings)
    results: list[CaseResult] = []
    empty_pending_count = 0
    with tempfile.TemporaryDirectory(prefix="push-kids-quality-") as temporary:
        directory = Path(temporary)
        media_directory = directory / "media"
        media_directory.mkdir(parents=True)
        evaluation_settings = settings.model_copy(
            update={
                "env": "test",
                "database_url": f"sqlite:///{directory / 'quality.db'}",
                "media_root": media_directory,
                "media_backend": "local",
            }
        )
        database = Database(evaluation_settings)
        database.create_schema()
        media_store = LocalMediaStore(media_directory, settings.upload_max_bytes)
        worker = AnalysisWorker(database, provider, media_store)

        for case in _ordered_cases(cases):
            case_id = str(case["id"])
            subjects = case["subject"]
            expected = {subjects} if isinstance(subjects, str) else set(subjects)
            submission_id = _seed_case(database, case, media_directory)
            failure_code, attempts, empty_pending = _process_case(
                database,
                worker,
                media_store,
                submission_id,
                expected,
            )
            empty_pending_count += int(empty_pending)
            results.append(
                CaseResult(
                    case_id=case_id,
                    expected=frozenset(expected),
                    failure_code=failure_code,
                    attempts=attempts,
                )
            )

        formal_write_count = _formal_write_count(database)
        remaining_pending_count = _pending_count(database)

    report = _build_report(
        results,
        empty_pending_count=empty_pending_count,
        remaining_pending_count=remaining_pending_count,
        formal_write_count=formal_write_count,
    )
    encoded = json.dumps(report, ensure_ascii=False, separators=(",", ":"))
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(encoded + os.linesep, encoding="utf-8")
    print(encoded)
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
