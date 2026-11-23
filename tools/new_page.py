#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tạo trang mới từ template trong kb-core/templates.

Chạy ở thư mục chứa các kho:
    python kb-core/tools/new_page.py <kho>/<thu-muc>/<ten-file> "Tiêu đề"
    python kb-core/tools/new_page.py kb-redhat/satellite/capsule-sync "Đồng bộ Capsule" --tags howto,satellite,capsule
    python kb-core/tools/new_page.py kb-base-devops/linux/disk-full "Đầy ổ đĩa" -t troubleshooting --tags linux,storage

Việc script làm: kiểm tra tên kebab-case và tag hợp lệ → điền title, tags, updated, owner
(mặc định lấy `git config user.name`) → ghi file → cập nhật _index.md của thư mục
→ ghi 1 dòng vào log.md. Các placeholder còn lại ({{tldr}}, {{source}}, ...) phải điền tay;
kb_lint.py sẽ báo lỗi nếu còn sót.
"""

import argparse
import datetime as dt
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kb_common as kc  # noqa: E402

TEMPLATES = {
    "page": "page.md",
    "runbook": "runbook.md",
    "troubleshooting": "troubleshooting.md",
    "decision-record": "decision-record.md",
}
TYPE_TAG = {"runbook": "runbook", "troubleshooting": "troubleshooting", "decision-record": "decision"}


def yaml_str(value):
    """Đặt giá trị trong nháy kép khi YAML có thể hiểu sai."""
    if ": " in value or value.endswith(":") or value[:1] in "[]{}'\"-*&!|>%@`#,?":
        return '"%s"' % value.replace('"', "'")
    return value


def git_user(cwd):
    try:
        out = subprocess.run(["git", "config", "user.name"], cwd=str(cwd),
                             stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                             universal_newlines=True, timeout=5)
        return out.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return ""


def fail(msg):
    print("LỖI: %s" % msg, file=sys.stderr)
    return 2


def linked_from(index_file, target, kb):
    if not index_file.is_file():
        return False
    for link, _line in kc.find_links(kc.read_text(index_file)):
        if kc.resolve_link(index_file, link, kb) == target:
            return True
    return False


def main(argv=None):
    kc.setup_stdout()
    ap = argparse.ArgumentParser(description="Tạo trang mới từ template kb-core/templates")
    ap.add_argument("path", help="<kho>/<thu-muc>/<ten-file> (đuôi .md tự thêm)")
    ap.add_argument("title", help="tiêu đề trang")
    ap.add_argument("-t", "--template", choices=sorted(TEMPLATES), default="page")
    ap.add_argument("--tags", default="", help="tag cách nhau bởi dấu phẩy (phải có trong standards/tags.md)")
    ap.add_argument("--product", default="", help="sản phẩm + phiên bản, vd. 'Red Hat Satellite 6.16'")
    ap.add_argument("--source", default="", help="URL hoặc tài liệu gốc")
    ap.add_argument("--owner", default="", help="người phụ trách (mặc định git user.name)")
    ap.add_argument("--no-index", action="store_true", help="không cập nhật _index.md")
    ap.add_argument("--no-log", action="store_true", help="không ghi log.md")
    args = ap.parse_args(argv)

    target = Path(args.path)
    if target.suffix.lower() != ".md":
        target = target.with_name(target.name + ".md")
    target = target.resolve()
    if not kc.KEBAB_MD_RE.match(target.name):
        return fail("tên file phải là kebab-case, không dấu: %s" % target.name)
    kb = kc.find_kb_root(target.parent)
    if kb is None:
        return fail("không tìm thấy gốc kho (thư mục có index.md và CLAUDE.md) chứa %s" % target.parent)
    rel_parts = target.relative_to(kb).parts
    if len(rel_parts) < 2:
        return fail("đặt trang trong một thư mục chủ đề, không đặt ở gốc kho")
    if rel_parts[0] in kc.RESERVED_TOP_DIRS:
        return fail("thư mục '%s/' dành riêng, không chứa trang nội dung" % rel_parts[0])
    bad = [p for p in rel_parts[:-1] if not kc.KEBAB_DIR_RE.match(p)]
    if bad:
        return fail("tên thư mục phải là kebab-case, không dấu: %s" % ", ".join(bad))
    if target.exists():
        return fail("file đã tồn tại: %s" % target)

    vocab = kc.load_tags()
    tags = [t.strip() for t in args.tags.split(",") if t.strip()]
    type_tag = TYPE_TAG.get(args.template)
    if type_tag and type_tag not in tags:
        tags.insert(0, type_tag)
    unknown = [t for t in tags if t not in vocab]
    if unknown:
        return fail("tag không có trong kb-core/standards/tags.md: %s" % ", ".join(unknown))

    owner = (args.owner or git_user(kb) or os.environ.get("USERNAME")
             or os.environ.get("USER") or "{{owner}}")
    today = dt.date.today()
    text = kc.read_text(kc.TEMPLATES_DIR / TEMPLATES[args.template])
    values = {"title": yaml_str(args.title), "tags": ", ".join(tags),
              "date": today.isoformat(), "owner": owner}
    if args.source:
        values["source"] = yaml_str(args.source)
    if args.product:
        values["product"] = yaml_str(args.product)
    else:
        text = text.replace("product: {{product}}", "product:")
    for key, value in values.items():
        text = text.replace("{{%s}}" % key, value)

    target.parent.mkdir(parents=True, exist_ok=True)
    kc.write_text(target, text)
    rel = target.relative_to(kb.parent).as_posix()
    print("Đã tạo  %s (template: %s)" % (rel, args.template))

    if not args.no_index:
        import kb_index
        folder = target.parent
        while folder != kb:  # cập nhật cả _index.md của các thư mục cha
            status = kb_index.update_dir(folder, kb)
            print("%s/_index.md: %s" % (folder.relative_to(kb).as_posix(), status))
            folder = folder.parent
        topic = kb / rel_parts[0]
        if not linked_from(kb / "index.md", topic / "_index.md", kb):
            print("LƯU Ý: thư mục '%s/' chưa có trong %s/index.md — thêm dòng:" % (rel_parts[0], kb.name))
            print("  - [%s](%s/_index.md) — <tóm tắt 1 câu>" % (kb_index.dir_title(topic), rel_parts[0]))
    if not args.no_log:
        kc.append_log(kb, "update", "tạo trang %s" % target.relative_to(kb).as_posix(), today)
        print("log.md: đã ghi 1 dòng")
    print("Tiếp theo: điền TL;DR, source, nội dung → chạy kb_lint.py %s" % kb.name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
