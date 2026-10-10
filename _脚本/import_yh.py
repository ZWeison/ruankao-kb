# -*- coding: utf-8 -*-
"""
把 YoungHong1992 清理稿转换成本知识库的元数据格式。

输入：_staging/yh2024/content/02-历年真题-清洗版/*.md
输出：_staging/imported/01-真题-按年份/YYYY-考期/YYYY-考期-科目.md（先落暂存，核对后再入库）

设计原则：
- 正文逐字保留（含来源附加的"备考提示"，那是有价值的参考内容，不删）
- 头部按本库《元数据规范》重建为 15 个字段
- 考点标签用关键词命中法自动提取（保守：只认明确出现的技术名词）
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "_staging" / "yh2024" / "content" / "02-历年真题-清洗版"
OUT = ROOT / "_staging" / "imported" / "01-真题-按年份"

SUBJECT_MAP = {
    "comprehensive": ("综合知识", "选择题"),
    "case-analysis": ("案例分析", "案例题"),
    "essay": ("论文", "论文题"),
}
SESSION_MAP = {"h1": "上半年", "h2": "下半年"}

# 关键词 → 考点标签（只用明确的技术名词，避免误标）
TAG_RULES: list[tuple[str, list[str]]] = [
    ("架构评估", ["ATAM", "SAAM", "CBAM", "效用树", "敏感点", "权衡点", "风险点", "架构评估"]),
    ("质量属性", ["质量属性", "可用性", "可修改性", "可测试性", "易用性", "互操作性", "鲁棒性", "ISO 25010"]),
    ("架构风格", ["架构风格", "管道", "过滤器", "黑板", "隐式调用", "解释器", "事件驱动", "批处理", "层次式", "分层架构", "C/S", "B/S", "仓库风格"]),
    ("ABSD", ["ABSD", "基于架构的软件", "架构驱动"]),
    ("DSSA", ["DSSA", "特定领域软件", "领域字典"]),
    ("架构演化", ["架构演化", "绞杀者", "防腐层", "遗留系统", "上云", "6R", "迁移"]),
    ("微服务", ["微服务", "限界上下文", "DDD", "服务拆分", "服务治理"]),
    ("云原生", ["云原生", "容器", "Kubernetes", "K8s", "Service Mesh", "服务网格", "不可变基础设施", "声明式API"]),
    ("SOA", ["SOA", "面向服务", "ESB", "企业服务总线", "BPEL", "Web Service", "服务编排", "服务编制"]),
    ("Serverless", ["Serverless", "无服务器", "FaaS", "冷启动", "12-Factor"]),
    ("DevOps", ["DevOps", "CI/CD", "持续集成", "持续交付", "持续部署", "蓝绿", "金丝雀", "灰度", "IaC", "GitOps", "DORA"]),
    ("企业应用集成", ["企业应用集成", "EAI", "集成平台", "中间件", "MOM", "ORB", "TPM", "RPC", "集成模式"]),
    ("基于构件", ["构件", "CBSD", "软件复用", "复用", "构件组装"]),
    ("设计模式", ["设计模式", "单例模式", "工厂模式", "装饰模式", "观察者模式", "策略模式", "适配器模式", "GoF", "SOLID"]),
    ("UML", ["UML", "用例图", "类图", "顺序图", "活动图", "状态图", "部署图", "泛化", "包含关系", "扩展关系"]),
    ("软件工程", ["生命周期", "瀑布", "螺旋模型", "增量模型", "喷泉模型", "V 模型", "V模型", "敏捷", "RUP", "统一过程", "需求分析", "结构化分析"]),
    ("软件测试", ["测试", "黑盒", "白盒", "边界值", "等价类", "因果图", "判定表", "冒烟", "回归测试", "单元测试", "集成测试", "测试左移"]),
    ("软件维护", ["软件维护", "可维护性", "完善性维护", "适应性维护", "改正性维护", "预防性维护"]),
    ("软件过程", ["CMMI", "DO-178", "能力成熟度", "软件过程"]),
    ("软件可靠性", ["可靠性", "MTBF", "MTTR", "MTTF", "容错", "避错", "检错", "N版本", "失效", "故障率"]),
    ("容灾与高可用", ["容灾", "高可用", "RTO", "RPO", "两地三中心", "主备", "双活", "限流", "熔断", "降级", "舱壁", "负载均衡"]),
    ("信息安全", ["安全", "加密", "对称加密", "非对称加密", "数字签名", "数字证书", "PKI", "认证", "访问控制", "DDoS", "SQL注入", "XSS", "CSRF", "等保", "WAF", "防火墙", "入侵检测", "SSL", "WPA", "RBAC", "审计"]),
    ("计算机系统", ["Cache", "流水线", "海明码", "CRC", "校验", "浮点", "存储", "磁盘", "总线", "指令", "CPU", "DSP"]),
    ("操作系统", ["操作系统", "进程", "线程", "死锁", "银行家算法", "页面置换", "调度", "PV操作", "临界区", "中断", "文件系统", "索引节点", "虚拟存储", "分段", "分页"]),
    ("数据库", ["数据库", "范式", "函数依赖", "ER图", "E-R", "事务", "并发控制", "索引", "自然连接", "关系模式", "数据仓库", "OLAP", "OLTP", "分库分表", "读写分离"]),
    ("NoSQL", ["NoSQL", "Redis", "MongoDB", "HBase", "列族", "键值", "图数据库", "CAP"]),
    ("大数据架构", ["大数据", "Hadoop", "HDFS", "MapReduce", "Spark", "数据湖", "数据中台", "数仓"]),
    ("Lambda架构", ["Lambda", "批处理层", "加速层", "服务层"]),
    ("Kappa架构", ["Kappa"]),
    ("湖仓一体", ["湖仓"]),
    ("计算机网络", ["网络", "OSI", "TCP", "IP", "子网", "路由", "交换机", "802.11", "域名", "DNS", "HTTP"]),
    ("嵌入式", ["嵌入式", "实时", "RTOS", "优先级反转", "RMS", "EDF", "可调度"]),
    ("区块链", ["区块链", "智能合约", "共识", "溯源"]),
    ("知识图谱", ["知识图谱", "本体", "知识表示", "图数据库"]),
    ("人工智能", ["人工智能", "神经网络", "深度学习", "机器学习", "Transformer", "大模型", "多模态", "无监督", "监督学习", "强化学习", "专家系统", "RAG", "知识库", "倒排索引"]),
    ("项目管理", ["关键路径", "PERT", "挣值", "工期", "进度", "成本管理", "风险管理"]),
    ("法律法规", ["著作权", "专利", "商标", "知识产权", "优先权", "计算机软件保护条例"]),
    ("标准化", ["标准化", "GB/T", "ISO 标准", "国家标准"]),
    ("专业英语", ["English", "Multi-agent", "The ", "which of the following"]),
    ("数学与逻辑", ["最小生成树", "定义域", "排列组合", "概率", "线性规划"]),
    ("边缘计算", ["边缘计算", "雾计算", "云边协同"]),
]

GENERIC_TAG = "软件工程"


def split_fm(text: str) -> tuple[dict, str]:
    text = text.lstrip("\ufeff")
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    block, body = text[3:end].strip("\n"), text[end + 4:].lstrip("\n")
    data = {}
    for line in block.splitlines():
        if ":" in line:
            k, _, v = line.partition(":")
            data[k.strip()] = v.strip().strip('"')
    return data, body


def count_items(subject_key: str, body: str) -> int:
    """题量：优先读来源自述的『题目数量/主试题数量』，其次数标题。"""
    m = re.search(r"题目数量：\**\s*(\d+)", body)
    if m:
        return int(m.group(1))
    m = re.search(r"主试题数量：\**\s*(\d+)", body)
    if m:
        return int(m.group(1))
    if subject_key == "comprehensive":
        # 既可能是 "### 第N题"，也可能是 "## 第N-M题" 分组标题
        n = len(re.findall(r"^### 第\d+题\s*$", body, re.M))
        if n:
            return n
        total = 0
        for a, b in re.findall(r"^## 第(\d+)[-—~](\d+)题", body, re.M):
            total += int(b) - int(a) + 1
        if total:
            return total
        return len(re.findall(r"^## 第\d+题", body, re.M))
    return len(re.findall(r"^## 试题[一二三四五六七八九十]", body, re.M))


def extract_tags(body: str, valid: set[str], subject_key: str, limit: int = 5) -> list[str]:
    """
    双通道标签提取（不依赖各科目的区块结构，避免结构一变就整体失效）：

      通道 A「结构标题」：试题标题、题目分组标题 —— 反映命题点
      通道 B「全文密度」：整篇关键词命中密度 —— 反映贯穿全卷的主体考点

    两通道各自按长度归一排序后**交错**取前 N 个。
    只做长度归一，不额外惩罚长文本（案例分析含教材原文是正常的）。
    """
    heads = re.findall(r"^#{2,4}\s*[^\n]*$", body, re.M)

    def score(scope: str) -> dict[str, float]:
        if not scope.strip():
            return {}
        norm = max(1.0, len(scope) / 1000.0)
        out: dict[str, float] = {}
        for tag, kws in TAG_RULES:
            n = sum(scope.count(k) for k in kws)
            if n:
                out[tag] = n / norm
        return out

    sa = score("\n".join(heads))
    sb = score(body)
    order_a = [t for t, _ in sorted(sa.items(), key=lambda x: -x[1]) if t in valid]
    order_b = [t for t, _ in sorted(sb.items(), key=lambda x: -x[1]) if t in valid]

    interleaved: list[str] = []
    for i in range(max(len(order_a), len(order_b))):
        if i < len(order_a) and order_a[i] not in interleaved:
            interleaved.append(order_a[i])
        if i < len(order_b) and order_b[i] not in interleaved:
            interleaved.append(order_b[i])
    return interleaved[:limit] or [GENERIC_TAG]


def load_valid_tags() -> set[str]:
    f = ROOT / "00-元数据" / "考点标签词表.md"
    return set(re.findall(r"`([^`]+)`", f.read_text(encoding="utf-8"))) if f.exists() else set()


def main() -> int:
    valid = load_valid_tags()
    files = sorted(p for p in SRC.glob("*.md") if p.name != "INDEX.md")
    print(f"源文件 {len(files)} 份；词表 {len(valid)} 个标签\n")

    # 预扫：找出「同 年份+考期+科目」有多份的组 —— 那必然是独立回忆版，必须区分
    groups: dict[tuple, list[Path]] = {}
    parsed: dict[Path, dict] = {}
    for p in files:
        fm, body = split_fm(p.read_text(encoding="utf-8", errors="replace"))
        year = int(fm.get("year", 0))
        session = SESSION_MAP.get(fm.get("session", ""), "")
        subject_key = fm.get("subject", "")
        if not (year and session and subject_key in SUBJECT_MAP):
            continue
        parsed[p] = {"year": year, "session": session,
                     "subject_key": subject_key, "body": body}
        groups.setdefault((year, session, subject_key), []).append(p)

    collisions = {k: v for k, v in groups.items() if len(v) > 1}
    if collisions:
        print("检测到多套独立版本（禁止合并，各自成文件）：")
        for k, v in collisions.items():
            print(f"  {k[0]} {k[1]} {SUBJECT_MAP[k[2]][0]}：{len(v)} 套")
            for p in v:
                print(f"      - {p.name}")
        print()

    OUT.mkdir(parents=True, exist_ok=True)
    report = []
    unknown = {}
    written = 0

    for p in files:
        if p not in parsed:
            print(f"  [跳过] 无法解析: {p.name}")
            continue
        d = parsed[p]
        year, session, subject_key, body = (
            d["year"], d["session"], d["subject_key"], d["body"])
        subject, item_type = SUBJECT_MAP[subject_key]

        # 版本标记：源文件名已有 → 用它；否则落在冲突组里 → 按题量区分 A/B
        variant = ""
        m = re.search(r"回忆版([A-Z])", p.stem)
        if m:
            variant = f"-回忆版{m.group(1)}"
        elif (year, session, subject_key) in collisions:
            n_probe = count_items(subject_key, body)
            variant = "-回忆版A" if n_probe <= 70 else "-回忆版B"

        n = count_items(subject_key, body)
        tags = extract_tags(body, valid, subject_key)
        for t in tags:
            if t not in valid:
                unknown[t] = unknown.get(t, 0) + 1

        has_answer = ("正确答案" in body) or ("参考答案" in body)

        # 重建正文：去掉源 # 标题（改用统一标题），保留其余
        lines = body.splitlines()
        body_clean = "\n".join(l for l in lines if not l.startswith("# "))
        body_clean = re.sub(r"\n{3,}", "\n\n", body_clean).strip()
        title = f"{year} 年{session} 系统架构设计师 {subject}{variant}"

        fm_out = [
            "---",
            f"年份: {year}",
            f"考期: {session}",
            f"科目: {subject}",
            f"题量: {n}",
            f"题目类型: {item_type}",
            "来源类型: 回忆版",
            "是否官方: false",
            f"含答案: {'true' if has_answer else 'false'}",
            f"答案可信度: {'中' if has_answer else '存疑'}",
            f"含解析: {'true' if has_answer else 'false'}",
            f"考点标签: [{', '.join(tags)}]",
            "出处: YoungHong1992/ruankao-senior-architecture-designer",
            "URL: https://github.com/YoungHong1992/ruankao-senior-architecture-designer",
            "抓取日期: 2026-10-11",
            "校对状态: 待校对",
            "---",
            "",
            f"# {title}",
            "",
            "> **来源**：YoungHong1992 备考知识库「清洗交叉校对版」，非官方。",
            "> 题面为公开回忆版/整理稿，答案非官方标准答案；使用前请对照原始资料。",
            "> **该来源正文自带「备考提示」，已原样保留** —— 属整理者补充内容，非试卷原文。",
            "",
            "---",
            "",
            body_clean,
            "",
        ]

        dest_dir = OUT / f"{year}-{session}"
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest = dest_dir / f"{year}-{session}-{subject}{variant}.md"
        dest.write_text("\n".join(fm_out), encoding="utf-8")
        written += 1
        report.append({"file": str(dest.relative_to(OUT)).replace("\\", "/"),
                       "year": year, "session": session, "subject": subject,
                       "items": n, "tags": tags, "has_answer": has_answer,
                       "body_chars": len(body_clean)})
        print(f"  ✓ {dest.relative_to(OUT)}  题量={n}  标签={','.join(tags)}")

    (OUT.parent / "import_report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\n写入 {written} 份")
    if unknown:
        print(f"\n⚠️ 未在词表中的标签（需补进 考点标签词表.md）：")
        for t, c in sorted(unknown.items(), key=lambda x: -x[1]):
            print(f"    {t}  (命中 {c} 卷)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
