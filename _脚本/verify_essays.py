# -*- coding: utf-8 -*-
"""
核对论文范文转换完整性：源 PDF 抽取字数 vs Markdown 头部声明的字数。
两者应当一致（允许小幅差异，因为正文里加了来源说明块）。
"""
import re
import sys
from pathlib import Path

from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_staging" / "gitee" / "04、论文（真题范文+写作）"
KB = ROOT / "03-论文范文"

# 先建 PDF 名 → 抽取字数 的索引
pdf_chars: dict[str, int] = {}
for p in SRC.rglob("*.pdf"):
    try:
        txt = "".join((pg.extract_text() or "") for pg in PdfReader(str(p)).pages)
        pdf_chars[p.name] = len(re.sub(r"\s", "", txt))
    except Exception as e:
        pdf_chars[p.name] = -1

rows = []
for md in sorted(KB.rglob("*.md")):
    if md.name.startswith("00-") or md.name == "README.md":
        continue
    t = md.read_text(encoding="utf-8")
    m = re.search(r"^字数: (\d+)$", t, re.M)
    if not m:
        continue
    claimed = int(m.group(1))
    pm = re.search(r"原始文件：`([^`]+)`", t)
    src_name = pm.group(1) if pm else ""
    actual = pdf_chars.get(src_name)
    rows.append((md.name, claimed, actual, src_name))

rows.sort(key=lambda r: (r[2] if r[2] is not None else -1))

print(f"{'Markdown 文件':46s} {'声明':>6s} {'PDF实际':>8s}  判定")
print("-" * 82)
bad = 0
for name, claimed, actual, src_name in rows:
    if actual is None:
        verdict = "找不到源 PDF"
        bad += 1
    elif actual < 0:
        verdict = "PDF 读取失败"
        bad += 1
    elif abs(actual - claimed) <= 60:
        verdict = "OK"
    else:
        verdict = f"差 {actual - claimed:+d}"
        bad += 1
    disp = name[:44]
    print(f"{disp:46s} {claimed:6d} {str(actual):>8s}  {verdict}")

print("-" * 82)
print(f"共 {len(rows)} 篇，异常 {bad} 篇")
