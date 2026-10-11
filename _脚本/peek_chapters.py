# -*- coding: utf-8 -*-
"""
扫描"章节真题"类 PDF 的章节边界。

这类 PDF 是「按章组织的真题+解析」汇编：
  - 每章标题是独立短行（如「计算机组成与体系结构」），不带"第X章"前缀
  - 每页页眉含「第N 页共M 页」
  - 题目为「N.」开头，带 A/B/C/D 选项与【解析】

本脚本按页扫描，输出每页首个"疑似章节标题"的候选，便于人工确认章节表。
"""
import re
import sys
from collections import Counter
from pathlib import Path

import pymupdf

pdf = Path(sys.argv[1])

doc = pymupdf.open(str(pdf))
pages_text: list[str] = []
for i in range(doc.page_count):
    pages_text.append(doc[i].get_text() or "")
doc.close()

print(f"文件: {pdf.name}  页数: {len(pages_text)}\n")

# 统计全文中反复出现的短行 —— 这些是页眉/章节名
short_lines: Counter = Counter()
for t in pages_text:
    for ln in t.split("\n"):
        s = ln.strip()
        if 4 <= len(s) <= 28 and not re.match(r"^[\dA-D．.、\s]+$", s):
            short_lines[s] += 1

print("=== 高频短行（出现 ≥3 次，多为页眉或章名）===")
for s, c in short_lines.most_common(30):
    if c >= 3:
        print(f"  {c:4d}× {s}")

print("\n=== 逐页首个短行候选（可能标识章切换）===")
prev = None
for i, t in enumerate(pages_text, 1):
    for ln in t.split("\n"):
        s = ln.strip()
        if 4 <= len(s) <= 28 and not re.match(r"^[\dA-D．.、\s]+$", s) \
                and "第" not in s[:2] or (len(s) <= 20 and "共" not in s):
            if s != prev:
                print(f"  p{i:3d}: {s}")
                prev = s
            break
