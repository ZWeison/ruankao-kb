# -*- coding: utf-8 -*-
"""
把「系统架构设计章节真题.pdf」作为**整篇参考资料**归入 05-按章节真题/，
并生成一份「章节定位表」，便于按考点跳转。

为什么不拆成多个文件：
  实测该 PDF 的文字流不规整（章标题与正文常粘连、被页面切断），
  自动切分的章节边界不可靠（曾出现某章 34 页、另一章 0 页的明显错位）。
  与其产出一堆章节归属错误的文件，不如保留完整原文 + 提供定位表。
  —— 「宁可不拆，不可拆错」。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
SRC = (ROOT / "_staging" / "yjian180_sa2018" / "系统架构设计章节真题"
       / "系统架构设计章节真题.pdf")
OUT_DIR = ROOT / "_staging" / "imported3" / "05-按章节真题"

HDR = re.compile(r"第\s*(\d+)\s*页\s*共\s*(\d+)\s*页")

# 章节白名单：用于在每页里定位"这一页属于哪一章"，只做定位表，不做切分
CHAPTERS: list[str] = [
    "计算机组成与体系结构", "操作系统", "嵌入式系统设计", "计算机网络",
    "数据库系统", "系统性能", "系统可靠性", "软件架构评估",
    "特定领域软件架构", "软件工程", "开发模型", "需求分析", "软件设计",
    "软件测试", "软件维护", "设计模式", "信息安全", "标准化与知识产权",
    "专业英语",
]


def clean(text: str) -> str:
    """清理抽取噪声 + 合并被单独抽出的题号行。"""
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    t = HDR.sub("", t)

    lines = t.split("\n")
    merged: list[str] = []
    i = 0
    while i < len(lines):
        cur = lines[i]
        if re.fullmatch(r"\s*\d{1,3}\s*[.．、]\s*", cur) and i + 1 < len(lines):
            nxt = lines[i + 1].strip()
            if nxt and not re.fullmatch(r"\s*[A-D]\s*[.．、].*", nxt):
                merged.append(re.sub(r"\s+", "", cur) + nxt)
                i += 2
                continue
        merged.append(cur)
        i += 1
    t = "\n".join(merged)

    t = re.sub(r"(?<=[\u4e00-\u9fff])[ \t]+(?=[\u4e00-\u9fff])", "", t)
    t = re.sub(r"(?<=[\u4e00-\u9fff])[ \t]+(?=[，。；：、？！（）【】《》""''])", "", t)
    t = re.sub(r"(?<=[，。；：、？！（）【】《》""''])[ \t]+(?=[\u4e00-\u9fff])", "", t)
    t = re.sub(r"(?<=[\u4e00-\u9fff])[ \t]+(?=[．.,;:!?()\[\]])", "", t)
    t = re.sub(r"(?<=[．.,;:!?()\[\]])[ \t]+(?=[\u4e00-\u9fff])", "", t)

    lines = t.split("\n")
    out: list[str] = []
    for ln in lines:
        s = ln.strip()
        if not s:
            if out and out[-1] != "":
                out.append("")
            continue
        if (out and out[-1] and not re.search(r"[。！？；：\])】》”]$", out[-1])
                and not re.match(r"^[（(\[【《\d一二三四五六七八九十]", s)
                and not re.match(r"^[A-D][.．、]", s) and not s.startswith("【")):
            out[-1] += s
        else:
            out.append(s)
    t = "\n".join(out)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def main() -> int:
    doc = pymupdf.open(str(SRC))
    pages = [(doc[i].get_text() or "") for i in range(doc.page_count)]
    doc.close()
    print(f"源：{SRC.name}  {len(pages)} 页\n")

    # 定位表：找每章标题首次出现的页。
    # ⚠️ 该 PDF 文字流不规整，正文里也会出现章名（如解析文字提到「系统性能」），
    #    故本表页码仅为近似，**不作为可靠导航依据**，只用来提示"这本册子覆盖哪些章"。
    locate: list[dict] = []
    for name in CHAPTERS:
        hits: list[int] = []
        for idx, raw in enumerate(pages, 1):
            pos = raw.find(name)
            if pos != -1 and pos < len(raw) * 0.45:
                hits.append(idx)
        locate.append({"chapter": name, "pages": hits[:3], "count": len(hits)})

    print("=== 章节出现情况（页码近似，仅作覆盖提示）===")
    for item in locate:
        pg = item["pages"][0] if item["pages"] else None
        print(f"  {item['chapter']:22s} 首次≈p{pg if pg else '?'}  出现 {item['count']} 页")

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    body = clean("\n".join(pages))
    n_items = len(re.findall(r"(?m)^\s*\d{1,3}\s*[.．、]\s*\S", body))
    n_ans = len(re.findall(r"【答案】|【答案】：", body))
    n_ana = len(re.findall(r"【解析】", body))

    toc = "\n".join(
        f"| {i+1} | {x['chapter']} | {'≈ 第 ' + str(x['pages'][0]) + ' 页' if x['pages'] else '未检出'} |"
        f" {x['count']} |"
        for i, x in enumerate(locate))

    fm = [
        "---",
        "材料类型: 按章节真题",
        "章节: 全册（19 章）",
        f"题量: {n_items}",
        "来源类型: 回忆版",
        "是否官方: false",
        "含答案: true",
        "答案可信度: 中",
        "含解析: true",
        "出处: GitHub yjian180/2018_system_architect（系统架构设计章节真题.pdf）",
        "URL: https://github.com/yjian180/2018_system_architect",
        "抓取日期: 2026-10-11",
        "校对状态: 待校对",
        "---",
        "",
        "# 系统架构设计章节真题（按考点分章）",
        "",
        "> **来源**：GitHub `yjian180/2018_system_architect` 的 `系统架构设计章节真题.pdf`，",
        f"> 共 128 页 / 约 13.4 万字。非官方。",
        ">",
        f"> 本册含约 **{n_items} 道题**、**{n_ans} 个答案**、**{n_ana} 段解析**。",
        ">",
        "> **与 `01-真题-按年份/` 的关系**：那一层是「按考期保真的正本」，",
        "> 本册是「**按考点横向打穿的复习视图**」——",
        "> 想专门攻「设计模式」，就看本册对应章，一次打穿历年该考点的所有题。",
        "> 同一道题可能两边都有，**用途不同，不合并**。",
        ">",
        "> ⚠️ **三个已知限制**：",
        "> 1. **本册未按章拆分文件**。实测该 PDF 文字流不规整（章标题与正文粘连、被分页切断），",
        ">    自动切分会产生章节错位（曾试出某章 34 页、另一章 0 页），故保留完整原文 + 下方定位表。",
        "> 2. **下方定位表的页码仅为近似**。正文解析里也会出现章名（如讲解中提到「系统性能」），",
        ">    自动定位无法区分「章标题」与「正文提及」，**不要依赖该表精确跳转**。",
        "> 3. 内容为 PDF 逐字抽取，存在断句与个别错字，**重要结论请回原卷核对**。",
        "",
        "---",
        "",
        "## 章节目录（覆盖范围提示）",
        "",
        "下表说明本册**覆盖哪些考点章节**，页码仅作参考。",
        "实际使用时建议**用关键词搜索**（如搜「设计模式」或具体题眼）定位，比按页翻更可靠。",
        "",
        "| # | 章节 | 首次出现（近似） | 相关页数 |",
        "|---|---|---|---|",
        toc,
        "",
        "> 提示：本册的价值是「同一考点的历年题目集中在一处」。",
        "> 例如攻「设计模式」，直接搜关键词，比重头翻十套真题更省时间。",
        "",
        "---",
        "",
        body,
        "",
    ]
    dest = OUT_DIR / "系统架构设计章节真题-全册.md"
    dest.write_text("\n".join(fm), encoding="utf-8")

    (OUT_DIR.parent / "import3_report.json").write_text(
        json.dumps({"locate": locate, "items": n_items, "answers": n_ans,
                    "analyses": n_ana, "chars": len(re.sub(r"\s", "", body)),
                    "file": dest.name}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print(f"\n写入 {dest.name}")
    print(f"  题量≈{n_items}  答案 {n_ans}  解析 {n_ana}  "
          f"{len(re.sub(r'\\s','',body))} 字")
    return 0


if __name__ == "__main__":
    sys.exit(main())
