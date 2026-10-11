# -*- coding: utf-8 -*-
"""
扫描版 PDF → Markdown（PyMuPDF 渲染 + Tesseract OCR）

为什么要用临时 ASCII 目录：
  Tesseract 无法处理含中文的路径（会报 "Illegal byte sequence"），
  而本知识库根目录是 D:\\软考知识库。所以把每页 PNG 落到 C:\\ocrtmp 再调用。

用法：
  python _脚本\\ocr_pdf.py <PDF路径> <输出.md路径> [起始页] [结束页]
  python _脚本\\ocr_pdf.py --scan <目录>        # 列出该目录下"疑似扫描图"的 PDF

环境：
  TESSDATA_PREFIX 需指向含 chi_sim/eng 的目录（默认自动设为 C:\\tessdata）
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import pymupdf

TESS = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
TESSDATA = r"C:\tessdata"
TMP = Path(r"C:\ocrtmp")

# 先设好环境再调用 tesseract（子进程继承）
os.environ["TESSDATA_PREFIX"] = TESSDATA


def ocr_image(png: Path, lang: str = "chi_sim+eng") -> str:
    """对单张 PNG 做 OCR，返回文本。png 必须在 ASCII 路径下。"""
    TMP.mkdir(parents=True, exist_ok=True)
    out_base = TMP / (png.stem + "_out")
    cmd = [TESS, str(png), str(out_base), "-l", lang, "--psm", "6"]
    r = subprocess.run(cmd, capture_output=True, cwd=str(TMP))
    if r.returncode != 0:
        return f"[OCR 失败: {r.stderr.decode('utf-8', 'replace')[:200]}]"
    txt = out_base.with_suffix(".txt")
    if not txt.exists():
        return ""
    s = txt.read_text(encoding="utf-8", errors="replace")
    txt.unlink(missing_ok=True)
    return s


def clean_ocr(text: str) -> str:
    """清理 OCR 噪声。"""
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"[ \t]+", " ", t)
    # 合并被 OCR 拆断的中文行（行尾不是标点且下一行以中文开头）
    lines = t.split("\n")
    out: list[str] = []
    for ln in lines:
        s = ln.strip()
        if not s:
            if out and out[-1] != "":
                out.append("")
            continue
        if out and out[-1] and not re.search(r"[。！？；：\])】》”]$", out[-1]) \
                and not re.match(r"^[（(\[【《\d一二三四五六七八九十（]", s):
            out[-1] = out[-1] + s
        else:
            out.append(s)
    return "\n".join(out).strip()


def has_text_layer(pdf: Path, probe: int = 3, threshold: int = 200) -> bool:
    doc = pymupdf.open(str(pdf))
    try:
        total = 0
        for i in range(min(probe, doc.page_count)):
            total += len((doc[i].get_text() or "").strip())
        return total > threshold
    finally:
        doc.close()


def ocr_pdf(pdf: Path, out_md: Path, first: int = 1, last: int | None = None,
            dpi: int = 300, lang: str = "chi_sim+eng") -> dict:
    TMP.mkdir(parents=True, exist_ok=True)
    doc = pymupdf.open(str(pdf))
    try:
        start = max(1, first) - 1
        end = doc.page_count if last is None else min(last, doc.page_count)
        pages: list[str] = []
        for i in range(start, end):
            page = doc[i]
            pix = page.get_pixmap(dpi=dpi)
            png = TMP / f"p{i+1:04d}.png"
            pix.save(str(png))
            txt = clean_ocr(ocr_image(png, lang))
            pages.append(f"<!-- 第 {i+1} 页 -->\n\n{txt}")
            png.unlink(missing_ok=True)
            print(f"    第 {i+1}/{end} 页 OCR 完成（{len(txt)} 字）", flush=True)
    finally:
        doc.close()

    body = "\n\n---\n\n".join(pages)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(body, encoding="utf-8")
    return {"pages": end - start, "chars": len(re.sub(r"\s", "", body))}


def scan(directory: Path) -> None:
    pdfs = sorted(directory.rglob("*.pdf"))
    print(f"扫描 {len(pdfs)} 个 PDF\n")
    printed = 0
    for p in pdfs:
        try:
            ok = has_text_layer(p)
        except Exception as e:
            print(f"  ? {p.name} 读取失败: {e}")
            continue
        if not ok:
            doc = pymupdf.open(str(p))
            n = doc.page_count
            doc.close()
            size = p.stat().st_size / 1024 / 1024
            print(f"  [扫描图] {p.name}  页数={n}  {size:.1f}MB")
            printed += 1
    print(f"\n共 {printed} 个疑似扫描图 PDF")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)
    if sys.argv[1] == "--scan":
        scan(Path(sys.argv[2]))
    else:
        src = Path(sys.argv[1])
        dst = Path(sys.argv[2])
        first = int(sys.argv[3]) if len(sys.argv) > 3 else 1
        last = int(sys.argv[4]) if len(sys.argv) > 4 else None
        print(f"OCR: {src.name}  页 {first}—{last or '末尾'}")
        info = ocr_pdf(src, dst, first, last)
        print(f"\n完成：{info['pages']} 页，{info['chars']} 字 → {dst}")
