# -*- coding: utf-8 -*-
"""
把论文范文 PDF 转成本知识库的 Markdown，并按主题归入 03-论文范文/。

输入：_staging/gitee/04、论文（真题范文+写作）/**/*.pdf
输出：_staging/imported/03-论文范文/<主题目录>/NNN-<论题简称>.md

处理要点：
- 论题从正文首行提取，**不信任文件名**（源里有 论信息系统架构设计 / 论信息系统的架构设计
  这类近似但不相同的两篇，也有 _2 后缀的重复篇）
- 按论题关键词判主题目录，判不准进 99-未分类
- 是否考场原文：无法确证 → false（保守）
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

try:
    from pypdf import PdfReader
except ImportError:
    print("需要 pypdf：python -m pip install pypdf")
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_staging" / "gitee" / "04、论文（真题范文+写作）"
OUT = ROOT / "_staging" / "imported" / "03-论文范文"

# 论题关键词 → 主题目录（顺序有意义：先匹配到的胜）
THEME_RULES: list[tuple[str, str]] = [
    ("微服务与云原生", r"微服务|云原生|容器|服务网格|Serverless|无服务器"),
    ("大数据与NoSQL", r"大数据|数据仓库|数据湖|数据中台|NoSQL|分布式数据库|分布式存储|海量数据"),
    ("信息安全", r"安全性|安全架构|网络安全|信息安全|加密|认证|病毒|防护"),
    ("企业应用集成", r"企业应用集成|企业集成|EAI|ESB|中间件|集成平台|应用集成"),
    ("SOA与架构演化", r"SOA|面向服务|架构演化|遗留|改造|重构|三层结构|三层架构|分层"),
    ("嵌入式", r"嵌入式|实时系统|RTOS"),
    ("软件可靠性", r"可靠性|可维护性|容错|高可用|容灾|可用性|性能|优化|Web服务器"),
    ("架构评估", r"架构评估|体系结构评估|ATAM|质量属性"),
    ("设计模式", r"设计模式|模式的应用|面向对象"),
    ("基于构件", r"构件|复用|软件复用|构件化"),
    ("测试与质量", r"测试|质量保证|QA|评审"),
    ("DevOps与Serverless", r"DevOps|持续集成|持续交付|自动化运维"),
    ("软件工程与过程", r"^论UP|统一过程|RUP|生命周期|敏捷"),
    ("架构设计", r"架构设计|体系结构设计|软件架构|信息系统架构|需求分析|UML|建模|设计"),
]

THEME_DIRS = [
    "01-架构设计", "02-架构评估", "03-软件可靠性", "04-信息安全",
    "05-微服务与云原生", "06-大数据与NoSQL", "07-SOA与架构演化",
    "08-基于构件", "09-设计模式", "10-企业应用集成", "11-嵌入式",
    "12-测试与质量", "13-DevOps与Serverless", "14-软件工程与过程",
    "99-未分类",
]

# 主题名 → 带序号前缀的目录名（THEME_RULES 里写的是逻辑名，落盘要带前缀）
NAME_TO_DIR = {d[3:]: d for d in THEME_DIRS}


def dir_for(theme: str) -> str:
    """把逻辑主题名解析成真实目录名。"""
    if theme in NAME_TO_DIR:
        return NAME_TO_DIR[theme]
    for d in THEME_DIRS:
        if d[3:] == theme:
            return d
    return "99-未分类"


def extract_text(pdf: Path) -> str:
    reader = PdfReader(str(pdf))
    return "\n".join((p.extract_text() or "") for p in reader.pages)


def clean(text: str) -> str:
    """清理 PDF 抽取噪声：行尾连字符断词、多余空白、页码行。"""
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"-\n(?=[a-z])", "", t)            # 英文断词
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    # 去掉形如孤立的页码行
    t = re.sub(r"\n\s*\d{1,3}\s*\n", "\n", t)
    return t.strip()


def get_topic(text: str, fallback: str) -> str:
    """
    论题提取，按优先级：
      1) 「试题N 论XXX」—— PDF 里常见的试卷标注，最可靠
      2) 独立的「论XXXX」行（源里格式不一，有的前面带 x / 页码残留）
      3) 前 12 行里形如「XXX应用」「XXX设计」的短标题行
      4) 文件名
    不能直接取第一个非空行：PDF 首行常是页眉（「x 企业集成平台」「历年真题」）。
    """
    head = text[:3000]

    # 1) 试题N + 论题
    m = re.search(r"试题[一二三四五六七八九十\d]+\s*(论[^\n，。；：]{2,30})", head)
    if m:
        t = re.sub(r"\s+", "", m.group(1))
        if 4 <= len(t) <= 32:
            return t

    # 2) 独立成行的论题（允许前置 1-2 个噪声字符）
    for m in re.finditer(r"^[\s\dxX·、.．]{0,3}(论[^\n，。；：]{2,30})\s*$", head, re.M):
        t = re.sub(r"\s+", "", m.group(1))
        if 4 <= len(t) <= 32 and "摘要" not in t:
            return t

    # 3) 短标题行（如「x 设计模式」）
    for line in head.splitlines()[:12]:
        s = re.sub(r"^[\s\dxX·、.．]{0,3}", "", line.strip())
        s = re.sub(r"\s+", "", s)
        if 4 <= len(s) <= 24 and not re.search(r"摘要|历年真题|试题|^[（(]|：|:", s):
            if re.search(r"模式|架构|设计|集成|平台|数据库|存储|可靠性|性能|维护|测试|安全|SOA|构件|UML", s):
                return s

    return re.sub(r"(_\d+)?$", "", fallback)


def pick_theme(topic: str, body: str) -> str:
    """
    先按论题判，再退回正文。
    论题里"论"之后的词才是真主题；把论题与正文混在一起匹配会被正文里的
    通用技术词带偏（例：论SOA技术的应用，正文提到"安全"就被判成信息安全）。
    """
    t = topic.replace(" ", "")
    for theme, pat in THEME_RULES:
        if re.search(pat, t):
            return theme
    return "99-未分类"


def get_abstract(text: str) -> str:
    m = re.search(r"摘\s*要[：:]\s*(.{80,600}?)(?=\n\s*\n|关键词|$)", text, re.S)
    return re.sub(r"\s+", " ", m.group(1)).strip() if m else ""


def main() -> int:
    pdfs = sorted(p for p in SRC.rglob("*.pdf") if "目录" not in p.name)
    print(f"待转换 {len(pdfs)} 个范文 PDF\n")

    for d in THEME_DIRS:
        (OUT / d).mkdir(parents=True, exist_ok=True)

    counters: dict[str, int] = {}
    report = []
    failed = []

    for pdf in pdfs:
        try:
            raw = extract_text(pdf)
        except Exception as e:
            failed.append((pdf.name, str(e)))
            print(f"  ✗ {pdf.name} 抽取失败: {e}")
            continue

        text = clean(raw)
        if len(text) < 400:
            failed.append((pdf.name, f"正文过短（{len(text)} 字）"))
            print(f"  ✗ {pdf.name} 正文过短，跳过")
            continue

        topic = get_topic(text, pdf.stem)
        theme = pick_theme(topic, text)
        abstract = get_abstract(text)
        n_abs = len(abstract)
        n_body = len(re.sub(r"\s", "", text))

        # 模板 / 技巧类文档单独标注 —— 它们不含真实项目内容，不能当范文背
        if "模板" in pdf.name:
            doc_kind = "模板"
        elif "技巧" in pdf.name:
            doc_kind = "提纲"
        else:
            doc_kind = "范文"

        counters[theme] = counters.get(theme, 0) + 1
        seq = counters[theme]
        safe_topic = re.sub(r'[\\/:*?"<>|]', "-", topic)[:40]
        theme_dir = dir_for(theme)
        dest = OUT / theme_dir / f"{seq:03d}-{safe_topic}.md"

        fm = [
            "---",
            f"范文类型: {doc_kind}",
            f"论题: {topic}",
            "对应年份: 未知",
            "对应考期: 未知",
            f"主题: {theme}",
            f"字数: {n_body}",
            "是否考场原文: false",
            f"出处: Gitee CTO说/系统架构设计师（{pdf.parent.name}）",
            "URL: https://gitee.com/zaonai/system_architect_old",
            "抓取日期: 2026-10-11",
            "校对状态: 待校对",
            "---",
            "",
            f"# {topic}",
            "",
            "> **来源**：Gitee「CTO说/系统架构设计师」备考资源库，MIT 协议。",
        ]
        if doc_kind == "范文":
            fm += [
                "> ⚠️ **是否考场原文：无法确证** → 按保守口径标 `false`。",
                "> 公开流传的「范文」多来自机构或个人整理，题目真实但文章未必是考场答卷，",
                "> **建议只学行文结构与论证方式，不要当作得分样本**。",
            ]
        else:
            fm += [
                f"> ⚠️ **本文不是范文，是「{doc_kind}」类文档** —— 用于学结构、评分要点与写作套路，",
                "> **不含真实项目内容，不能当范文背诵**。",
            ]
        fm += [f"> 原始文件：`{pdf.name}`", "", "---", ""]
        if abstract:
            fm += ["## 摘要", "", abstract, "", "---", ""]
        fm += ["## 正文", "", text, ""]

        dest.write_text("\n".join(fm), encoding="utf-8")
        report.append({"file": str(dest.relative_to(OUT)).replace("\\", "/"),
                       "topic": topic, "theme": theme, "chars": n_body,
                       "source_pdf": pdf.name})
        print(f"  ✓ [{theme}] {topic}  ({n_body} 字)")

    (OUT.parent / "essay_import_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n转换成功 {len(report)} 篇")
    if failed:
        print(f"失败 {len(failed)} 篇：")
        for n, r in failed:
            print(f"    {n} -> {r}")
    print("\n主题分布：")
    for d in THEME_DIRS:
        c = counters.get(d[3:], 0)
        if c:
            print(f"    {d}: {c} 篇")
    return 0


if __name__ == "__main__":
    sys.exit(main())
