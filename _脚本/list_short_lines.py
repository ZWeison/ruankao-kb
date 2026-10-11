# -*- coding: utf-8 -*-
"""列出章节真题 PDF 中所有「单页独占一行」的短行，用于人工确定章节表。

判据：该行在一页里只出现一次，长度 ≤ 22，且不含题干/选项/解析特征。
"""
import re
import sys
from collections import Counter
from pathlib import Path

import pymupdf

pdf = Path(sys.argv[1])
doc = pymupdf.open(str(pdf))
pages = [(doc[i].get_text() or "") for i in range(doc.page_count)]
doc.close()

HDR = re.compile(r"第\s*\d+\s*页\s*共\s*\d+\s*页")
BAD = re.compile(r"解析|答案|如下|所示|如图|下列|关于|以下|：|:|[（(]|[）)]|等于|因此|所以|"
                 r"其中|那么|则|若|假设|当|第\s*\d+\s*页")

cands: dict[str, tuple[int, str]] = {}
for i, t in enumerate(pages, 1):
    body = HDR.sub("", t)
    for ln in body.split("\n"):
        s = ln.strip()
        if not (3 <= len(s) <= 22):
            continue
        if re.match(r"^[\dA-Da-d．.、\s]+$", s):
            continue
        if BAD.search(s):
            continue
        # 中文为主，不含数字串
        if len(re.findall(r"[\u4e00-\u9fff]", s)) < 3:
            continue
        if re.search(r"\d", s):
            continue
        cands.setdefault(s, (i, s))

print(f"{pdf.name}  共 {len(pages)} 页")
print(f"候选短行 {len(cands)} 条，按首次出现页排序：\n")
for s, (pg, _) in sorted(cands.items(), key=lambda x: x[1][0]):
    print(f"  p{pg:3d}  {s}")
