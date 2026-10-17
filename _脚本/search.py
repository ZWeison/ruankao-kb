#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统架构设计师知识库 —— 全文检索

用法（在 D:\\软考知识库 下执行）：

  # 按关键词搜（默认搜正文 + 头部字段）
  python _脚本\\search.py ATAM

  # 按标签搜
  python _脚本\\search.py --tag 架构评估

  # 按来源类型过滤（只看真题/回忆版，排除模拟题）
  python _脚本\\search.py --kind 回忆版 熔断

  # 按年份范围
  python _脚本\\search.py --year 2023-2025 质量属性

  # 只搜真题正文
  python _脚本\\search.py --only 真题 微服务

  # 列出所有标签及出现次数
  python _脚本\\search.py --tags

  # 存疑题清单
  python _脚本\\search.py --dubious

选项：
  --tag TAG        限定考点标签（可重复）
  --kind KIND      限定来源类型：真题 / 回忆版 / 模拟题
  --year RANGE     年份范围，如 2023 或 2023-2025
  --subject S      限定科目：综合知识 / 案例分析 / 论文
  --only SCOPE     搜索范围：真题 / 范文 / 专题 / 全部（默认全部）
  --tags           列出标签统计
  --dubious        列出答案可信度为「存疑」的文件
  --stats          列出知识库整体统计
  -n N             最多显示 N 条命中上下文（默认 40）
"""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAM_DIR = ROOT / "01-真题-按年份"
ESSAY_DIR = ROOT / "03-论文范文"
CHAPTER_DIR = ROOT / "05-按章节真题"
CASE_TOPIC_DIR = ROOT / "05-案例专题"

EXAM_FILE_RE = re.compile(
    r"^(\d{4})-(上半年|下半年)-(综合知识|案例分析|论文)(?:-(.+))?\.md$"
)
SKIP_NAMES = {"readme.md", "index.md"}


def split_front_matter(text: str) -> tuple[dict, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block = text[3:end].strip("\n")
    body = text[end + 4:].lstrip("\n")
    data: dict = {}
    for raw in block.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = ([x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
                         if inner else [])
        elif val.lower() in ("true", "false"):
            data[key] = val.lower() == "true"
        elif re.fullmatch(r"-?\d+", val):
            data[key] = int(val)
        else:
            data[key] = val.strip("'\"")
    return data, body


class Doc:
    __slots__ = ("path", "meta", "body", "scope", "year", "kind")

    def __init__(self, path: Path, scope: str):
        self.path = path
        self.scope = scope
        data, body = split_front_matter(path.read_text(encoding="utf-8", errors="replace"))
        self.meta = data
        self.body = body
        m = EXAM_FILE_RE.match(path.name)
        self.year = int(m.group(1)) if m else None
        self.kind = data.get("来源类型") or data.get("范文类型") or ""

    @property
    def rel(self) -> str:
        return str(self.path.relative_to(ROOT)).replace("\\", "/")

    @property
    def tags(self) -> list[str]:
        t = self.meta.get("考点标签")
        return t if isinstance(t, list) else []

    @property
    def label(self) -> str:
        if self.scope == "真题":
            return f"{self.meta.get('年份','?')}-{self.meta.get('考期','?')}-{self.meta.get('科目','?')}"
        if self.scope == "专题":
            return str(self.meta.get("题型", self.path.stem))
        return str(self.meta.get("论题", self.path.stem))


def load_docs() -> list[Doc]:
    docs: list[Doc] = []
    for base, scope in ((EXAM_DIR, "真题"), (ESSAY_DIR, "范文"),
                        (CHAPTER_DIR, "章节"), (CASE_TOPIC_DIR, "专题")):
        if not base.exists():
            continue
        for p in sorted(base.rglob("*.md")):
            if p.name.lower() in SKIP_NAMES or p.name.startswith("00-"):
                continue
            docs.append(Doc(p, scope))
    return docs


def in_year_range(year, spec: str) -> bool:
    if year is None:
        return False
    if "-" in spec:
        a, _, b = spec.partition("-")
        try:
            return int(a) <= year <= int(b)
        except ValueError:
            return True
    return str(year) == spec.strip()


def cmd_tags(docs: list[Doc]) -> None:
    c: Counter = Counter()
    for d in docs:
        c.update(d.tags)
    if not c:
        print("（尚未归档任何带标签的文件）")
        return
    print(f"{'标签':<20}{'卷/篇数'}")
    print("-" * 30)
    for t, n in c.most_common():
        print(f"{t:<20}{n}")


def cmd_stats(docs: list[Doc]) -> None:
    exams = [d for d in docs if d.scope == "真题"]
    essays = [d for d in docs if d.scope == "范文"]
    chapters = [d for d in docs if d.scope == "章节"]
    topics = [d for d in docs if d.scope == "专题"]
    sim = sum(d.meta.get("含模拟题", 0) or 0 for d in topics
              if isinstance(d.meta.get("含模拟题", 0), int))
    real_in_topic = sum(d.meta.get("含真题", 0) or 0 for d in topics
                        if isinstance(d.meta.get("含真题", 0), int))
    print(f"收录：真题 {len(exams)} 卷，范文 {len(essays)} 篇，"
          f"案例专题 {len(topics)} 篇（模拟题 {sim} 道 + 真题 {real_in_topic} 道）\n")
    if exams:
        years = sorted({d.year for d in exams if d.year})
        print(f"真题年份跨度：{years[0]} — {years[-1]}")
        c: Counter = Counter(d.meta.get("来源类型", "未知") for d in exams)
        print("来源类型分布：" + "，".join(f"{k} {v}" for k, v in c.most_common()))
        c = Counter(d.meta.get("校对状态", "未知") for d in exams)
        print("校对状态分布：" + "，".join(f"{k} {v}" for k, v in c.most_common()))
        c = Counter(str(d.meta.get("答案可信度", "未知")) for d in exams)
        print("答案可信度分布：" + "，".join(f"{k} {v}" for k, v in c.most_common()))
    if essays:
        c = Counter("考场原文" if d.meta.get("是否考场原文") is True else "机构自产/仿写"
                    for d in essays)
        print("范文原文性质：" + "，".join(f"{k} {v}" for k, v in c.most_common()))


def cmd_dubious(docs: list[Doc]) -> None:
    hits = [d for d in docs if d.meta.get("答案可信度") == "存疑"
            or d.meta.get("校对状态") == "存疑"]
    if not hits:
        print("没有标记为「存疑」的文件。")
        return
    print(f"存疑文件（{len(hits)}）：\n")
    for d in hits:
        print(f"  {d.rel}")
        print(f"    答案可信度={d.meta.get('答案可信度','-')} "
              f"校对状态={d.meta.get('校对状态','-')} 出处={d.meta.get('出处','-')}")


def cmd_search(docs: list[Doc], args) -> None:
    pat = re.compile(re.escape(args.keyword), re.IGNORECASE) if args.keyword else None
    results: list[tuple[Doc, list[str]]] = []

    for d in docs:
        if args.only != "全部" and d.scope != args.only:
            continue
        if args.kind and d.meta.get("来源类型") != args.kind:
            continue
        if args.subject and d.meta.get("科目") != args.subject:
            continue
        if args.year and not in_year_range(d.year, args.year):
            continue
        if args.tag and not all(t in d.tags for t in args.tag):
            continue

        if pat is None:
            results.append((d, []))
            continue

        lines: list[str] = []
        header_text = "\n".join(
            f"{k}: {'、'.join(v) if isinstance(v, list) else v}"
            for k, v in d.meta.items()
        )
        for i, line in enumerate((header_text + "\n" + d.body).splitlines(), 1):
            if pat.search(line):
                lines.append(f"      L{i}: {line.strip()[:110]}")
        if lines:
            results.append((d, lines))

    if not results:
        print("没有命中。")
        return

    print(f"命中 {len(results)} 个文件"
          + (f"（关键词：{args.keyword}）" if args.keyword else "") + "\n")
    for d, lines in results:
        head = f"● {d.label}"
        meta_bits = [f"{d.meta.get('来源类型','')}"]
        if d.year:
            meta_bits.append(str(d.year))
        if d.tags:
            meta_bits.append("标签:" + "/".join(d.tags))
        meta_bits.append(f"校对:{d.meta.get('校对状态','-')}")
        print(head)
        print(f"    {' | '.join(x for x in meta_bits if x)}")
        print(f"    {d.rel}")
        for l in lines[: args.n]:
            print(l)
        if len(lines) > args.n:
            print(f"      …… 还有 {len(lines) - args.n} 处命中")
        print()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="系统架构设计师知识库全文检索",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("keyword", nargs="?", default=None, help="搜索关键词（支持中文）")
    ap.add_argument("--tag", action="append", help="限定考点标签，可重复")
    ap.add_argument("--kind", help="来源类型：真题 / 回忆版 / 模拟题")
    ap.add_argument("--year", help="年份或范围，如 2023 或 2023-2025")
    ap.add_argument("--subject", help="科目：综合知识 / 案例分析 / 论文")
    ap.add_argument("--only", default="全部", choices=["真题", "范文", "章节", "专题", "全部"],
                    help="搜索范围")
    ap.add_argument("--tags", action="store_true", help="列出标签统计")
    ap.add_argument("--stats", action="store_true", help="列出整体统计")
    ap.add_argument("--dubious", action="store_true", help="列出存疑文件")
    ap.add_argument("-n", type=int, default=40, help="每个文件最多显示几处命中")
    args = ap.parse_args()

    docs = load_docs()

    if args.tags:
        cmd_tags(docs)
        return 0
    if args.stats:
        cmd_stats(docs)
        return 0
    if args.dubious:
        cmd_dubious(docs)
        return 0

    if not docs:
        print("知识库目前是空的（还没有归档任何真题或范文）。")
        print(f"扫描目录：{EXAM_DIR}")
        print(f"          {ESSAY_DIR}")
        return 0

    if args.keyword is None and not args.tag and not args.kind and not args.year:
        ap.print_help()
        return 0

    cmd_search(docs, args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
