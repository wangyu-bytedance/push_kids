from __future__ import annotations

import argparse
import json
import logging
import os
import re
from pathlib import Path
from statistics import median
from time import monotonic
from typing import TypedDict

from push_kids.agent_processing.contracts import AnalysisInput
from push_kids.agent_processing.providers import ArkAnalysisProvider
from push_kids.agent_processing.telemetry import AnalysisTrace
from push_kids.platform.config import Settings


class _Sample(TypedDict):
    mode: str
    run: int
    duration_ms: int
    turns: int
    cached_tokens: int | None


class _BenchmarkMetrics(logging.Handler):
    def __init__(self, job_id: str) -> None:
        super().__init__()
        self.job_id = job_id
        self.turns = 0
        self.cached_tokens = 0
        self.cached_tokens_reported = False

    def emit(self, record: logging.LogRecord) -> None:
        message = record.getMessage()
        if f"job_id={self.job_id}" not in message:
            return
        if message.startswith("analysis_generation_completed "):
            self.turns += 1
        match = re.search(r"(?:^| )cached_tokens=(\d+)(?: |$)", message)
        if match:
            self.cached_tokens += int(match.group(1))
            self.cached_tokens_reported = True


def _run_once(
    *,
    enabled: bool,
    run_number: int,
    text: str,
    image_paths: list[Path],
) -> _Sample:
    mode = "session" if enabled else "stateless"
    job_id = f"benchmark-{mode}-{run_number}"
    metrics = _BenchmarkMetrics(job_id)
    analysis_logger = logging.getLogger("push_kids.analysis")
    analysis_logger.addHandler(metrics)
    previous_level = analysis_logger.level
    analysis_logger.setLevel(logging.INFO)
    try:
        provider = ArkAnalysisProvider(
            Settings(
                PUSH_KIDS_AI_PROVIDER="ark",
                ARK_CONTEXT_CACHE_ENABLED=enabled,
            )
        )
        started = monotonic()
        provider.analyze_with_history(
            AnalysisInput(
                text=text,
                image_paths=image_paths,
                existing_subjects=["语文", "数学", "英语"],
            ),
            lambda _request: [],
            max_turns=8,
            trace=AnalysisTrace(job_id=job_id, attempt=1),
        )
        duration_ms = int((monotonic() - started) * 1000)
    finally:
        analysis_logger.removeHandler(metrics)
        analysis_logger.setLevel(previous_level)
    return {
        "mode": mode,
        "run": run_number,
        "duration_ms": duration_ms,
        "turns": metrics.turns,
        "cached_tokens": metrics.cached_tokens if metrics.cached_tokens_reported else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Secret-safe paired Ark context-session latency benchmark"
    )
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--image", type=Path)
    parser.add_argument("--text", default="数学学习了两位数进位加法")
    args = parser.parse_args()
    if not 1 <= args.runs <= 10:
        raise SystemExit("--runs must be between 1 and 10")
    if not os.getenv("ARK_API_KEY"):
        raise SystemExit("ARK_API_KEY is not configured; benchmark skipped")
    image_paths = [args.image] if args.image else []
    if any(not path.exists() for path in image_paths):
        raise SystemExit("image path does not exist")

    samples: list[_Sample] = []
    try:
        for run_index in range(args.runs):
            # Alternate order so provider warming or implicit caching cannot always favor one mode.
            order = (False, True) if run_index % 2 == 0 else (True, False)
            for enabled in order:
                sample = _run_once(
                    enabled=enabled,
                    run_number=run_index + 1,
                    text=args.text,
                    image_paths=image_paths,
                )
                samples.append(sample)
                print(json.dumps(sample, ensure_ascii=False, sort_keys=True))
    except Exception as exc:
        raise SystemExit(f"benchmark failed: {type(exc).__name__}") from None

    durations = {
        mode: [sample["duration_ms"] for sample in samples if sample["mode"] == mode]
        for mode in ("stateless", "session")
    }
    stateless_median = median(durations["stateless"])
    session_median = median(durations["session"])
    summary = {
        "runs_per_mode": args.runs,
        "stateless_median_ms": stateless_median,
        "session_median_ms": session_median,
        "session_change_percent": round(
            (session_median - stateless_median) / stateless_median * 100,
            2,
        ),
        "negative_change_means_session_faster": True,
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))


if __name__ == "__main__":
    main()
