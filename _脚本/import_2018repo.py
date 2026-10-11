# -*- coding: utf-8 -*-
"""
把 yjian180/2018_system_architect 的真题 PDF 转成本知识库的 Markdown。

为什么用这个源而不用 Gitee 那批：
  这批 PDF **全部含文本层**（实测 28/28），可逐字抽取；
  Gitee 那批同类内容是扫描图，OCR 输出乱码不可用。

输入：_staging/yjian180_sa2018/<年份>年/*.pdf
     优先取「科目一：综合知识」「科目二：案例分析」；
     「综合版」是把科目一+科目二合并，与上面重复，跳过。
输出：_staging/imported2/01-真题-按年份/YYYY-下半年/YYYY-下半年-<科目>.md
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_staging" / "yjian180_sa2018"
OUT = ROOT / "_staging" / "imported2" / "01-真题-按年份"

# 这批源只有下半年（2009—2017 年系统架构设计师仅下半年开考）
SESSION = "下半年"

SUBJECT_KEY = {"综合知识": "综合知识", "案例分析": "案例分析"}
ITEM_TYPE = {"综合知识": "选择题", "案例分析": "案例题"}

TAG_RULES: list[tuple[str, list[str]]] = [
    ("架构评估", ["ATAM", "SAAM", "CBAM", "效用树", "敏感点", "权衡点", "架构评估", "体系结构评估"]),
    ("质量属性", ["质量属性", "可用性", "可修改性", "可测试性", "易用性", "互操作性", "鲁棒性"]),
    ("架构风格", ["架构风格", "管道", "过滤器", "黑板", "隐式调用", "解释器", "事件驱动", "批处理", "分层", "C/S", "B/S", "仓库风格", "面向对象"]),
    ("架构设计", ["架构设计", "体系结构设计", "ABSD", "DSSA", "特定领域"]),
    ("架构演化", ["演化", "遗留", "重构", "改造"]),
    ("微服务", ["微服务"]),
    ("云原生", ["云原生", "容器", "虚拟化"]),
    ("SOA", ["SOA", "面向服务", "Web服务", "Web 服务", "ESB"]),
    ("企业应用集成", ["应用集成", "企业集成", "中间件", "EAI", "集成平台"]),
    ("基于构件", ["构件", "复用"]),
    ("设计模式", ["设计模式", "单例", "工厂模式", "装饰", "观察者", "策略模式", "适配器"]),
    ("UML", ["UML", "用例图", "类图", "顺序图", "活动图", "状态图", "部署图"]),
    ("软件工程", ["生命周期", "瀑布", "螺旋", "增量模型", "喷泉", "V模型", "V 模型", "敏捷", "RUP", "需求分析", "结构化"]),
    ("软件测试", ["测试", "黑盒", "白盒", "边界值", "等价类", "因果图", "判定表", "回归"]),
    ("软件维护", ["软件维护", "可维护性"]),
    ("软件过程", ["CMM", "CMMI", "能力成熟度", "软件过程"]),
    ("软件可靠性", ["可靠性", "MTBF", "MTTR", "MTTF", "容错", "避错", "检错", "失效"]),
    ("容灾与高可用", ["容灾", "高可用", "RTO", "RPO", "负载均衡", "限流", "熔断", "降级"]),
    ("信息安全", ["安全", "加密", "数字签名", "数字证书", "认证", "访问控制", "防火墙", "病毒", "入侵", "密钥"]),
    ("计算机系统", ["Cache", "流水线", "海明码", "CRC", "校验", "浮点", "存储", "磁盘", "指令", "CPU", "总线"]),
    ("操作系统", ["操作系统", "进程", "线程", "死锁", "银行家", "页面置换", "调度", "PV操作", "信号量", "中断", "文件系统", "索引节点", "分页", "分段"]),
    ("数据库", ["数据库", "范式", "函数依赖", "ER图", "E-R", "事务", "并发控制", "索引", "关系模式", "数据仓库", "OLAP", "分布式数据库"]),
    ("NoSQL", ["NoSQL", "Redis", "MongoDB", "HBase", "列族", "键值"]),
    ("大数据架构", ["大数据", "Hadoop", "HDFS", "MapReduce", "数据仓库", "数据挖掘"]),
    ("计算机网络", ["网络", "OSI", "TCP", "IP地址", "子网", "路由", "交换机", "802.11", "域名"]),
    ("嵌入式", ["嵌入式", "实时", "RTOS", "优先级"]),
    ("人工智能", ["人工智能", "神经网络", "专家系统", "机器学习", "数据挖掘", "知识库"]),
    ("项目管理", ["关键路径", "PERT", "挣值", "工期", "进度", "成本"]),
    ("法律法规", ["著作权", "专利", "商标", "知识产权"]),
    ("标准化", ["标准化", "GB/T", "ISO", "国家标准"]),
    ("专业英语", ["English", "The ", "which of the following"]),
    ("数学与逻辑", ["最小生成树", "定义域", "排列组合", "概率"]),
]

GENERIC = "软件工程"


def extract_text(pdf: Path) -> str:
    doc = pymupdf.open(str(pdf))
    try:
        return "\n".join(p.get_text() or "" for p in doc)
    finally:
        doc.close()


def clean(text: str) -> str:
    """
    清理 PDF 抽取噪声。

    两个针对性处理（都是实测出来的）：
      1. 中文排版里汉字与标点之间不应有空格，而 PDF 抽取常插入空格 → 压缩
      2. PDF 常把「题号」单独抽成一行（`1.` 换行后才接题干）→ 与下一行合并，
         否则题号行与题干行脱节，题量统计和标签提取都会失真
    """
    t = text.replace("\r\n", "\n").replace("\r", "\n")
    # 去掉独占一行的页眉 URL
    t = re.sub(r"^\s*https?://\S+\s*$", "", t, flags=re.M)

    # ① 把「只有题号的短行」与下一行合并
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

    # ② 汉字之间、汉字与标点之间的空格压缩
    t = re.sub(r"(?<=[\u4e00-\u9fff])[ \t]+(?=[\u4e00-\u9fff])", "", t)
    t = re.sub(r"(?<=[\u4e00-\u9fff])[ \t]+(?=[，。；：、？！（）【】《》""''])", "", t)
    t = re.sub(r"(?<=[，。；：、？！（）【】《》""''])[ \t]+(?=[\u4e00-\u9fff])", "", t)
    t = re.sub(r"(?<=[\u4e00-\u9fff])[ \t]+(?=[．.,;:!?()\[\]])", "", t)
    t = re.sub(r"(?<=[．.,;:!?()\[\]])[ \t]+(?=[\u4e00-\u9fff])", "", t)
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


def count_items(subject: str, body: str) -> int:
    """题量：数形如「N.」的题干起始行。"""
    nums = re.findall(r"^\s*(\d{1,3})[.．、]\s*", body, re.M)
    if not nums:
        return 0
    # 取最大值作为题量（比计数更稳，避免选项编号混入）
    return max(int(n) for n in nums if int(n) <= 200)


def extract_tags(body: str, valid: set[str], limit: int = 5) -> list[str]:
    heads = re.findall(r"^\s*\d{1,3}[.．、][^\n]*$", body, re.M)
    def sc(scope: str) -> dict[str, float]:
        if not scope.strip():
            return {}
        norm = max(1.0, len(scope) / 1000.0)
        out = {}
        for tag, kws in TAG_RULES:
            n = sum(scope.count(k) for k in kws)
            if n:
                out[tag] = n / norm
        return out
    a = [t for t, _ in sorted(sc("\n".join(heads)).items(), key=lambda x: -x[1]) if t in valid]
    b = [t for t, _ in sorted(sc(body).items(), key=lambda x: -x[1]) if t in valid]
    out: list[str] = []
    for i in range(max(len(a), len(b))):
        if i < len(a) and a[i] not in out:
            out.append(a[i])
        if i < len(b) and b[i] not in out:
            out.append(b[i])
    return out[:limit] or [GENERIC]


def load_valid_tags() -> set[str]:
    f = ROOT / "00-元数据" / "考点标签词表.md"
    return set(re.findall(r"`([^`]+)`", f.read_text(encoding="utf-8"))) if f.exists() else set()


def main() -> int:
    valid = load_valid_tags()
    rows: list[tuple[int, str, Path]] = []

    for ydir in sorted(SRC.glob("[0-9][0-9][0-9][0-9]年")):
        year = int(ydir.name[:4])
        for pdf in sorted(ydir.glob("*.pdf")):
            name = pdf.name
            if "综合版" in name or "综合" not in name and "案例分析" not in name:
                # 综合版与科目一/二重复；其他排除
                if "综合版" in name:
                    continue
            if "科目一" in name or "综合知识" in name:
                rows.append((year, "综合知识", pdf))
            elif "科目二" in name or "案例分析" in name:
                rows.append((year, "案例分析", pdf))

    print(f"待转换 {len(rows)} 份（{len({r[0] for r in rows})} 个年份 × 2 科）\n")

    report = []
    for year, subject, pdf in sorted(rows):
        try:
            text = clean(extract_text(pdf))
        except Exception as e:
            print(f"  ✗ {year} {subject}: {e}")
            continue
        if len(text) < 500:
            print(f"  ✗ {year} {subject} 正文过短（{len(text)} 字），跳过")
            continue

        n = count_items(subject, text)
        tags = extract_tags(text, valid)
        has_ans = bool(re.search(r"(参考答案|答案[:：]|正确答案)", text))

        dest_dir = OUT / f"{year}-{SESSION}"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{year}-{SESSION}-{subject}.md"

        fm = [
            "---",
            f"年份: {year}",
            f"考期: {SESSION}",
            f"科目: {subject}",
            f"题量: {n}",
            f"题目类型: {ITEM_TYPE[subject]}",
            "来源类型: 回忆版",
            "是否官方: false",
            f"含答案: {'true' if has_ans else 'false'}",
            f"答案可信度: {'中' if has_ans else '存疑'}",
            f"含解析: {'true' if has_ans else 'false'}",
            f"考点标签: [{', '.join(tags)}]",
            "出处: GitHub yjian180/2018_system_architect",
            "URL: https://github.com/yjian180/2018_system_architect",
            "抓取日期: 2026-10-11",
            "校对状态: 待校对",
            "---",
            "",
            f"# {year} 年{SESSION}系统架构设计师 {subject}",
            "",
            "> **来源**：GitHub `yjian180/2018_system_architect`，个人整理的历年真题汇编，非官方。",
            "> 该源为**纯文本 PDF**（非扫描图），本文件由 `_脚本/import_2018repo.py` 逐字抽取生成，",
            "> 仅对 PDF 抽取造成的多余空格做了压缩，**未改写题面内容**。",
            f"> 原始文件：`{pdf.name}`",
            "",
            f"> ⚠️ **该源本身不完整**：本卷题号从 1 连续编到 {n}，**无缺号**，",
            f"> 说明源 PDF 只收录了 {n} 题（综合知识实际应为 75 题）。",
            "> 缺失部分需另找来源补齐，**不要把本文件的题量当作该年真实题量**。",
            "",
            "> ⚠️ **另有排版缺陷**：PDF 抽取把部分句子在行尾切断（如「分为三个独立的」换行接「进程」），",
            "> 以及原书排印错误（如选项 D 的「应该软件」应为「应用软件」）。",
            "> **使用时应把它当作检索与复习线索，重要结论请回到原卷核对。**",
            "",
            "---",
            "",
            text,
            "",
        ]
        dest.write_text("\n".join(fm), encoding="utf-8")
        report.append({"file": str(dest.relative_to(OUT)).replace("\\", "/"),
                       "year": year, "subject": subject, "items": n,
                       "tags": tags, "has_answer": has_ans,
                       "chars": len(re.sub(r"\s", "", text))})
        print(f"  ✓ {year} {subject}  题量≈{n}  {len(re.sub(r'\\s','',text))} 字  标签={','.join(tags)}")

    (OUT.parent / "import2_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n写入 {len(report)} 份")
    return 0


if __name__ == "__main__":
    sys.exit(main())
