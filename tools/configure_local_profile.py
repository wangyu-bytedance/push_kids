from __future__ import annotations

import argparse
import sys

import httpx


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="通过本地 API 配置真实家庭档案；不会生成示例学习记录。"
    )
    parser.add_argument("--api", default="http://127.0.0.1:8011/api/v1")
    parser.add_argument("--family-id", default="local-family")
    parser.add_argument("--child-name", required=True)
    parser.add_argument("--grade", default="小学")
    parser.add_argument("--budget", type=int, default=15, choices=(10, 15, 20, 30))
    parser.add_argument("--learning", nargs="*", default=[])
    parser.add_argument("--activities", nargs="*", default=[])
    return parser.parse_args()


def ensure_success(response: httpx.Response) -> dict | list:
    if response.is_success:
        return response.json()
    try:
        message = response.json()["error"]["message"]
    except (KeyError, TypeError, ValueError):
        message = response.text
    raise RuntimeError(f"API {response.status_code}: {message}")


def main() -> int:
    args = parse_args()
    headers = {"X-Family-ID": args.family_id}
    with httpx.Client(base_url=args.api, headers=headers, timeout=10) as client:
        children = ensure_success(client.get("/children"))
        assert isinstance(children, list)
        child = next((item for item in children if item["name"] == args.child_name), None)
        if child is None:
            child = ensure_success(
                client.post(
                    "/children",
                    json={
                        "name": args.child_name,
                        "grade": args.grade,
                        "daily_budget_minutes": args.budget,
                    },
                )
            )
        else:
            child = ensure_success(
                client.patch(
                    f"/children/{child['id']}",
                    json={"grade": args.grade, "daily_budget_minutes": args.budget},
                )
            )
        assert isinstance(child, dict)
        subjects = ensure_success(client.get(f"/children/{child['id']}/subjects"))
        assert isinstance(subjects, list)
        by_key = {(item["name"], item["kind"]): item for item in subjects}
        for kind, names in (("learning", args.learning), ("activity", args.activities)):
            for name in dict.fromkeys(item.strip() for item in names if item.strip()):
                existing = by_key.get((name, kind))
                if existing is None:
                    ensure_success(
                        client.post(
                            "/subjects",
                            json={"child_id": child["id"], "name": name, "kind": kind},
                        )
                    )
                elif not existing["active"]:
                    ensure_success(
                        client.patch(f"/subjects/{existing['id']}", json={"active": True})
                    )
    print(f"PROFILE_CONFIGURED family={args.family_id} child={args.child_name}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (httpx.HTTPError, RuntimeError) as exc:
        print(f"PROFILE_CONFIGURATION_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
