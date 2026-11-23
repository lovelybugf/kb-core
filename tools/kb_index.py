#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sinh/cập nhật khối AUTO-INDEX trong _index.md của từng thư mục chủ đề.

Chạy ở thư mục chứa các kho:
    python kb-core/tools/kb_index.py kb-*            # ghi file
    python kb-core/tools/kb_index.py kb-* --check    # chỉ kiểm tra, thoát mã 1 nếu cần cập nhật

Mỗi trang thành 1 dòng: "- [title](file.md) — câu đầu tiên của TL;DR".
Thư mục con có _index.md thành 1 dòng trỏ tới _index.md của nó (tóm tắt = blockquote đầu tiên).
Phần viết tay nằm ngoài khối <!-- AUTO-INDEX START --> ... <!-- AUTO-INDEX END --> được giữ nguyên.
Thư mục chưa có _index.md mà có trang → tạo _index.md với khung tối thiểu.
Không đụng tới index.md ở gốc kho (viết tay) và các thư mục raw/, templates/, tools/, data/.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_common as kc  # noqa: E402

EMPTY_LINE = "_(chưa có trang)_"


def dir_title(folder):
    return folder.name.replace("-", " ").capitalize()


def md_escape(text):
    return str(text).replace("[", "\\[").replace("]", "\\]")


def index_heading(idx_path):
    """(tiêu đề H1, câu tóm tắt trong blockquote đầu tiên) của một _index.md."""
    title, summary = None, ""
    for line in kc.read_text(idx_path).splitlines():
        s = line.strip()
        if title is None and s.startswith("# "):
            title = s[2:].strip()
        elif not summary and s.startswith(">"):
            summary = s.lstrip(">").strip()
        if title and summary:
            break
    return title or dir_title(idx_path.parent), summary


def build_entries(folder, kb):
    entries = []
    pages = sorted((p for p in folder.iterdir()
                    if p.is_file() and kc.is_content_page(p, kb)), key=lambda p: p.name)
    for page in pages:
        data, _errors, body, _offset = kc.parse_frontmatter(kc.read_text(page))
        title = (data or {}).get("title") or page.stem
        if isinstance(title, list):
            title = ", ".join(title)
        tldr, _ = kc.find_tldr(body)
        summary = kc.first_sentence(tldr) if tldr else "(chưa có TL;DR)"
        entries.append("- [%s](%s) — %s" % (md_escape(title), page.name, summary))
    subs = sorted((s for s in folder.iterdir()
                   if s.is_dir() and not s.name.startswith(".") and (s / "_index.md").is_file()),
                  key=lambda s: s.name)
    for sub in subs:
        title, summary = index_heading(sub / "_index.md")
        entries.append("- [%s](%s/_index.md) — %s" % (md_escape(title), sub.name, summary or "thư mục con"))
    return entries


def render_block(entries):
    body = "\n".join(entries) if entries else EMPTY_LINE
    return "%s\n%s\n%s" % (kc.AUTO_START, body, kc.AUTO_END)


def update_dir(folder, kb, write=True):
    """Trả về 'created' | 'updated' | 'unchanged' | None (thư mục không cần _index.md)."""
    folder, kb = Path(folder), Path(kb)
    idx = folder / "_index.md"
    entries = build_entries(folder, kb)
    block = render_block(entries)
    if idx.is_file():
        old = kc.read_text(idx)
        start, end = old.find(kc.AUTO_START), old.find(kc.AUTO_END)
        if start != -1 and end > start:
            new = old[:start] + block + old[end + len(kc.AUTO_END):]
        else:
            new = old.rstrip("\n") + "\n\n## Trang\n\n" + block + "\n"
    else:
        if not entries:
            return None
        old = None
        new = ("# %s\n\n> TODO: mô tả phạm vi thư mục `%s/` trong 1 câu.\n\n## Trang\n\n%s\n"
               % (dir_title(folder), folder.name, block))
    if new == old:
        return "unchanged"
    if write:
        kc.write_text(idx, new)
    return "created" if old is None else "updated"


def main(argv=None):
    kc.setup_stdout()
    ap = argparse.ArgumentParser(description="Sinh khối AUTO-INDEX trong _index.md")
    ap.add_argument("kbs", nargs="+", help="thư mục kho, hỗ trợ glob (vd. kb-*)")
    ap.add_argument("--check", action="store_true", help="không ghi file; thoát mã 1 nếu cần cập nhật")
    args = ap.parse_args(argv)

    roots = kc.expand_args(args.kbs)
    if not roots:
        print("Không tìm thấy thư mục kho nào khớp: %s" % " ".join(args.kbs), file=sys.stderr)
        return 2
    workspace = roots[0].parent
    changed = total = 0
    for kb in roots:
        if not kc.is_kb_root(kb):
            print("BỎ QUA  %s: không phải kho (thiếu index.md/CLAUDE.md)" % kb.name)
            continue
        for folder in kc.content_dirs(kb):
            status = update_dir(folder, kb, write=not args.check)
            if status is None:
                continue
            total += 1
            if status != "unchanged":
                changed += 1
                try:
                    rel = (folder / "_index.md").relative_to(workspace).as_posix()
                except ValueError:
                    rel = str(folder / "_index.md")
                label = "CẦN CẬP NHẬT" if args.check else status.upper()
                print("%-12s %s" % (label, rel))
    verb = "cần cập nhật" if args.check else "đã ghi"
    print("Tổng: %d _index.md, %s %d" % (total, verb, changed))
    return 1 if args.check and changed else 0


if __name__ == "__main__":
    sys.exit(main())
