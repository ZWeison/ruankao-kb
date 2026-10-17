# -*- coding: utf-8 -*-
"""
论文范文缺口分析：
  论题清单（2016—2026 全部 13 期 × 4 = 52 个）vs 已归档范文（28 篇）

论题清单是权威侧的"应有什么"；范文是"已有什么"。
比对用「主题关键词」而非精确字符串 —— 因为论题措辞在各来源间有差异
（如「论软件系统架构评估」/「论软件系统架构评估及其应用」）。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ESSAY_DIR = ROOT / "03-论文范文"

# 2016—2026 全部论题（取自库内 01-真题-按年份/*/*-论文.md，与希赛网/LynnCen 交叉一致）
TOPICS: list[tuple[str, str, str]] = [
    ("2016-下半年", "论软件系统架构评估", "架构评估"),
    ("2016-下半年", "论软件设计模式及其应用", "设计模式"),
    ("2016-下半年", "论数据访问层设计技术及其应用", "数据库"),
    ("2016-下半年", "论微服务架构及其应用", "微服务"),
    ("2017-下半年", "论软件架构风格", "架构风格"),
    ("2017-下半年", "论软件系统建模方法及其应用", "UML"),
    ("2017-下半年", "论无服务器架构及其应用", "Serverless"),
    ("2017-下半年", "论软件质量保证及其应用", "测试与质量"),
    ("2018-下半年", "论软件开发过程 RUP 及其应用", "软件工程与过程"),
    ("2018-下半年", "论软件体系结构的演化", "架构演化"),
    ("2018-下半年", "论面向服务架构设计及其应用", "SOA"),
    ("2018-下半年", "论 NoSQL 数据库技术及其应用", "NoSQL"),
    ("2019-下半年", "论软件设计方法及其应用", "架构设计"),
    ("2019-下半年", "论软件系统架构评估及其应用", "架构评估"),
    ("2019-下半年", "论数据湖技术及其应用", "大数据"),
    ("2019-下半年", "论负载均衡技术在 Web 系统中的应用", "可靠性"),
    ("2020-下半年", "论数据分片技术及其应用", "数据库"),
    ("2020-下半年", "论云原生架构及其应用", "云原生"),
    ("2020-下半年", "论软件测试中缺陷管理及其应用", "测试与质量"),
    ("2020-下半年", "论企业集成架构设计及应用", "企业应用集成"),
    ("2021-下半年", "论面向方面的编程技术及其应用（AOP）", "架构设计"),
    ("2021-下半年", "论系统安全架构设计及其应用", "信息安全"),
    ("2021-下半年", "论企业集成平台的理解与应用", "企业应用集成"),
    ("2021-下半年", "论微服务架构及其应用", "微服务"),
    ("2022-下半年", "论基于构件的软件开发方法及其应用", "基于构件"),
    ("2022-下半年", "论软件维护方法及其应用", "软件可靠性"),
    ("2022-下半年", "论区块链技术及应用", "大数据"),
    ("2022-下半年", "论湖仓一体架构及其应用", "大数据"),
    ("2023-下半年", "论边缘计算及其应用", "边缘计算"),
    ("2023-下半年", "论多源数据集成及应用", "企业应用集成"),
    ("2023-下半年", "论面向对象的建模及应用", "UML"),
    ("2023-下半年", "论软件的可靠性评价", "软件可靠性"),
    ("2024-上半年", "论大数据Lambda架构", "大数据"),
    ("2024-上半年", "论模型驱动架构设计方法及其应用", "架构设计"),
    ("2024-上半年", "论单元测试方法及其应用", "测试与质量"),
    ("2024-上半年", "论云上自动化运维及其应用", "DevOps"),
    ("2024-下半年", "论分布式事务及其解决方案", "数据库"),
    ("2024-下半年", "论多元异构数据集成方法", "企业应用集成"),
    ("2024-下半年", "论软件维护及其应用", "软件可靠性"),
    ("2024-下半年", "论面向服务的架构设计", "SOA"),
    ("2025-上半年", "论负载均衡技术", "可靠性"),
    ("2025-上半年", "论软件测试方法及应用", "测试与质量"),
    ("2025-上半年", "论事件驱动架构", "架构风格"),
    ("2025-上半年", "论多模型数据库及应用", "数据库"),
    ("2025-下半年", "论无服务器架构", "Serverless"),
    ("2025-下半年", "论基于云原生数据库的企业信息系统架构", "云原生"),
    ("2025-下半年", "论系统性能测试技术及其应用", "测试与质量"),
    ("2025-下半年", "论秒杀场景及其技术解决方案", "容灾与高可用"),
    ("2026-上半年", "论向量数据库在项目中的应用", "数据库"),
    ("2026-上半年", "论高并发系统设计", "容灾与高可用"),
    ("2026-上半年", "论多模态大模型在移动智能测试框架中的应用", "人工智能"),
    ("2026-上半年", "论六边形架构的设计与应用", "架构设计"),
]


def main() -> int:
    # 收集已归档范文
    have: list[dict] = []
    for md in sorted(ESSAY_DIR.rglob("*.md")):
        if md.name.startswith("00-") or md.name == "README.md":
            continue
        t = md.read_text(encoding="utf-8")
        m = re.search(r"^论题: (.+)$", t, re.M)
        k = re.search(r"^范文类型: (.+)$", t, re.M)
        if not m:
            continue
        have.append({"topic": m.group(1).strip(),
                     "kind": (k.group(1).strip() if k else ""),
                     "path": str(md.relative_to(ROOT)).replace("\\", "/")})

    essays = [h for h in have if h["kind"] == "范文"]
    print(f"论题清单：{len(TOPICS)} 个（2016—2026，13 期 × 4）")
    print(f"已归档范文：{len(essays)} 篇（另有模板/提纲 {len(have) - len(essays)} 篇不计入）\n")

    # 用主题关键词做匹配：论题里含主题关键词，或与已有论题高度重合
    def covered(topic: str) -> dict | None:
        key = re.sub(r"[\s（）()]", "", topic)
        # 去掉"及其应用/及应用/与方法"等修饰再比
        core = re.sub(r"(及其应用|及应用|方法|的设计与应用|的应用与实现|的理解与应用|技术)$", "", key)
        for h in essays:
            hk = re.sub(r"[\s（）()]", "", h["topic"])
            hcore = re.sub(r"(及其应用|及应用|方法|的设计与应用|的应用与实现|的理解与应用|技术)$", "", hk)
            if not core or not hcore:
                continue
            if core == hcore or core in hcore or hcore in core:
                return h
            if len(core) >= 5 and len(hcore) >= 5 and (core[:6] == hcore[:6]):
                return h
        return None

    missing: list[tuple[str, str, str]] = []
    got: list[tuple[str, str, str, str]] = []
    for period, topic, theme in TOPICS:
        hit = covered(topic)
        if hit:
            got.append((period, topic, theme, hit["path"]))
        else:
            missing.append((period, topic, theme))

    print("=" * 72)
    print(f"✅ 已覆盖 {len(got)} / {len(TOPICS)}")
    print("=" * 72)
    for period, topic, theme, path in got:
        print(f"  [{period}] {topic}")
        print(f"        → {path}")
    print()
    print("=" * 72)
    print(f"❌ 缺失 {len(missing)} / {len(TOPICS)}")
    print("=" * 72)
    cur = None
    by_period: dict[str, list] = {}
    for period, topic, theme in missing:
        by_period.setdefault(period, []).append((topic, theme))
    # 按考期顺序输出（去重）
    seen_period: set[str] = set()
    for period, _, _ in TOPICS:
        if period in seen_period:
            continue
        seen_period.add(period)
        if period in by_period:
            items = by_period[period]
            print(f"\n  【{period}】缺 {len(items)}/4")
            for topic, theme in items:
                print(f"      □ {topic}   （{theme}）")
        else:
            print(f"\n  【{period}】✅ 4/4 齐全")

    print(f"\n缺失合计：{len(missing)} 个论题")
    print("\n按主题统计缺口：")
    from collections import Counter
    c = Counter(t for _, _, t in missing)
    for k, v in c.most_common():
        print(f"    {k:16s} {v}")

    out = ROOT / "00-元数据" / "论文范文缺口.json"
    out.write_text(json.dumps({
        "totalTopics": len(TOPICS), "covered": len(got), "missing": len(missing),
        "coveredList": [{"period": p, "topic": t, "theme": th, "file": f}
                        for p, t, th, f in got],
        "missingList": [{"period": p, "topic": t, "theme": th}
                        for p, t, th in missing],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n已写出 {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
