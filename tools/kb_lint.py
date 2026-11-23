#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kiểm tra một hoặc nhiều kho tri thức kb-* (Python 3.8+, chỉ thư viện chuẩn).

Chạy ở thư mục chứa các kho (glob được tự mở rộng, kể cả trên PowerShell):
    python kb-core/tools/kb_lint.py kb-*
    python kb-core/tools/kb_lint.py kb-redhat --strict
    python kb-core/tools/kb_lint.py kb-* --today 2027-06-01   # mô phỏng ngày để thử kiểm tra độ cũ

LỖI (ERROR): thiếu file gốc bắt buộc, CLAUDE.md > 40 dòng, index.md > 200 dòng,
log.md sai định dạng, thiếu frontmatter/trường bắt buộc, reliability/updated sai,
tag không có trong kb-core/standards/tags.md, thiếu TL;DR, placeholder {{...}} còn sót,
trang > 500 dòng, link tương đối hỏng / sai hoa-thường / trỏ ổ đĩa cục bộ,
trang không có trong _index.md (hoặc index.md với trang ở gốc), _index.md mồ côi.
CẢNH BÁO (WARN): `updated` quá 180 ngày hoặc ở tương lai, tên file/thư mục không
kebab-case, trường frontmatter lạ, > 6 tag, nghi chứa bí mật (mật khẩu, khóa, IP nội bộ),
link sang kho chưa có trên máy.

Mã thoát: 0 = không lỗi; 1 = có lỗi (với --strict: có lỗi hoặc cảnh báo); 2 = sai tham số.
"""

import argparse
import datetime as dt
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_common as kc  # noqa: E402

ROOT_FILES = ("CLAUDE.md", "index.md", "log.md", "README.md", ".gitignore")
ROOT_LIMITS = {"CLAUDE.md": 40, "index.md": 200}
MAX_TAGS = 6
SECRET_PATTERNS = (
    (re.compile(r"(?i)\b(password|passwd|secret|token|api[_-]?key)\b\s*[:=]\s*['\"]?(?![<{$])[^\s'\"<>]{4,}"),
     "nghi chứa mật khẩu/khóa — thay bằng placeholder <...>"),
    (re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"), "chứa private key"),
    (re.compile(r"\bAKIA[0-9A-Z]{16}\b"), "nghi chứa AWS access key"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{30,}\b"), "nghi chứa GitHub token"),
    (re.compile(r"\bsk-ant-[A-Za-z0-9_-]{10,}"), "nghi chứa Anthropic API key"),
    (re.compile(r"(?<![\d.])(10\.\d{1,3}\.\d{1,3}\.\d{1,3}|192\.168\.\d{1,3}\.\d{1,3}"
                r"|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})(?![\d.])"),
     "nghi chứa IP nội bộ — thay bằng placeholder"),
)


class Linter(object):
    def __init__(self, workspace, tags, today, stale_days, max_lines):
        self.workspace = workspace
        self.tags = tags
        self.today = today
        self.stale_days = stale_days
        self.max_lines = max_lines
        self.issues = []
        self._dir_cache = {}

    # ------------------------------------------------------------------ tiện ích
    def add(self, level, path, line, msg):
        self.issues.append((level, Path(path), line, msg))

    def rel(self, path):
        try:
            return Path(path).relative_to(self.workspace).as_posix()
        except ValueError:
            return str(path)

    def _listdir(self, folder):
        key = str(folder)
        if key not in self._dir_cache:
            try:
                self._dir_cache[key] = set(os.listdir(key))
            except OSError:
                self._dir_cache[key] = None
        return self._dir_cache[key]

    def exact_case(self, dest):
        """Windows không phân biệt hoa/thường, GitHub/Linux có: kiểm tra từng phần đường dẫn."""
        try:
            parts = dest.relative_to(self.workspace).parts
        except ValueError:
            return True
        cur = self.workspace
        for part in parts:
            names = self._listdir(cur)
            if names is None:
                return True
            if part not in names:
                return False
            cur = cur / part
        return True

    def sibling_root(self, dest):
        try:
            first = dest.relative_to(self.workspace).parts[0]
        except (ValueError, IndexError):
            return None
        return self.workspace / first

    # --------------------------------------------------------------- từng kho
    def lint_kb(self, kb):
        if not kc.is_kb_root(kb):
            self.add("ERROR", kb, 0, "không phải kho tri thức (thiếu index.md hoặc CLAUDE.md)")
            return 0
        self.check_root(kb)
        pages, link_map = [], {}
        for path in kc.iter_md_files(kb):
            text = kc.read_text(path)
            if kc.is_content_page(path, kb):
                pages.append(path)
                self.check_page(path, text)
            if not kc.is_template_file(path, kb):
                link_map[path] = self.check_links(path, text, kb)
            self.check_secrets(path, text)
        for d in kc.content_dirs(kb):
            if not kc.KEBAB_DIR_RE.match(d.name):
                self.add("WARN", d, 0, "tên thư mục nên là kebab-case không dấu")
        self.check_coverage(kb, pages, link_map)
        return len(pages)

    def check_root(self, kb):
        for name in ROOT_FILES:
            if not (kb / name).is_file():
                self.add("ERROR", kb / name, 0, "thiếu file bắt buộc ở gốc kho")
        if not (kb / "raw").is_dir():
            self.add("ERROR", kb / "raw", 0, "thiếu thư mục raw/ (kèm .gitkeep)")
        for name, limit in ROOT_LIMITS.items():
            p = kb / name
            if p.is_file():
                n = len(kc.read_text(p).splitlines())
                if n > limit:
                    self.add("ERROR", p, 0, "%d dòng, vượt giới hạn %d dòng" % (n, limit))
        idx = kb / "index.md"
        if idx.is_file():
            lines = kc.read_text(idx).splitlines()
            first = next((l for l in lines if l.strip()), "")
            if not first.startswith("# "):
                self.add("WARN", idx, 1, "dòng đầu nên là tiêu đề H1 (định dạng llms.txt)")
            if not any(l.startswith(">") for l in lines):
                self.add("WARN", idx, 0, "thiếu blockquote tóm tắt kho (định dạng llms.txt)")
        log = kb / "log.md"
        if log.is_file():
            for n, line in enumerate(kc.read_text(log).splitlines(), 1):
                s = line.strip()
                if not s or s.startswith(("#", ">", "<!--")):
                    continue
                m = kc.LOG_RE.match(s)
                if not m:
                    self.add("ERROR", log, n, "sai định dạng 'YYYY-MM-DD | ingest|update|lint | mô tả'")
                elif kc.parse_date(m.group(1)) is None:
                    self.add("ERROR", log, n, "ngày không hợp lệ: %s" % m.group(1))

    def check_page(self, path, text):
        lines = text.splitlines()
        if len(lines) > self.max_lines:
            self.add("ERROR", path, 0, "%d dòng (> %d) — tách thành nhiều trang" % (len(lines), self.max_lines))
        if not kc.KEBAB_MD_RE.match(path.name):
            self.add("WARN", path, 0, "tên file nên là kebab-case không dấu")

        data, errors, body, offset = kc.parse_frontmatter(text)
        for e in errors:
            self.add("ERROR", path, 1, e)
        if data is None:
            return
        for field in kc.REQUIRED_FIELDS:
            value = data.get(field)
            if value is None:
                self.add("ERROR", path, 1, "frontmatter thiếu trường '%s'" % field)
            elif value in ("", []):
                self.add("ERROR", path, 1, "trường '%s' đang rỗng" % field)
        for field in data:
            if field not in kc.KNOWN_FIELDS:
                self.add("WARN", path, 1, "trường frontmatter lạ '%s'" % field)

        tags = data.get("tags")
        if isinstance(tags, str) and tags:
            self.add("ERROR", path, 1, "tags phải là danh sách dạng [a, b]")
            tags = [tags]
        if isinstance(tags, list):
            if len(tags) > MAX_TAGS:
                self.add("WARN", path, 1, "%d tag (> %d)" % (len(tags), MAX_TAGS))
            if len(set(tags)) != len(tags):
                self.add("WARN", path, 1, "tag bị lặp")
            for tag in tags:
                if tag not in self.tags:
                    self.add("ERROR", path, 1, "tag '%s' không có trong kb-core/standards/tags.md" % tag)

        reliability = data.get("reliability")
        if reliability and reliability not in kc.RELIABILITY:
            self.add("ERROR", path, 1, "reliability '%s' không hợp lệ (%s)" % (reliability, " | ".join(kc.RELIABILITY)))

        updated = data.get("updated")
        if updated:
            day = kc.parse_date(updated)
            if day is None:
                self.add("ERROR", path, 1, "updated '%s' không đúng dạng YYYY-MM-DD" % updated)
            else:
                age = (self.today - day).days
                if age < 0:
                    self.add("WARN", path, 1, "updated %s ở tương lai" % updated)
                elif age > self.stale_days:
                    self.add("WARN", path, 1, "quá cũ: updated %s (%d ngày > %d) — rà soát lại" % (updated, age, self.stale_days))

        tldr, idx = kc.find_tldr(body)
        line_no = offset + max(idx, 0) + 1
        if tldr is None:
            self.add("ERROR", path, line_no, "thiếu dòng '%s ...' ngay sau frontmatter" % kc.TLDR_PREFIX)
        elif not tldr:
            self.add("ERROR", path, line_no, "TL;DR rỗng")

        for n, line in enumerate(kc.strip_code(text).splitlines(), 1):
            if re.search(r"\{\{[^}]*\}\}", line):
                self.add("ERROR", path, n, "còn placeholder template {{...}} chưa điền")
                break

    def check_links(self, path, text, kb):
        targets = set()
        for target, line in kc.find_links(text):
            if kc.DRIVE_RE.match(target) or target.lower().startswith("file:"):
                self.add("ERROR", path, line, "link tuyệt đối tới máy cục bộ: %s" % target)
                continue
            dest = kc.resolve_link(path, target, kb)
            if dest is None:
                continue
            targets.add(dest)
            if dest.exists():
                if not self.exact_case(dest):
                    self.add("ERROR", path, line, "link sai chữ hoa/thường (hỏng trên Linux/GitHub): %s" % target)
                continue
            try:
                dest.relative_to(kb)
                inside = True
            except ValueError:
                inside = False
            if not inside:
                sibling = self.sibling_root(dest)
                if sibling is not None and not sibling.exists():
                    self.add("WARN", path, line, "link sang kho chưa có trên máy: %s" % target)
                    continue
            self.add("ERROR", path, line, "link hỏng: %s" % target)
        return targets

    def check_secrets(self, path, text):
        for n, line in enumerate(text.splitlines(), 1):
            for regex, msg in SECRET_PATTERNS:
                if regex.search(line):
                    self.add("WARN", path, n, msg)
                    break

    def check_coverage(self, kb, pages, link_map):
        index_md = kb / "index.md"
        root_links = link_map.get(index_md, set())
        reported = set()
        for page in pages:
            folder = page.parent
            if folder == kb:
                if page not in root_links:
                    self.add("ERROR", page, 0, "trang ở gốc kho chưa có trong index.md")
                continue
            idx = folder / "_index.md"
            if not idx.is_file():
                if folder not in reported:
                    self.add("ERROR", idx, 0, "thư mục chủ đề thiếu _index.md (chạy kb_index.py)")
                    reported.add(folder)
                continue
            if page not in link_map.get(idx, set()):
                self.add("ERROR", page, 0, "trang mồ côi: chưa có trong %s (chạy kb_index.py)" % self.rel(idx))
        for f in link_map:
            if f.name != "_index.md":
                continue
            parents = [index_md]
            if f.parent.parent != kb:
                parents.append(f.parent.parent / "_index.md")
            if not any(f in link_map.get(p, set()) for p in parents):
                self.add("ERROR", f, 0, "_index.md mồ côi: chưa được trỏ tới từ index.md hoặc _index.md cấp trên")


def main(argv=None):
    kc.setup_stdout()
    ap = argparse.ArgumentParser(description="Kiểm tra kho tri thức kb-*")
    ap.add_argument("kbs", nargs="+", help="thư mục kho, hỗ trợ glob (vd. kb-*)")
    ap.add_argument("--tags", help="đường dẫn tags.md (mặc định kb-core/standards/tags.md)")
    ap.add_argument("--max-lines", type=int, default=500, help="số dòng tối đa của 1 trang (mặc định 500)")
    ap.add_argument("--stale-days", type=int, default=180, help="số ngày coi là quá cũ (mặc định 180)")
    ap.add_argument("--today", help="ngày tham chiếu YYYY-MM-DD (mặc định hôm nay)")
    ap.add_argument("--strict", action="store_true", help="coi cảnh báo là lỗi")
    ap.add_argument("-q", "--quiet", action="store_true", help="không in cảnh báo")
    args = ap.parse_args(argv)

    roots = kc.expand_args(args.kbs)
    if not roots:
        print("Không tìm thấy thư mục kho nào khớp: %s" % " ".join(args.kbs), file=sys.stderr)
        return 2
    tags_file = Path(args.tags) if args.tags else kc.TAGS_FILE
    if not tags_file.is_file():
        print("Không thấy danh mục tag: %s" % tags_file, file=sys.stderr)
        return 2
    today = kc.parse_date(args.today) if args.today else dt.date.today()
    if today is None:
        print("--today phải có dạng YYYY-MM-DD", file=sys.stderr)
        return 2

    workspace = Path(os.path.commonpath([str(r.parent) for r in roots]))
    linter = Linter(workspace, kc.load_tags(tags_file), today, args.stale_days, args.max_lines)
    counts = []
    for kb in roots:
        counts.append((kb.name, linter.lint_kb(kb)))

    order = {"ERROR": 0, "WARN": 1}
    issues = sorted(linter.issues, key=lambda i: (order[i[0]], linter.rel(i[1]), i[2]))
    for level, path, line, msg in issues:
        if args.quiet and level == "WARN":
            continue
        loc = linter.rel(path) + (":%d" % line if line else "")
        print("%-5s %s: %s" % (level, loc, msg))

    n_err = sum(1 for i in issues if i[0] == "ERROR")
    n_warn = len(issues) - n_err
    print("")
    for name, n in counts:
        print("  %-18s %4d trang" % (name, n))
    print("Tổng: %d kho, %d trang, %d lỗi, %d cảnh báo" % (len(counts), sum(n for _, n in counts), n_err, n_warn))
    return 1 if n_err or (args.strict and n_warn) else 0


if __name__ == "__main__":
    sys.exit(main())
