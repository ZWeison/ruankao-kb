#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
系统架构设计师知识库 —— 元数据校验器

用法（在 D:\\软考知识库 下执行）：
    python _脚本\\validate.py

检查项：
  1. 真题文件头部是否存在、15 个字段是否齐全
  2. 枚举取值是否合法
  3. 目录名 / 文件名 / 头部三者是否一致（年份、考期、科目）
  4. 同一「年份+考期+科目」是否重复
  5. 考期是否真实存在（见 ALLOWED_SESSIONS）
  6. 论文范文头部 10 个字段是否齐全
  7. 考点标签是否在词表内

退出码：0 = 全部通过；1 = 存在错误
"""

from __future__ import annotations

import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------- 常量定义

SUBJECTS = ("综合知识", "案例分析", "论文")
SUBJECT_TYPE = {"综合知识": "选择题", "案例分析": "案例题", "论文": "论文题"}
SOURCE_KINDS = ("真题", "回忆版", "模拟题")
CREDIBILITY = ("高", "中", "存疑")
PROOFREAD = ("已校对", "待校对", "存疑")
SESSIONS = ("上半年", "下半年")

REQUIRED_EXAM = [
    "年份", "考期", "科目", "题量", "题目类型", "来源类型", "是否官方",
    "含答案", "答案可信度", "含解析", "考点标签", "出处", "URL",
    "抓取日期", "校对状态",
]

REQUIRED_ESSAY = [
    "范文类型", "论题", "对应年份", "对应考期", "主题", "字数",
    "是否考场原文", "出处", "URL", "抓取日期", "校对状态",
]

# 05-按章节真题：按考点组织的复习视图（非按考期归档的正本）
REQUIRED_CHAPTER = [
    "材料类型", "章节", "题量", "来源类型", "是否官方", "含答案",
    "答案可信度", "含解析", "出处", "URL", "抓取日期", "校对状态",
]

# 05-案例专题：按题型组织的案例专题（含自主命题模拟题 + 部分真题原文）
REQUIRED_CASE_TOPIC = [
    "文档类型", "题型", "主题", "含模拟题", "含真题", "来源类型",
    "是否官方", "出处", "URL", "抓取日期", "校对状态",
]
CASE_TOPIC_KIND = "案例专题"

ESSAY_KINDS = ("范文", "模板", "提纲")

# 真实开考情况（与 00-元数据/考试期次总表.md 保持一致）
# 2016—2023 仅下半年开考；2024 起一年两次
ONLY_H2 = set(range(2009, 2024))          # 2009—2023 只有下半年
BOTH_SESSIONS = {2024, 2025, 2026}

EXAM_DIR = ROOT / "01-真题-按年份"
ESSAY_DIR = ROOT / "03-论文范文"
CHAPTER_DIR = ROOT / "05-按章节真题"
CASE_TOPIC_DIR = ROOT / "05-案例专题"

# 年份-考期目录名
EXAM_DIR_RE = re.compile(r"^(\d{4})-(上半年|下半年)$")
# 真题文件名 YYYY-考期-科目[-版本].md
EXAM_FILE_RE = re.compile(
    r"^(\d{4})-(上半年|下半年)-(综合知识|案例分析|论文)(?:-(.+))?\.md$"
)

errors: list[str] = []
warnings: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


# ---------------------------------------------------------------- YAML 解析

def split_front_matter(text: str) -> tuple[dict, str]:
    """极简 YAML front matter 解析器，只支持本知识库用到的标量/行内列表。"""
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
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            continue
        key, _, val = line.partition(":")
        key, val = key.strip(), val.strip()
        if val.startswith("[") and val.endswith("]"):
            inner = val[1:-1].strip()
            data[key] = (
                [x.strip().strip("'\"") for x in inner.split(",") if x.strip()]
                if inner else []
            )
        elif val.lower() in ("true", "false"):
            data[key] = val.lower() == "true"
        elif re.fullmatch(r"-?\d+", val):
            data[key] = int(val)
        else:
            data[key] = val.strip("'\"")
    return data, body


def load_tags(path: Path) -> set[str]:
    """从考点标签词表.md 提取所有合法标签（读取表格中的 `标签` 单元格）。"""
    tags: set[str] = set()
    if not path.exists():
        return tags
    for line in path.read_text(encoding="utf-8").splitlines():
        for m in re.finditer(r"`([^`]+)`", line):
            tags.add(m.group(1))
    return tags


# ---------------------------------------------------------------- 校验逻辑

def check_exam_file(path: Path, valid_tags: set[str], seen: dict) -> None:
    rel = path.relative_to(ROOT)
    m = EXAM_FILE_RE.match(path.name)
    if not m:
        err(f"{rel}｜文件名不符合规范 YYYY-考期-科目.md")
        return
    f_year, f_session, f_subject = int(m.group(1)), m.group(2), m.group(3)

    # 目录名一致性
    dm = EXAM_DIR_RE.match(path.parent.name)
    if not dm:
        err(f"{rel}｜父目录名不符合规范 YYYY-考期")
    else:
        if int(dm.group(1)) != f_year:
            err(f"{rel}｜目录年份 {dm.group(1)} 与文件名年份 {f_year} 不一致")
        if dm.group(2) != f_session:
            err(f"{rel}｜目录考期 {dm.group(2)} 与文件名考期 {f_session} 不一致")

    # 考期真实性
    if f_year in ONLY_H2 and f_session == "上半年":
        err(f"{rel}｜{f_year} 年只在【下半年】开考，不存在上半年考试")

    data, body = split_front_matter(path.read_text(encoding="utf-8", errors="replace"))
    if not data:
        err(f"{rel}｜缺少 YAML 头部（front matter）")
        return

    missing = [k for k in REQUIRED_EXAM if k not in data]
    if missing:
        err(f"{rel}｜缺少字段：{'、'.join(missing)}")

    for key, allowed in (
        ("科目", SUBJECTS),
        ("来源类型", SOURCE_KINDS),
        ("答案可信度", CREDIBILITY),
        ("校对状态", PROOFREAD),
        ("考期", SESSIONS),
    ):
        if key in data and data[key] not in allowed:
            err(f"{rel}｜{key} = 「{data[key]}」不在允许取值 {allowed}")

    if "是否官方" in data and not isinstance(data["是否官方"], bool):
        err(f"{rel}｜是否官方 必须是 true/false")
    if "含答案" in data and not isinstance(data["含答案"], bool):
        err(f"{rel}｜含答案 必须是 true/false")
    if "含解析" in data and not isinstance(data["含解析"], bool):
        err(f"{rel}｜含解析 必须是 true/false")

    # 与文件名交叉验证
    if data.get("年份") != f_year:
        err(f"{rel}｜头部年份 {data.get('年份')} 与文件名 {f_year} 不一致")
    if data.get("考期") != f_session:
        err(f"{rel}｜头部考期 {data.get('考期')} 与文件名 {f_session} 不一致")
    if data.get("科目") != f_subject:
        err(f"{rel}｜头部科目 {data.get('科目')} 与文件名 {f_subject} 不一致")
    if f_subject in SUBJECT_TYPE and data.get("题目类型") != SUBJECT_TYPE[f_subject]:
        err(f"{rel}｜题目类型应为「{SUBJECT_TYPE[f_subject]}」，实际「{data.get('题目类型')}」")

    # 官方从未公布真题
    if data.get("是否官方") is True and data.get("来源类型") != "模拟题":
        warn(f"{rel}｜标记为官方真题：官方从未公布过真题，请确认是否有据")

    # 标签
    tags = data.get("考点标签")
    if isinstance(tags, list):
        if not (1 <= len(tags) <= 8):
            warn(f"{rel}｜考点标签数量 {len(tags)} 个，建议 2—6 个")
        if valid_tags:
            unknown = [t for t in tags if t not in valid_tags]
            if unknown:
                warn(f"{rel}｜标签不在词表内：{'、'.join(unknown)}（请先加入考点标签词表.md）")
    elif "考点标签" in data:
        err(f"{rel}｜考点标签 必须是 [a, b, c] 格式")

    # 重复期次（同一 年份+考期+科目+版本标记 只能一个文件）
    # 版本后缀（-回忆版A / -回忆版B）是合法区分：机考后同一次考试存在多套
    # 题序、题量都不同的回忆版，禁止合并，必须各自成文件。
    key = (f_year, f_session, f_subject, m.group(4) or "")
    if key in seen:
        err(f"{rel}｜与 {seen[key]} 重复"
            f"（同一 年份+考期+科目+版本 只能一个文件）")
    else:
        seen[key] = str(rel)

    if not body.strip():
        err(f"{rel}｜正文为空")


def check_essay_file(path: Path, valid_tags: set[str]) -> None:
    rel = path.relative_to(ROOT)
    data, body = split_front_matter(path.read_text(encoding="utf-8", errors="replace"))
    if not data:
        err(f"{rel}｜缺少 YAML 头部（front matter）")
        return
    missing = [k for k in REQUIRED_ESSAY if k not in data]
    if missing:
        err(f"{rel}｜缺少字段：{'、'.join(missing)}")
    if "范文类型" in data and data["范文类型"] not in ESSAY_KINDS:
        err(f"{rel}｜范文类型 = 「{data['范文类型']}」不在 {ESSAY_KINDS}")
    if "校对状态" in data and data["校对状态"] not in PROOFREAD:
        err(f"{rel}｜校对状态 取值非法")
    if "是否考场原文" in data and not isinstance(data["是否考场原文"], bool):
        err(f"{rel}｜是否考场原文 必须是 true/false")
    if data.get("是否考场原文") is True:
        warn(f"{rel}｜标记为考场原文：多数公开\"范文\"实为机构自产，请确认可溯源")
    if not body.strip():
        err(f"{rel}｜正文为空")


def check_chapter_file(path: Path) -> None:
    """校验 05-按章节真题 下的文件头部。"""
    rel = path.relative_to(ROOT)
    data, body = split_front_matter(path.read_text(encoding="utf-8", errors="replace"))
    if not data:
        err(f"{rel}｜缺少 YAML 头部（front matter）")
        return
    missing = [k for k in REQUIRED_CHAPTER if k not in data]
    if missing:
        err(f"{rel}｜缺少字段：{'、'.join(missing)}")
    for key, allowed in (("来源类型", SOURCE_KINDS),
                         ("答案可信度", CREDIBILITY),
                         ("校对状态", PROOFREAD)):
        if key in data and data[key] not in allowed:
            err(f"{rel}｜{key} = 「{data[key]}」不在允许取值 {allowed}")
    for key in ("是否官方", "含答案", "含解析"):
        if key in data and not isinstance(data[key], bool):
            err(f"{rel}｜{key} 必须是 true/false")
    if not body.strip():
        err(f"{rel}｜正文为空")


def check_case_topic_file(path: Path, valid_tags: set[str]) -> None:
    """05-案例专题：按题型组织的专题（含自主命题模拟题 + 部分真题原文）。"""
    rel = path.relative_to(ROOT)
    data, body = split_front_matter(path.read_text(encoding="utf-8", errors="replace"))
    if not data:
        err(f"{rel}｜缺少 YAML 头部（front matter）")
        return
    missing = [k for k in REQUIRED_CASE_TOPIC if k not in data]
    if missing:
        err(f"{rel}｜缺少字段：{'、'.join(missing)}")
    if data.get("文档类型") != CASE_TOPIC_KIND:
        err(f"{rel}｜文档类型应为「{CASE_TOPIC_KIND}」，实际「{data.get('文档类型')}」")
    for key, allowed in (("来源类型", SOURCE_KINDS),
                         ("校对状态", PROOFREAD)):
        if key in data and data[key] not in allowed:
            err(f"{rel}｜{key} = 「{data[key]}」不在允许取值 {allowed}")
    if "是否官方" in data and not isinstance(data["是否官方"], bool):
        err(f"{rel}｜是否官方 必须是 true/false")
    for key in ("含模拟题", "含真题"):
        if key in data and not isinstance(data[key], int):
            err(f"{rel}｜{key} 必须是整数")
    if not body.strip():
        err(f"{rel}｜正文为空")


def main() -> int:
    print("=" * 72)
    print("系统架构设计师知识库 —— 元数据校验")
    print(f"根目录：{ROOT}")
    print(f"日期：{date.today().isoformat()}")
    print("=" * 72)

    tag_file = ROOT / "00-元数据" / "考点标签词表.md"
    valid_tags = load_tags(tag_file)
    print(f"标签词表载入：{len(valid_tags)} 个标签\n")

    seen: dict = {}
    exam_count = essay_count = 0

    if EXAM_DIR.exists():
        for path in sorted(EXAM_DIR.rglob("*.md")):
            # README 等说明文件不是真题正文，跳过
            if path.name.lower() in ("readme.md", "index.md") or path.name.startswith("00-"):
                continue
            check_exam_file(path, valid_tags, seen)
            exam_count += 1
    else:
        warn(f"未找到真题目录 {EXAM_DIR}")

    if ESSAY_DIR.exists():
        for path in sorted(ESSAY_DIR.rglob("*.md")):
            # README / 生成物（00-选题索引.md 等）不是范文正文，跳过
            if path.name.lower() in ("readme.md", "index.md"):
                continue
            if path.name.startswith("00-"):
                continue
            check_essay_file(path, valid_tags)
            essay_count += 1

    chapter_count = 0
    if CHAPTER_DIR.exists():
        for path in sorted(CHAPTER_DIR.rglob("*.md")):
            if path.name.lower() in ("readme.md", "index.md"):
                continue
            check_chapter_file(path)
            chapter_count += 1

    case_topic_count = 0
    if CASE_TOPIC_DIR.exists():
        for path in sorted(CASE_TOPIC_DIR.rglob("*.md")):
            if path.name.lower() in ("readme.md", "index.md"):
                continue
            if path.name.startswith("00-"):
                continue
            check_case_topic_file(path, valid_tags)
            case_topic_count += 1

    print(f"扫描：真题 {exam_count} 个文件，范文 {essay_count} 个文件，"
          f"章节真题 {chapter_count} 个文件，案例专题 {case_topic_count} 个文件\n")

    if warnings:
        print(f"--- 警告（{len(warnings)}）---")
        for w in warnings:
            print(f"  [WARN] {w}")
        print()

    if errors:
        print(f"--- 错误（{len(errors)}）---")
        for e in errors:
            print(f"  [ERR ] {e}")
        print()
        print(f"结果：FAILED —— {len(errors)} 个错误，{len(warnings)} 个警告")
        return 1

    print(f"结果：PASSED —— 0 个错误，{len(warnings)} 个警告")
    if exam_count == 0 and essay_count == 0:
        print("（目前还没有待校验的文件，这是正常的初始状态）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
