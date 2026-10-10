#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统架构设计师知识库 —— 索引生成器

用法（在 D:\\软考知识库 下执行）：
    python _脚本\\build_index.py

产出：
  00-元数据/exams.json                      机器可读总索引
  02-按题型索引/选择题-按考期.md            按年份列出所有综合知识卷
  02-按题型索引/案例题-按考期.md
  02-按题型索引/论文题-按考期.md
  02-按题型索引/考点覆盖统计.md             标签出现频次 + 年份覆盖矩阵
  03-论文范文/00-选题索引.md                范文按主题/论题归类

本脚本只读取 01-真题-按年份 与 03-论文范文，不修改任何原有文件。
"""

from __future__ import annotations

import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAM_DIR = ROOT / "01-真题-按年份"
ESSAY_DIR = ROOT / "03-论文范文"
META_DIR = ROOT / "00-元数据"
INDEX_DIR = ROOT / "02-按题型索引"

EXAM_FILE_RE = re.compile(
    r"^(\d{4})-(上半年|下半年)-(综合知识|案例分析|论文)(?:-(.+))?\.md$"
)
SUBJECT_TYPE = {"综合知识": "选择题", "案例分析": "案例题", "论文": "论文题"}
SESSION_ORDER = {"上半年": 0, "下半年": 1}
GENERATED_NOTE = (
    "> ⚙️ 本文件由 `_脚本/build_index.py` 自动生成，"
    "**请勿手工编辑**（改动会在下次生成时丢失）。\n"
    f"> 生成时间：{date.today().isoformat()}\n"
)


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


def collect_exams() -> list[dict]:
    records: list[dict] = []
    if not EXAM_DIR.exists():
        return records
    for path in sorted(EXAM_DIR.rglob("*.md")):
        m = EXAM_FILE_RE.match(path.name)
        if not m:
            print(f"  [跳过] 文件名不符规范：{path.relative_to(ROOT)}")
            continue
        data, body = split_front_matter(path.read_text(encoding="utf-8", errors="replace"))
        year, session, subject, variant = (
            int(m.group(1)), m.group(2), m.group(3), m.group(4)
        )
        records.append({
            "year": year,
            "session": session,
            "subject": subject,
            "itemType": SUBJECT_TYPE.get(subject, ""),
            "variant": variant or "",
            "itemCount": data.get("题量", 0),
            "sourceKind": data.get("来源类型", "未知"),
            "official": bool(data.get("是否官方", False)),
            "hasAnswer": bool(data.get("含答案", False)),
            "answerCredibility": data.get("答案可信度", "未知"),
            "hasAnalysis": bool(data.get("含解析", False)),
            "tags": data.get("考点标签", []) if isinstance(data.get("考点标签"), list) else [],
            "origin": data.get("出处", ""),
            "url": data.get("URL", ""),
            "fetchedAt": str(data.get("抓取日期", "")),
            "proofread": data.get("校对状态", "未知"),
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "charCount": len(body),
        })
    records.sort(key=lambda r: (-r["year"], SESSION_ORDER.get(r["session"], 9), r["subject"]))
    return records


def collect_essays() -> list[dict]:
    records: list[dict] = []
    if not ESSAY_DIR.exists():
        return records
    for path in sorted(ESSAY_DIR.rglob("*.md")):
        # README / 生成物（00-选题索引.md 等）不是范文正文，跳过
        if path.name.lower() in ("readme.md", "index.md"):
            continue
        if path.name.startswith("00-"):
            continue
        data, body = split_front_matter(path.read_text(encoding="utf-8", errors="replace"))
        records.append({
            "topic": data.get("论题", path.stem),
            "kind": data.get("范文类型", "范文"),
            "year": str(data.get("对应年份", "未知")),
            "session": data.get("对应考期", "未知"),
            "theme": data.get("主题", path.parent.name),
            "wordCount": data.get("字数", "未知"),
            "isReal": bool(data.get("是否考场原文", False)),
            "origin": data.get("出处", ""),
            "url": data.get("URL", ""),
            "proofread": data.get("校对状态", "未知"),
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "charCount": len(body),
        })
    return records


def table(rows: list[list[str]], header: list[str]) -> str:
    if not rows:
        return "_（暂无数据）_\n"
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out) + "\n"


def rel_link(target_rel: str, from_dir: Path) -> str:
    """把仓库内相对路径转成从 from_dir 出发的正斜杠相对路径。"""
    try:
        rel = os.path.relpath(ROOT / target_rel, start=from_dir)
    except ValueError:
        return target_rel
    return rel.replace("\\", "/")


def write_by_subject(subject: str, records: list[dict]) -> None:
    rows = []
    for r in [x for x in records if x["subject"] == subject]:
        name = f"{r['year']}-{r['session']}-{r['subject']}"
        if r["variant"]:
            name += f"-{r['variant']}"
        rows.append([
            r["year"], r["session"], name,
            r["itemCount"] or "?",
            r["sourceKind"],
            "✅" if r["hasAnswer"] else "—",
            r["answerCredibility"],
            "✅" if r["hasAnalysis"] else "—",
            r["proofread"],
            f"[{r['origin']}]({r['url']})" if r["url"].startswith("http") else r["origin"],
            f"[打开]({rel_link(r['path'], INDEX_DIR)})",
        ])
    title = f"# {SUBJECT_TYPE[subject]}索引（{subject}）\n\n{GENERATED_NOTE}\n"
    if not rows:
        title += "**尚未归档任何一卷。**\n\n"
        title += ("归档方法：把整理好的 Markdown 放到 "
                  f"`01-真题-按年份/YYYY-考期/YYYY-考期-{subject}.md`，"
                  "填好 YAML 头部后重新运行本脚本。\n")
    else:
        title += table(rows, [
            "年份", "考期", "文件名", "题量", "来源类型",
            "含答案", "答案可信度", "含解析", "校对状态", "出处", "文件",
        ])
    (INDEX_DIR / f"{SUBJECT_TYPE[subject]}-按考期.md").write_text(title, encoding="utf-8")


def write_tag_stats(records: list[dict]) -> None:
    counter: Counter = Counter()
    by_tag_year: dict[str, set[int]] = defaultdict(set)
    for r in records:
        for t in r["tags"]:
            counter[t] += 1
            by_tag_year[t].add(r["year"])

    total = len(records)
    lines = [f"# 考点覆盖统计\n\n{GENERATED_NOTE}\n",
             f"收录试卷数：**{total}**\n"]

    if not counter:
        lines.append("**尚未归档任何一卷，暂无统计数据。**\n")
    else:
        lines.append("## 标签出现频次（按出现的卷数计）\n")
        rows = [[t, c, "、".join(str(y) for y in sorted(by_tag_year[t]))]
                for t, c in counter.most_common()]
        lines.append(table(rows, ["考点标签", "出现卷数", "涉及年份"]))
        lines.append("\n## 年份 × 科目 覆盖矩阵\n")
        years = sorted({r["year"] for r in records}, reverse=True)
        subjects = ["综合知识", "案例分析", "论文"]
        grid = []
        for y in years:
            cells = []
            for s in subjects:
                hit = [r for r in records if r["year"] == y and r["subject"] == s]
                cells.append(f"{len(hit)} 卷" if hit else "—")
            grid.append([y] + cells)
        lines.append(table(grid, ["年份"] + subjects))
    (INDEX_DIR / "考点覆盖统计.md").write_text("\n".join(lines), encoding="utf-8")


def write_essay_index(essays: list[dict]) -> None:
    lines = [f"# 论文范文选题索引\n\n{GENERATED_NOTE}\n",
             f"收录范文/模板：**{len(essays)}** 篇\n"]
    if not essays:
        lines.append("**尚未归档任何范文。**\n\n"
                     "归档方法：把范文 Markdown 放到 `03-论文范文/<主题目录>/`，"
                     "填好 YAML 头部（见 `00-元数据/元数据规范.md` 第 4 节）后重新运行本脚本。\n")
    else:
        by_theme: dict[str, list[dict]] = defaultdict(list)
        for e in essays:
            by_theme[str(e["theme"])].append(e)
        lines.append("## 按主题\n")
        for theme in sorted(by_theme):
            lines.append(f"\n### {theme}（{len(by_theme[theme])} 篇）\n")
            rows = [[
                e["topic"],
                e["kind"],
                f"{e['year']} {e['session']}" if e["year"] != "未知" else "未知",
                e["wordCount"],
                "✅ 考场原文" if e["isReal"] else "机构自产/仿写",
                e["proofread"],
                f"[打开]({rel_link(e['path'], ESSAY_DIR)})",
            ] for e in by_theme[theme]]
            lines.append(table(rows, [
                "论题", "类型", "对应考期", "字数", "原文性质", "校对状态", "文件",
            ]))
        lines.append("\n## 全部论题一览\n")
        lines.append(table(
            [[e["topic"], e["theme"], e["kind"], f"{e['year']} {e['session']}",
              e["wordCount"], f"[打开]({rel_link(e['path'], ESSAY_DIR)})"] for e in essays],
            ["论题", "主题", "类型", "对应考期", "字数", "文件"],
        ))
    (ESSAY_DIR / "00-选题索引.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    print("=" * 72)
    print("系统架构设计师知识库 —— 索引生成")
    print(f"根目录：{ROOT}")
    print("=" * 72)

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    META_DIR.mkdir(parents=True, exist_ok=True)

    exams = collect_exams()
    essays = collect_essays()
    print(f"收录：真题 {len(exams)} 卷，范文 {len(essays)} 篇\n")

    for subject in SUBJECT_TYPE:
        write_by_subject(subject, exams)
        print(f"  写入 02-按题型索引/{SUBJECT_TYPE[subject]}-按考期.md")

    write_tag_stats(exams)
    print("  写入 02-按题型索引/考点覆盖统计.md")

    write_essay_index(essays)
    print("  写入 03-论文范文/00-选题索引.md")

    payload = {
        "schemaVersion": 1,
        "generatedAt": date.today().isoformat(),
        "generator": "_脚本/build_index.py",
        "note": "本题库为个人学习资料，真题均为非官方回忆版；详见 00-元数据/来源清单.md",
        "stats": {"examFiles": len(exams), "essayFiles": len(essays)},
        "exams": exams,
        "essays": essays,
    }
    (META_DIR / "exams.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("  写入 00-元数据/exams.json")

    print("\n完成。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
