# -*- coding: utf-8 -*-
"""
论文范文格式重构：把 PDF 抽取造成的「整坨正文」还原成可读的段落结构。

要解决的三个问题（实测出来的）：
  1. PDF 硬换行 —— 每行只有 20—30 字，一段话被切成十几行
  2. 广告水印混入正文 —— 「软考达人」「ruankaodaren」「手机端题库」等
  3. 没有段落分隔 —— 「摘要：」「正文：」只是纯文本标签，不是标题

重建策略：
  - 删水印行
  - 把整段文字**先合并再重切**：合并所有硬换行 → 按句子切分 → 按话语标记/长度重组成段落
  - 「摘要：」「正文：」提升为 ## 标题

用法：
  python _脚本\\rebuild_format.py --dry-run      # 预览（不写文件）
  python _脚本\\rebuild_format.py                # 实际改写
  python _脚本\\rebuild_format.py --file <路径>  # 只处理单个文件
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ESSAY_DIR = ROOT / "03-论文范文"

# 广告/水印行（整行匹配即删除）
WATERMARK_PAT = re.compile(
    r"软考达人|ruankaodaren|手机端题库|PC\s*端题库|微信搜索|软考专业备考平台|"
    r"免费提供\s*\d+\s*w\*?\+?\s*软考题库|1TB\s*免费专业备考资料|"
    r"扫码|公众号|第\s*\d+\s*页\s*共"
)

# 段落起始标记（强）：出现在句首时倾向另起一段
PARA_CUES = (
    "首先", "其次", "再次", "然后", "接着", "最后", "此外", "另外", "同时",
    "与此同时", "因此", "所以", "因而", "于是", "综上", "总之", "总而言之",
    "总的来说", "但是", "然而", "不过", "尽管", "本人", "我在", "我作为",
    "我担任", "我负责", "我们", "该项目", "本项目", "该系统", "该项目组",
    "第一", "第二", "第三", "第四", "其一", "其二", "其三",
    "目前", "当前", "近年来", "随着", "具体来说", "具体而言", "例如", "比如",
    "一方面", "另一方面", "值得注意", "实践证明", "通过", "采用", "为",
)

# 句子结束符
SENT_END = "。！？；"


def split_frontmatter(text: str) -> tuple[list[str], str]:
    """返回 (frontmatter 行列表, 正文)。"""
    lines = text.lstrip("\ufeff").split("\n")
    if not lines or lines[0].strip() != "---":
        return [], text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[: i + 1], "\n".join(lines[i + 1:])
    return [], text


def is_watermark(line: str) -> bool:
    return bool(WATERMARK_PAT.search(line))


def join_lines(lines: list[str]) -> str:
    """把硬换行合并成连续文本。中文直接拼接，英文/数字之间补空格。"""
    out: list[str] = []
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if not out:
            out.append(s)
            continue
        prev = out[-1]
        # 上一行以英文/数字结尾，且这一行以英文/数字开头 → 补空格
        if re.search(r"[A-Za-z0-9]$", prev) and re.match(r"^[A-Za-z0-9]", s):
            out[-1] = prev + " " + s
        else:
            out[-1] = prev + s
    text = " ".join(out) if False else (out[0] if out else "")
    # 上面只是拼接；这里取合并后的整体
    text = ""
    for i, s in enumerate(out):
        if i == 0:
            text = s
        else:
            text = text  # 已在循环内合并，理论上 out 只有一项
    return out[0] if len(out) == 1 else "".join(out)


def merge_wrapped(lines: list[str]) -> str:
    """合并硬换行：逐行拼接，必要时补空格。"""
    buf = ""
    for ln in lines:
        s = ln.strip()
        if not s:
            continue
        if not buf:
            buf = s
        elif re.search(r"[A-Za-z0-9]$", buf) and re.match(r"^[A-Za-z0-9]", s):
            buf += " " + s
        else:
            buf += s
    return buf


def split_sentences(text: str) -> list[str]:
    """按中文句末标点切句，保留标点。"""
    parts = re.split(r"(?<=[。！？；])", text)
    return [p.strip() for p in parts if p.strip()]


def regroup_paragraphs(sentences: list[str], min_len: int = 100, max_len: int = 320) -> list[str]:
    """
    把句子重新组合成段落：
      - 当前段落已达 min_len 且下一句以话语标记开头 → 另起一段
      - 当前段落超过 max_len → 在句边界强制断开
    """
    paras: list[str] = []
    cur = ""
    for s in sentences:
        if not cur:
            cur = s
            continue
        starts_cue = any(s.startswith(c) for c in PARA_CUES)
        if (len(cur) >= min_len and starts_cue) or len(cur) >= max_len:
            paras.append(cur)
            cur = s
        else:
            cur += s
    if cur:
        paras.append(cur)
    return paras


def normalize_spaces(s: str) -> str:
    """压缩多余空格：汉字之间去空格，中英文之间保留单空格。"""
    s = re.sub(r"[ \t\u3000]+", " ", s)
    s = re.sub(r"(?<=[\u4e00-\u9fff]) (?=[\u4e00-\u9fff])", "", s)
    s = re.sub(r"(?<=[\u4e00-\u9fff]) (?=[，。；：、？！（）【】《》])", "", s)
    s = re.sub(r"(?<=[，。；：、？！（）【】《》]) (?=[\u4e00-\u9fff])", "", s)
    return s.strip()


def rebuild_body(body: str, topic: str) -> str:
    """
    重建正文结构。

    **按行判断结构标记**，不用全文正则 —— 否则 `## 正文` 里的「正文」二字
    会被当成标记，产生空标题之类的错乱（这是实测踩过的坑）。
    """
    raw = body.split("\n")

    # 1) 删水印
    raw = [ln for ln in raw if not is_watermark(ln)]

    # 2) 删掉上一版导入留下的 ## 摘要 / ## 正文 / 分隔线（本函数会重新生成）
    cleaned: list[str] = []
    for ln in raw:
        s = ln.strip()
        if re.fullmatch(r"#{2,3}\s*(摘要|正文)", s):
            continue
        if s == "---":
            continue
        cleaned.append(ln)
    raw = cleaned

    # 3) 保留开头的 # 标题 与 > 来源引用块
    head: list[str] = []
    i = 0
    while i < len(raw):
        s = raw[i].strip()
        if s.startswith("# ") or s.startswith(">") or s == "":
            head.append(raw[i])
            i += 1
        else:
            break
    rest_lines = raw[i:]

    # 4) 逐行分类。标记只认「整行就是 摘要 / 摘要：xxx / 正文 / 正文：xxx」
    SECTION = re.compile(
        r"^(?:【\s*(摘要|正文)\s*】|(摘要|正文))\s*[:：]?\s*(.*)$"
    )

    sections: list[tuple[str, list[str]]] = []
    cur_title = ""
    cur: list[str] = []

    def flush() -> None:
        nonlocal cur_title, cur
        txt = "\n".join(cur).strip()
        if txt:
            sections.append((cur_title, txt.split("\n")))
        cur = []

    first_content = True
    for ln in rest_lines:
        s = ln.strip()
        if s and first_content:
            # 跳过重复的论题标题行
            # 跳过重复的论题标题行。用「去掉全部空白」比对：
            # 缩写里常有空格（论 UP / 论 SOA / 论基于 UML），只压缩空格会漏判
            if re.sub(r"\s+", "", s) == re.sub(r"\s+", "", topic):
                first_content = False
                continue
            first_content = False

        m = SECTION.match(s) if s else None
        if m:
            # 只有「行首即标记且标记后是同句内容或为空」才算章节标题，
            # 避免把正文里出现的「正文……」当成标题
            marker = m.group(1) or m.group(2)
            tail = m.group(3) or ""
            if marker and (not tail or not re.match(r"^[，。；、]", tail)):
                flush()
                cur_title = marker
                if tail:
                    cur.append(tail)
                continue
        cur.append(ln)
    flush()

    # 5) 生成
    blocks: list[str] = []
    for title, ls in sections:
        merged = normalize_spaces(merge_wrapped(ls))
        if not merged:
            continue
        if title:
            blocks.append(f"## {title}")
            blocks.append("")
        if title == "摘要":
            # 软考摘要通常 250—300 字、单段。超过 420 字才拆，避免破坏规范结构
            paras = ([merged] if len(merged) <= 420
                     else regroup_paragraphs(split_sentences(merged),
                                             min_len=200, max_len=420))
        else:
            paras = regroup_paragraphs(split_sentences(merged))
        for p in paras:
            blocks.append(p)
            blocks.append("")

    out_head = "\n".join(head).rstrip()
    if not blocks:
        return out_head + "\n"
    return out_head + "\n\n---\n\n" + "\n".join(blocks).rstrip() + "\n"



def needs_rebuild(path: Path) -> tuple[bool, str]:
    """判断是否需要重构，并给出原因。"""
    text = path.read_text(encoding="utf-8", errors="replace")
    fm, body = split_frontmatter(text)
    lines = [ln for ln in body.split("\n") if ln.strip()]
    if not lines:
        return False, "空"
    wm = sum(1 for ln in lines if is_watermark(ln))
    if wm:
        return True, f"含水印 {wm} 行"
    blank = sum(1 for ln in body.split("\n") if not ln.strip())
    total = len(body.split("\n"))
    ratio = blank / max(1, total)
    if ratio < 0.10:
        return True, f"空行占比 {ratio:.0%}（段落粘连）"
    return False, f"空行占比 {ratio:.0%}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只预览，不写文件")
    ap.add_argument("--file", help="只处理指定文件")
    ap.add_argument("--show", type=int, default=1, help="dry-run 时展示几个文件的预览")
    args = ap.parse_args()

    if args.file:
        targets = [Path(args.file)]
    else:
        targets = sorted(
            p for p in ESSAY_DIR.rglob("*.md")
            if not p.name.startswith("00-") and p.name != "README.md"
        )

    todo: list[tuple[Path, str]] = []
    for p in targets:
        ok, why = needs_rebuild(p)
        if ok:
            todo.append((p, why))

    print(f"扫描 {len(targets)} 篇，需重构 {len(todo)} 篇\n")
    for p, why in todo:
        print(f"  {p.parent.name}/{p.name}  ← {why}")

    if not todo:
        print("\n无需重构。")
        return 0

    if args.dry_run:
        print(f"\n{'='*70}\n预览前 {args.show} 篇\n{'='*70}")
        for p, _ in todo[: args.show]:
            text = p.read_text(encoding="utf-8")
            fm, body = split_frontmatter(text)
            topic = "未知"
            for ln in fm:
                if ln.startswith("论题:"):
                    topic = ln.split(":", 1)[1].strip()
            new = rebuild_body(body, topic)
            print(f"\n--- {p.name} 重构后（第 1—45 行）---")
            for ln in new.split("\n")[:45]:
                print(ln)
        print(f"\n（dry-run：未写入任何文件）")
        return 0

    changed = 0
    for p, _ in todo:
        text = p.read_text(encoding="utf-8")
        fm, body = split_frontmatter(text)
        topic = "未知"
        for ln in fm:
            if ln.startswith("论题:"):
                topic = ln.split(":", 1)[1].strip()
        new_body = rebuild_body(body, topic)
        if fm:
            new = "\n".join(fm) + "\n" + new_body
        else:
            new = new_body
        p.write_text(new, encoding="utf-8")
        changed += 1
        print(f"  ✓ 重构 {p.name}")

    print(f"\n完成：改写 {changed} 篇")
    return 0


if __name__ == "__main__":
    sys.exit(main())
