# -*- coding: utf-8 -*-
"""探测 PDF 是否含文本层，并预览抽取质量。"""
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("需要 pypdf：python -m pip install pypdf")
    sys.exit(1)

stage = Path(sys.argv[1] if len(sys.argv) > 1 else r"D:\软考知识库\_staging\gitee")
files = sorted(stage.rglob("*.pdf"))
print(f"共 {len(files)} 个 PDF\n")

good = bad = 0
for f in files:
    try:
        r = PdfReader(str(f))
        n = len(r.pages)
        txt = ""
        for p in r.pages[:3]:
            txt += p.extract_text() or ""
        t = txt.strip()
        if len(t) > 200:
            good += 1
            flag = "有文本层"
        else:
            bad += 1
            flag = "疑似扫描图"
        name = f.name[:30]
        print(f"{name:32s} 页={n:3d} 抽取={len(t):6d}  {flag}")
        if len(t) > 200:
            sample = t[:100].replace("\n", " ")
            print(f"     样本: {sample}")
    except Exception as e:
        bad += 1
        print(f"{f.name[:30]:32s} 读取失败: {e}")

print(f"\n汇总：有文本层 {good} 个，疑似扫描图 {bad} 个")
