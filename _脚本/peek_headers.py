# -*- coding: utf-8 -*-
"""检查分页 PDF 的页眉结构，定位章标题。"""
import re
import sys
from pathlib import Path

import pymupdf

pdf = Path(sys.argv[1])
doc = pymupdf.open(str(pdf))
pages = [(doc[i].get_text() or "") for i in range(doc.page_count)]
doc.close()

HDR = re.compile(r"第\s*\d+\s*页\s*共\s*\d+\s*页")

print(f"{pdf.name}  共 {len(pages)} 页\n")
print("=== 每页页眉之后的首个非空行（章标题最可能出现在这里）===")
for i, t in enumerate(pages, 1):
    m = HDR.search(t)
    after = t[m.end():] if m else t
    lines = [ln.strip() for ln in after.split("\n") if ln.strip()]
    first = lines[0] if lines else "<空>"
    # 只标记"像标题"的：短、且不像题干/选项/解析
    looks_title = (len(first) <= 24
                   and not re.match(r"^[\dA-D（(【]", first)
                   and "解析" not in first and "答案" not in first)
    mark = "★" if looks_title else " "
    print(f"{mark} p{i:3d}: {first[:70]}")
