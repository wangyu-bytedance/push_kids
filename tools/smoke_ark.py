from __future__ import annotations

import argparse
import os
from pathlib import Path

from push_kids.agent_processing.contracts import AnalysisInput
from push_kids.agent_processing.providers import ArkAnalysisProvider
from push_kids.platform.config import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Secret-safe Ark provider smoke test")
    parser.add_argument("--image", type=Path)
    parser.add_argument("--text", default="数学学习了两位数进位加法")
    args = parser.parse_args()
    if not os.getenv("ARK_API_KEY"):
        raise SystemExit("ARK_API_KEY is not configured; smoke test skipped")
    images = [args.image] if args.image else []
    if any(not path.exists() for path in images):
        raise SystemExit("image path does not exist")
    result = ArkAnalysisProvider(Settings(PUSH_KIDS_AI_PROVIDER="ark")).analyze(
        AnalysisInput(text=args.text, image_paths=images)
    )
    print(
        {
            "ok": True,
            "subject": result.subject_name,
            "knowledge_point_count": len(result.knowledge_points),
            "todo_match_count": len(result.todo_matches),
        }
    )


if __name__ == "__main__":
    main()
