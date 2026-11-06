#!/usr/bin/env python3
"""Dry-run or apply the approved historical Knowledge cleanup without printing child content."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from dataclasses import asdict, dataclass
from pathlib import Path

from dotenv import dotenv_values
from sqlalchemy import func, select

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "apps" / "api" / "src"))

from push_kids.knowledge.maintenance import (  # noqa: E402
    KnowledgeRepairCluster,
    KnowledgeRepairConflict,
    apply_repair_cluster,
)
from push_kids.persistence.models import (  # noqa: E402
    KnowledgeItem,
    KnowledgeOccurrence,
    LearningRecord,
    ReviewFeedback,
    Subject,
)
from push_kids.platform.config import Settings  # noqa: E402
from push_kids.platform.database import Database  # noqa: E402

SPEC_REVISION = "SPEC-20261031-HISTORICAL-KNOWLEDGE-CLEANUP-01"


@dataclass(frozen=True)
class Rule:
    alias: str
    subject: str
    target: str
    sources: tuple[str, ...]


RULES = (
    Rule(
        "math_mixed_application",
        "数学",
        "加减法混合运算应用题",
        (
            "加减混合运算解决年龄问题",
            "看图列加减混合算式解决小鸟数量问题（算式为□+□-□=□）",
            "用加减混合解决上下车后求现有人数的实际问题",
            "认识加减混合运算，结合小鸟情境计算加减混合算式",
        ),
    ),
    Rule(
        "math_classification",
        "数学",
        "物体的分类与分类标准",
        ("按不同标准对物体分类", "识别不同类物品"),
    ),
    Rule(
        "math_clock",
        "数学",
        "钟表的认识与时刻认读",
        ("认识钟表与时刻认读", "认识时钟并识别时针"),
    ),
    Rule(
        "math_segments",
        "数学",
        "线段的定义、识别与数量计算",
        (
            "数组合/复杂图形（交叉、梯形、方格、菱形、多线段组合）中的线段条数",
            "数同一直线上分点构成的线段条数",
            "线段概念辨析判断（标注是/不是线段）",
            "数简单图形（六边形、带横线长方形、梯形、圆加线段等）中的线段条数",
            "按要求连点后数连线形成图形的线段总数（含带对角线四边形、顶点连底边多点图形）",
            "先数图中原有线段，再添画/画线段使总数达到指定条数（14条、3条）",
            "数各类图形中的线段条数：含简单平面图形、带分点直线、组合图形",
        ),
    ),
    Rule(
        "math_compare_chains",
        "数学",
        "10以内连加、连减算式结果的大小比较",
        ("比较10以内连加算式结果与数的大小，填>、<或=", "比较10以内连减算式结果与数的大小"),
    ),
    Rule(
        "math_part_whole",
        "数学",
        "用减法解决部分与整体关系的应用题",
        (
            "根据总数和部分数量看图列连减算式求未知部分",
            "用减法解决已知总数和一部分求另一部分的实际问题",
        ),
    ),
    Rule(
        "math_repeated_addition",
        "数学",
        "连加运算应用题",
        ("根据情境图看图列连加算式，求总数", "用连加解决多次购买后求总数的实际问题"),
    ),
    Rule(
        "english_j",
        "英语",
        "字母Jj的字母名、字母音及相关词汇",
        ("小写英文字母j", "jar", "juice", "jellyfish"),
    ),
    Rule(
        "english_n",
        "英语",
        "字母Nn的字母名、字母音及相关词汇",
        (
            "按笔顺描摹书写大写字母N和小写字母n",
            "听、指并跟读字母Nn相关单词nine、newt、nut",
            "听并跟读字母Nn",
            "认读英文字母Nn的字母名与字母音",
        ),
    ),
    Rule(
        "english_lm",
        "英语",
        "字母Ll、Mm的字母名、字母音及相关词汇",
        (
            "认读英文字母Ll、Mm的字母名和字母音",
            "认读以Ll、Mm开头的目标英语词汇：leaf、ladybug、milk、mango",
        ),
    ),
    Rule(
        "english_o",
        "英语",
        "字母Oo的字母名、字母音及相关词汇",
        ("认读字母Oo的字母名与字母音", "认读以Oo开头的on、orange、octopus三个目标词汇"),
    ),
    Rule(
        "english_happy_outing",
        "英语",
        "《A Happy Outing》阅读理解与表达",
        (
            "朗读并表演英文短文《A Happy Outing》",
            "阅读英语短文《A Happy Outing》，理解秋游出行、去动物园、野餐分享、"
            "表达开心的相关图文内容",
        ),
    ),
    Rule(
        "english_word_list",
        "英语",
        "指定英语词汇的认读与词义理解",
        (
            "认读think、fireworks、silk、hockey、tennis、pumpkin、baseball、blackboard、funny、duty、girl、teacher、friend",
            "识记英语单词think、fireworks、silk、hockey、tennis、pumpkin、baseball、blackboard、funny、duty、girl、teacher",
        ),
    ),
    Rule(
        "chinese_onomatopoeia",
        "语文",
        "拟声词的认识与运用",
        ("常见拟声词的认识与运用", "常用拟声词的认识与运用"),
    ),
    Rule(
        "chinese_grip",
        "语文",
        "正确握笔姿势",
        ("掌握正确握笔姿势", "正确握笔姿势练习"),
    ),
    Rule(
        "chinese_ie_ue_er",
        "语文",
        "复韵母ie、üe、er的认读与拼读",
        ("练习ie、üe与声母的拼音拼读", "认读复韵母ie、üe、er"),
    ),
    Rule(
        "chinese_adjective_collocation",
        "语文",
        "形容词与事物的搭配",
        ("照样子写“弯弯的”搭配的事物词语", "照样子给指定事物搭配合适形容词写短语"),
    ),
    Rule(
        "chinese_synonyms_antonyms",
        "语文",
        "近义词和反义词的概念、判断与运用",
        (
            "识记带拼音的常见两字反义词：成功—失败、喜欢—讨厌",
            "识别成语左思右想、千言万语中的近义字",
            "认识反义词的定义与特点（意思相反或相对、字数相同），示例高/矮、开心/难过",
            "识记带拼音的常见单字反义词：男—女、南—北、开—关、正—反",
            "认识近义词的定义、含义与判断要点（意思相近、字数相同）",
            "连线匹配近义词：美丽、容易、方法对应好看、简单、办法",
            "识记带拼音的常见近义词配对：特别—非常、美丽—好看、容易—简单、方法—办法、赶紧—赶快",
            "选序号给单字闭、沉搭配近义词（选项①重、②关）",
        ),
    ),
)

UNRESOLVED_NAMES = (
    "拼音",
    "进行词语相关学习",
    "田字格书写指定汉字",
    "在括号内书写指定词语",
    "识记Unit5 Lovely faces主题词汇与常用句子",
    "识记Unit6 My family主题词汇与常用句子",
    "识记Unit7 Animals in our lives主题词汇与常用句子",
    "中国发明",
    "听读介绍Bossaball运动的英语短文",
)


def _database(production_admin_dotenv: bool) -> Database:
    if not production_admin_dotenv:
        return Database(Settings())
    config = dotenv_values(ROOT / ".env")
    host, _, port = str(config.get("MYSQL_ADMIN_ADDRESS") or "").rpartition(":")
    if not host or not port:
        raise RuntimeError("production_admin_configuration_missing")
    from urllib.parse import quote_plus

    url = (
        "mysql+pymysql://"
        f"{quote_plus(str(config['MYSQL_ADMIN_USERNAME']))}:"
        f"{quote_plus(str(config['MYSQL_ADMIN_PASSWORD']))}@{host}:{port}/push_kids?charset=utf8mb4"
    )
    return Database(Settings(PUSH_KIDS_DATABASE_URL=url))


def _plan(db) -> tuple[list[KnowledgeRepairCluster], int]:
    clusters: list[KnowledgeRepairCluster] = []
    for rule in RULES:
        rows = list(
            db.execute(
                select(KnowledgeItem, Subject)
                .join(Subject, Subject.id == KnowledgeItem.subject_id)
                .where(
                    Subject.kind == "learning",
                    Subject.name == rule.subject,
                    KnowledgeItem.review_status == "normal",
                    KnowledgeItem.name.in_(rule.sources),
                )
                .order_by(
                    KnowledgeItem.family_id,
                    KnowledgeItem.child_id,
                    KnowledgeItem.created_at,
                    KnowledgeItem.id,
                )
            ).all()
        )
        scopes: dict[tuple[str, str, str], list[KnowledgeItem]] = {}
        for knowledge, subject in rows:
            scopes.setdefault((knowledge.family_id, knowledge.child_id, subject.id), []).append(
                knowledge
            )
        for (family_id, child_id, subject_id), items in scopes.items():
            if len(items) < 2 or {item.name for item in items} != set(rule.sources):
                continue
            canonical, *duplicates = items
            clusters.append(
                KnowledgeRepairCluster(
                    family_id=family_id,
                    child_id=child_id,
                    subject_id=subject_id,
                    canonical_id=canonical.id,
                    canonical_old_name=canonical.name,
                    target_name=rule.target,
                    duplicate_ids=tuple(item.id for item in duplicates),
                    duplicate_old_names=tuple(item.name for item in duplicates),
                )
            )
    unresolved = int(
        db.scalar(
            select(func.count())
            .select_from(KnowledgeItem)
            .where(
                KnowledgeItem.review_status == "normal",
                KnowledgeItem.name.in_(UNRESOLVED_NAMES),
            )
        )
        or 0
    )
    return clusters, unresolved


def _digest(clusters: list[KnowledgeRepairCluster]) -> str:
    payload = {
        "spec_revision": SPEC_REVISION,
        "clusters": [asdict(cluster) for cluster in clusters],
    }
    return hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def _fact_counts(db) -> dict[str, int]:
    return {
        "learning_records": int(db.scalar(select(func.count()).select_from(LearningRecord)) or 0),
        "knowledge_occurrences": int(
            db.scalar(select(func.count()).select_from(KnowledgeOccurrence)) or 0
        ),
        "review_feedback": int(db.scalar(select(func.count()).select_from(ReviewFeedback)) or 0),
        "knowledge_items": int(db.scalar(select(func.count()).select_from(KnowledgeItem)) or 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--production-admin-dotenv", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--approved-digest")
    args = parser.parse_args()
    database = _database(args.production_admin_dotenv)
    with database.session_factory() as db:
        clusters, unresolved = _plan(db)
        digest = _digest(clusters)
        before = _fact_counts(db)
        if not args.apply:
            db.rollback()
            print(
                json.dumps(
                    {
                        "spec_revision": SPEC_REVISION,
                        "mode": "dry_run",
                        "digest": digest,
                        "clusters": len(clusters),
                        "renames": len(clusters),
                        "supersessions": sum(len(item.duplicate_ids) for item in clusters),
                        "unresolved": unresolved,
                        "fact_counts": before,
                    },
                    sort_keys=True,
                )
            )
            return
        if not args.approved_digest or args.approved_digest != digest:
            raise KnowledgeRepairConflict("approved_digest_mismatch")
        if os.environ.get("PUSH_KIDS_KNOWLEDGE_BACKUP_CONFIRMED") != SPEC_REVISION:
            raise KnowledgeRepairConflict("backup_confirmation_missing")
        for cluster in clusters:
            apply_repair_cluster(db, cluster)
        after = _fact_counts(db)
        if after != before:
            raise KnowledgeRepairConflict("formal_fact_count_changed")
        db.commit()
        print(
            json.dumps(
                {
                    "spec_revision": SPEC_REVISION,
                    "mode": "applied",
                    "digest": digest,
                    "clusters": len(clusters),
                    "supersessions": sum(len(item.duplicate_ids) for item in clusters),
                    "unresolved": unresolved,
                    "fact_counts": after,
                },
                sort_keys=True,
            )
        )


if __name__ == "__main__":
    main()
