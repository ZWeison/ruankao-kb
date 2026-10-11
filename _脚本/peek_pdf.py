# -*- coding: utf-8 -*-
"""查看某个 PDF 的正文结构（前 N 行 + 标题候选）。"""
import re
import sys
from pathlib import Path

import pymupdf

pdf = Path(sys.argv[1])
n_show = int(sys.argv[2]) if len(sys.argv) > 2 else 70

doc = pymupdf.open(str(pdf))
print(f"文件: {pdf.name}")
print(f"页数: {doc.page_count}")
text = "".join((doc[i].get_text() or "") for i in range(doc.page_count))
doc.close()

body = re.sub(r"\n{2,}", "\n", text)
print(f"总字数(去空白): {len(re.sub(r'[ \t\n\r]', '', body))}")
print()

lines = [ln.strip() for ln in body.split("\n") if ln.strip()]
print(f"=== 前 {n_show} 个非空行 ===")
for i, s in enumerate(lines[:n_show], 1):
    print(f"{i:4d}| {s[:92]}")

print()
print("=== 可能的标题行（短行 + 含章/节/考点特征）===")
seen = 0
for i, s in enumerate(lines, 1):
    if len(s) <= 30 and re.search(r"第[一二三四五六七八九十\d]+[章节]|^[一二三四五六七八九十]、|考点|专题|真题", s):
        print(f"{i:4d}| {s}")
        seen += 1
        if seen >= 40:
            break
print(f"\n共 {len(lines)} 个非空行")
