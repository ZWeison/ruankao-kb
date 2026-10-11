# -*- coding: utf-8 -*-
"""在章节真题 PDF 中定位已知的教材章节标题行。"""
import re
import sys
from pathlib import Path

import pymupdf

pdf = Path(sys.argv[1])
doc = pymupdf.open(str(pdf))
pages = [(doc[i].get_text() or "") for i in range(doc.page_count)]
doc.close()

# 系统架构设计师教材（清华第2版）的章节名 + 常见章节真题分类名
CANDIDATES = [
    "计算机组成与体系结构", "操作系统", "计算机网络", "数据库系统",
    "系统性能", "系统可靠性", "信息安全", "软件工程", "开发模型",
    "需求分析", "软件设计", "软件测试", "软件维护", "软件项目管理",
    "系统架构设计", "特定领域软件架构", "基于架构的软件开发",
    "软件架构评估", "构件与中间件", "构件", "设计模式", "系统设计",
    "面向对象", "UML", "嵌入式", "系统运行与维护", "标准化与知识产权",
    "知识产权", "法律法规", "数学", "专业英语", "其他",
]

print(f"{pdf.name}  共 {len(pages)} 页\n")
print("=== 各章节名首次出现的页码 ===")
found = {}
for name in CANDIDATES:
    for i, t in enumerate(pages, 1):
        # 作为独立行出现（允许前后空白）
        if re.search(r"(?m)^\s*" + re.escape(name) + r"\s*$", t):
            found.setdefault(name, i)
            break

for name, pg in sorted(found.items(), key=lambda x: x[1]):
    print(f"  p{pg:3d}  {name}")

print("\n=== 所有「独立短行」且重复度低的行（章节名候选）===")
from collections import Counter
cnt: Counter = Counter()
firstpage: dict[str, int] = {}
for i, t in enumerate(pages, 1):
    for ln in t.split("\n"):
        s = ln.strip()
        if 3 <= len(s) <= 22 and not re.match(r"^[\dA-D．.、（）()【】\s]+$", s):
            cnt[s] += 1
            firstpage.setdefault(s, i)
for s, c in sorted(firstpage.items(), key=lambda x: x[1]):
    if cnt[s] <= 6 and not re.search(r"解析|答案|如下|所示|如图|下列|关于|以下", s):
        print(f"  p{firstpage[s]:3d} ({cnt[s]}×) {s}")
