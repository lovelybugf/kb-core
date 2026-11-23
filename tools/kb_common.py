# -*- coding: utf-8 -*-
"""Hàm dùng chung cho các công cụ kho tri thức kb-* (Python 3.8+, chỉ thư viện chuẩn).

Được import bởi kb_lint.py, kb_index.py, new_page.py (cùng thư mục).
"""

import datetime as dt
import glob
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote

CORE_DIR = Path(__file__).resolve().parent.parent  # .../kb-core
TAGS_FILE = CORE_DIR / "standards" / "tags.md"
TEMPLATES_DIR = CORE_DIR / "templates"

# File đặc biệt: không phải trang nội dung, không cần frontmatter.
SPECIAL_FILES = {"CLAUDE.md", "README.md", "index.md", "_index.md", "log.md"}
# Thư mục cấp 1 dành riêng: không chứa trang nội dung.
RESERVED_TOP_DIRS = {"raw", "templates", "tools", "data"}
# Thư mục luôn bỏ qua ở mọi cấp (cùng với mọi thư mục bắt đầu bằng ".").
SKIP_DIRS = {"__pycache__", "node_modules", "venv"}

REQUIRED_FIELDS = ("title", "tags", "source", "reliability", "updated", "owner")
KNOWN_FIELDS = REQUIRED_FIELDS + ("product",)
RELIABILITY = ("official", "community", "internal-tested", "unverified")
TLDR_PREFIX = "**TL;DR:**"
AUTO_START = "<!-- AUTO-INDEX START -->"
AUTO_END = "<!-- AUTO-INDEX END -->"

KEBAB_MD_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
KEBAB_DIR_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LOG_RE = re.compile(r"^(\d{4}-\d{2}-\d{2}) \| (ingest|update|lint) \| \S.*$")

FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE_RE = re.compile(r"(`+)(.+?)\1")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
LINK_RE = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*(<[^>]+>|[^)\s]+)(?:\s+[\"'(][^)]*)?\)")
REF_DEF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", re.M)
SCHEME_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9+.-]*:")
DRIVE_RE = re.compile(r"^[A-Za-z]:[\\/]")
TAG_DEF_RE = re.compile(r"^\s*[-*]\s+`([^`]+)`")
KEY_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_-]*):(?:\s+(.*))?$")
ITEM_RE = re.compile(r"^\s*-\s+(.*)$")
SENTENCE_END_RE = re.compile(r"(?<=[.!?…])\s+")


# --------------------------------------------------------------------------- I/O
def setup_stdout():
    """In tiếng Việt an toàn trên console Windows (kể cả khi chuyển hướng ra file)."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def read_text(path):
    with open(str(path), "r", encoding="utf-8-sig") as f:
        return f.read()


def write_text(path, text):
    """Ghi UTF-8 không BOM, xuống dòng LF."""
    with open(str(path), "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def parse_date(value):
    try:
        return dt.datetime.strptime(str(value).strip(), "%Y-%m-%d").date()
    except ValueError:
        return None


def append_log(kb_root, kind, message, today=None):
    """Ghi thêm 1 dòng 'YYYY-MM-DD | kind | message' vào log.md của kho."""
    log = Path(kb_root) / "log.md"
    day = (today or dt.date.today()).isoformat()
    text = read_text(log) if log.is_file() else "# Nhật ký\n\n"
    if text and not text.endswith("\n"):
        text += "\n"
    write_text(log, text + "%s | %s | %s\n" % (day, kind, message))


# ---------------------------------------------------------------------- kho, file
def expand_args(args):
    """Mở rộng glob (PowerShell không tự mở rộng `kb-*`), chỉ giữ thư mục."""
    roots = []
    for arg in args:
        matches = glob.glob(arg) if any(c in arg for c in "*?[") else [arg]
        for m in sorted(matches):
            p = Path(m).resolve()
            if p.is_dir() and p not in roots:
                roots.append(p)
    return roots


def is_kb_root(path):
    path = Path(path)
    return (path / "index.md").is_file() and (path / "CLAUDE.md").is_file()


def find_kb_root(start):
    """Đi ngược lên từ `start` tới thư mục gốc kho (có index.md + CLAUDE.md)."""
    cur = Path(start).resolve()
    for candidate in [cur] + list(cur.parents):
        if is_kb_root(candidate):
            return candidate
    return None


def _keep_dir(name):
    return not name.startswith(".") and name not in SKIP_DIRS


def iter_md_files(kb_root):
    """Mọi file .md trong kho, trừ thư mục ẩn (.git, ...) và raw/."""
    kb_root = Path(kb_root)
    for dirpath, dirnames, filenames in os.walk(str(kb_root)):
        current = Path(dirpath)
        dirnames[:] = sorted(
            d for d in dirnames
            if _keep_dir(d) and not (current == kb_root and d == "raw")
        )
        for name in sorted(filenames):
            if name.lower().endswith(".md"):
                yield current / name


def content_dirs(kb_root):
    """Thư mục chủ đề: mọi thư mục con, trừ thư mục dành riêng cấp 1 và thư mục ẩn."""
    kb_root = Path(kb_root)
    result = []
    for dirpath, dirnames, _filenames in os.walk(str(kb_root)):
        current = Path(dirpath)
        if current == kb_root:
            dirnames[:] = sorted(d for d in dirnames if _keep_dir(d) and d not in RESERVED_TOP_DIRS)
            continue
        dirnames[:] = sorted(d for d in dirnames if _keep_dir(d))
        result.append(current)
    return result


def top_dir(path, kb_root):
    parts = Path(path).relative_to(kb_root).parts
    return parts[0] if len(parts) > 1 else ""


def is_content_page(path, kb_root):
    path = Path(path)
    return (path.suffix.lower() == ".md"
            and path.name not in SPECIAL_FILES
            and top_dir(path, kb_root) not in RESERVED_TOP_DIRS)


def is_template_file(path, kb_root):
    path = Path(path)
    return top_dir(path, kb_root) == "templates" and path.name not in SPECIAL_FILES


# ------------------------------------------------------------------- frontmatter
def _scalar(raw):
    raw = raw.strip()
    if len(raw) >= 2 and raw[0] == raw[-1] and raw[0] in "\"'":
        return raw[1:-1]
    return raw


def _flow_list(inner):
    items, buf, quote = [], "", None
    for ch in inner:
        if quote:
            if ch == quote:
                quote = None
            buf += ch
        elif ch in "\"'":
            quote = ch
            buf += ch
        elif ch == ",":
            items.append(buf)
            buf = ""
        else:
            buf += ch
    items.append(buf)
    return [_scalar(x) for x in items if x.strip()]


def parse_frontmatter(text):
    """Đọc frontmatter YAML tối giản: `key: value`, danh sách `[a, b]` hoặc `- item`.

    Trả về (data | None, errors, body_lines, body_offset). body_offset = số dòng
    đứng trước thân trang (dùng để tính số dòng khi báo lỗi).
    """
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, ["thiếu frontmatter (dòng 1 phải là ---)"], lines, 0
    end = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end = i
            break
    if end is None:
        return None, ["frontmatter thiếu dòng đóng ---"], lines, 0

    data, errors, current = {}, [], None
    for n, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        item = ITEM_RE.match(line)
        if item and current is not None and (
                data.get(current) == "" or isinstance(data.get(current), list)):
            if not isinstance(data[current], list):
                data[current] = []
            data[current].append(_scalar(item.group(1)))
            continue
        m = KEY_RE.match(line)
        if not m:
            errors.append("frontmatter dòng %d không đúng dạng 'key: value'" % n)
            continue
        key, raw = m.group(1), (m.group(2) or "").strip()
        if key in data:
            errors.append("frontmatter trùng trường '%s'" % key)
        current = key
        if raw.startswith("["):
            if raw.endswith("]"):
                data[key] = _flow_list(raw[1:-1])
            else:
                errors.append("trường '%s': danh sách phải nằm trên 1 dòng dạng [a, b]" % key)
                data[key] = []
        elif raw == "":
            data[key] = ""
        else:
            if raw[0] not in "\"'" and (": " in raw or raw.endswith(":")):
                errors.append("trường '%s': giá trị chứa ': ' phải đặt trong nháy kép" % key)
            data[key] = _scalar(raw)
    return data, errors, lines[end + 1:], end + 1


def find_tldr(body_lines):
    """Trả về (nội dung TL;DR | None, chỉ số dòng không rỗng đầu tiên của thân trang)."""
    for i, line in enumerate(body_lines):
        s = line.strip()
        if not s:
            continue
        if s.startswith(TLDR_PREFIX):
            return s[len(TLDR_PREFIX):].strip(), i
        return None, i
    return None, -1


def first_sentence(text, limit=240):
    """Câu đầu tiên của TL;DR, dùng làm tóm tắt 1 câu trong _index.md."""
    text = " ".join(text.split())
    s = SENTENCE_END_RE.split(text, maxsplit=1)[0]
    if len(s) > limit:
        cut = s[:limit].rsplit(" ", 1)[0]
        if cut.count("`") % 2:
            cut = cut[:cut.rfind("`")].rstrip()
        s = cut + " …"
    return s


# ---------------------------------------------------------------------- tag, link
def load_tags(path=None):
    """Đọc danh mục tag: mỗi dòng dạng "- `tag` — mô tả" trong standards/tags.md."""
    tags, in_fence = set(), False
    for line in read_text(path or TAGS_FILE).splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = TAG_DEF_RE.match(line)
        if m:
            tags.add(m.group(1).strip())
    return tags


def strip_code(text):
    """Xoá code block, inline code, comment HTML (giữ nguyên số dòng)."""
    text = HTML_COMMENT_RE.sub(lambda m: re.sub(r"[^\n]", " ", m.group(0)), text)
    out, fence = [], None
    for line in text.split("\n"):
        m = FENCE_RE.match(line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence):
                fence = None
            out.append("")
            continue
        if m:
            fence = m.group(1)
            out.append("")
            continue
        out.append(INLINE_CODE_RE.sub(lambda mm: " " * len(mm.group(0)), line))
    return "\n".join(out)


def find_links(text):
    """Danh sách (đích link, số dòng) của link Markdown ngoài code block."""
    clean = strip_code(text)
    found = []
    for regex in (LINK_RE, REF_DEF_RE):
        for m in regex.finditer(clean):
            target = m.group(1).strip()
            if target.startswith("<") and target.endswith(">"):
                target = target[1:-1]
            found.append((target, clean.count("\n", 0, m.start()) + 1))
    return found


def resolve_link(src_file, target, kb_root):
    """Đường dẫn tuyệt đối của link nội bộ; None nếu là URL, mailto, neo (#) ..."""
    if not target or target.startswith("#") or target.startswith("//"):
        return None
    if SCHEME_RE.match(target) and not DRIVE_RE.match(target):
        return None
    path = unquote(target.split("#", 1)[0].split("?", 1)[0])
    if not path:
        return None
    if path.startswith("/"):
        base = Path(kb_root) / path.lstrip("/")
    else:
        base = Path(src_file).parent / path
    return Path(os.path.normpath(str(base)))
