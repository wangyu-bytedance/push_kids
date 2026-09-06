from __future__ import annotations

import argparse
import os
import sys

from push_kids.children.service import is_custom_subject
from push_kids.persistence.models import (
    Child,
    Family,
    FamilyMember,
    MemberRole,
    MemberStatus,
    Subject,
    WeChatActorBinding,
)
from push_kids.platform.config import Settings
from push_kids.platform.context import subject_hmac
from push_kids.platform.database import Database
from sqlalchemy import select


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="为一个微信用户创建或更新 staging 家庭档案；OpenID 只从环境变量读取。"
    )
    parser.add_argument("--openid-env", default="WECHAT_OPENID_TO_BIND")
    parser.add_argument("--family-id", required=True)
    parser.add_argument("--child-name", required=True)
    parser.add_argument("--grade", default="小学")
    parser.add_argument("--budget", type=int, default=15, choices=(10, 15, 20, 30))
    parser.add_argument("--learning", nargs="*", default=[])
    parser.add_argument("--activities", nargs="*", default=[])
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    settings = Settings()
    openid = os.environ.get(args.openid_env)
    if not openid:
        raise RuntimeError(f"环境变量 {args.openid_env} 未设置")
    if not settings.wechat_expected_app_id or not settings.actor_hmac_key:
        raise RuntimeError("WECHAT_APP_ID 或 PUSH_KIDS_ACTOR_HMAC_KEY 未设置")
    database = Database(settings)
    database.verify_cloud_schema()
    subject = subject_hmac(
        settings.actor_hmac_key.get_secret_value(), settings.wechat_expected_app_id, openid
    )
    with database.session_factory() as db:
        binding = db.scalar(
            select(WeChatActorBinding).where(
                WeChatActorBinding.app_id == settings.wechat_expected_app_id,
                WeChatActorBinding.subject_hmac == subject,
            )
        )
        if binding is None:
            binding = WeChatActorBinding(
                app_id=settings.wechat_expected_app_id,
                subject_hmac=subject,
                family_id=args.family_id,
            )
            db.add(binding)
            db.flush()
        else:
            binding.family_id = args.family_id
            binding.status = "active"
        family = db.get(Family, args.family_id)
        if family is None:
            family = Family(id=args.family_id, display_name=f"{args.child_name}的家")
            db.add(family)
            db.flush()
        member = db.scalar(select(FamilyMember).where(FamilyMember.actor_binding_id == binding.id))
        if member is None:
            db.add(
                FamilyMember(
                    family_id=args.family_id,
                    actor_binding_id=binding.id,
                    active_actor_binding_id=binding.id,
                    role=MemberRole.manager.value,
                    relationship_label="家庭管理员",
                )
            )
        else:
            member.family_id = args.family_id
            member.active_actor_binding_id = binding.id
            member.role = MemberRole.manager.value
            member.status = MemberStatus.active.value
        child = db.scalar(
            select(Child).where(Child.family_id == args.family_id, Child.name == args.child_name)
        )
        if child is None:
            child = Child(
                family_id=args.family_id,
                name=args.child_name,
                grade=args.grade,
                daily_budget_minutes=args.budget,
            )
            db.add(child)
            db.flush()
        else:
            child.grade = args.grade
            child.daily_budget_minutes = args.budget
        for kind, names in (("learning", args.learning), ("activity", args.activities)):
            for name in dict.fromkeys(item.strip() for item in names if item.strip()):
                item = db.scalar(
                    select(Subject).where(
                        Subject.family_id == args.family_id,
                        Subject.child_id == child.id,
                        Subject.name == name,
                    )
                )
                if item is None:
                    db.add(
                        Subject(
                            family_id=args.family_id,
                            child_id=child.id,
                            name=name,
                            kind=kind,
                            is_custom=is_custom_subject(name, kind),
                        )
                    )
                else:
                    item.kind = kind
                    item.active = True
        db.commit()
    print(f"CLOUD_FAMILY_PROVISIONED family={args.family_id} child={args.child_name}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except RuntimeError as exc:
        print(f"CLOUD_FAMILY_PROVISION_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
