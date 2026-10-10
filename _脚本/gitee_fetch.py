# -*- coding: utf-8 -*-
"""Gitee 目录遍历 + 下载（正确按 UTF-8 处理，避免 PowerShell 控制台编码问题）。"""
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

API = "https://gitee.com/api/v5/repos/{owner}/{repo}/contents"
OWNER, REPO = "zaonai", "system_architect"
UA = {"User-Agent": "Mozilla/5.0 (dsh)"}
STAGE = Path(r"D:\软考知识库\_staging\gitee")


def get(url: str, retries: int = 4):
    last = None
    for i in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.loads(r.read().decode("utf-8"))
        except Exception as e:
            last = e
            time.sleep(1.5 * (i + 1))
    print(f"    ! 失败 {url[:110]} -> {last}", flush=True)
    return None


def get_child(path: str, name_contains: str = ""):
    """按名字片段找子项（规避列目录接口的不稳定）。"""
    for e in list_dir(path):
        if e.get("type") == "dir" and name_contains in e.get("name", ""):
            return e
    return None


def list_dir(path: str):
    base = API.format(owner=OWNER, repo=REPO)
    url = f"{base}/{urllib.parse.quote(path)}" if path else base
    return get(url) or []


def walk(path: str, depth: int = 0, max_depth: int = 3, acc=None):
    """递归列出目录，返回条目列表。"""
    if acc is None:
        acc = []
    if depth > max_depth:
        return acc
    for item in list_dir(path):
        p = item.get("path", "")
        t = item.get("type")
        acc.append((depth, t, item.get("name", ""), p, item.get("size", 0)))
        if t == "dir" and depth < max_depth:
            walk(p, depth + 1, max_depth, acc)
    return acc


def encode_url(url: str) -> str:
    """
    Gitee 的 download_url 里中文路径是未编码的，urllib 会以 ASCII 编解码失败。
    这里只对 path/query 做百分号编码，保留 scheme://host。
    """
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parts.path, safe="/%")
    query = urllib.parse.quote(parts.query, safe="=&%")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def download(path: str) -> bool:
    """下载单个文件到 _staging/gitee/<path>。"""
    url = f"{API.format(owner=OWNER, repo=REPO)}/{urllib.parse.quote(path)}"
    meta = get(url)
    if not meta or "download_url" not in meta:
        return False
    dest = STAGE / path
    dest.parent.mkdir(parents=True, exist_ok=True)
    raw = encode_url(meta["download_url"])
    for i in range(3):
        try:
            req = urllib.request.Request(raw, headers=UA)
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            if data[:4] == b"<!DO" or data[:5] == b"<html":
                say("    ! 返回的是 HTML 而非文件（可能需要登录）")
                return False
            dest.write_bytes(data)
            return True
        except Exception as e:
            if i == 2:
                say(f"    ! 下载失败 {path[-40:]} -> {e}")
                return False
            time.sleep(2 * (i + 1))
    return False


def say(msg: str) -> None:
    """安全打印：控制台编码不支持时退化输出，绝不让打印异常中断下载。"""
    try:
        print(msg, flush=True)
    except Exception:
        print(msg.encode("ascii", "replace").decode("ascii"), flush=True)


EXAM_DIR = "03、历年真题(2009年-2025年)+答案解析"
ESSAY_DIR = "04、论文（真题范文+写作）"
# 排除知网学术论文（第三方版权，不入库）
SKIP_PATTERNS = ("知网参考",)

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else "list"
    which = sys.argv[2] if len(sys.argv) > 2 else "essay"
    target = EXAM_DIR if which == "exam" else ESSAY_DIR
    maxd = int(sys.argv[3]) if len(sys.argv) > 3 else 3

    if mode == "list":
        entries = walk(target, max_depth=maxd)
        print(f"共 {len(entries)} 项\n")
        for depth, t, name, p, size in entries:
            sz = f"{size/1024:.1f}KB" if size else ""
            print(f"{'  '*depth}[{t}] {name}  {sz}")
        out = STAGE.parent / f"gitee_tree_{which}.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(
            [{"depth": d, "type": t, "name": n, "path": p, "size": s}
             for d, t, n, p, s in entries], ensure_ascii=False, indent=2),
            encoding="utf-8")
        print(f"\n清单已写入 {out}")

    elif mode == "download":
        entries = walk(target, max_depth=maxd)
        files = [e for e in entries if e[1] == "file"
                 and not any(s in e[2] for s in SKIP_PATTERNS)]
        skipped = [e for e in entries if e[1] == "file"
                   and any(s in e[2] for s in SKIP_PATTERNS)]
        print(f"待下载 {len(files)} 个文件；跳过 {len(skipped)} 个（第三方学术论文）\n")
        for e in skipped:
            print(f"  [跳过] {e[2]}")
        print()
        ok = 0
        for i, (_, _, name, p, size) in enumerate(files, 1):
            if download(p):
                ok += 1
                print(f"  [{i}/{len(files)}] OK  {name}", flush=True)
        print(f"\n完成：{ok}/{len(files)}")
