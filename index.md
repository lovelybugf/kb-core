# kb-core

> Chuẩn chung và công cụ vận hành cho hệ thống kho tri thức Markdown kb-*: khuôn trang, frontmatter, đặt tên, tag, nguồn; quy trình ingest và lint; template; script Python.

Mọi kho khác tham chiếu chuẩn ở đây bằng URL GitHub `https://github.com/lovelybugf/kb-core/blob/main/...` (quy tắc link giữa các kho: `standards/page-structure.md`). Đọc `_index.md` của nhóm cần trước khi mở trang.

## Chuẩn

- [Chuẩn — mục lục](standards/_index.md) — khuôn trang, frontmatter, đặt tên, danh mục tag, nguồn và độ tin cậy.

## Vận hành

- [Vận hành — mục lục](operations/_index.md) — quy trình ingest, rà soát và lint định kỳ, dùng kho với Claude.

## Template

- [Template — mục lục](templates/_index.md) — khuôn trang, runbook, troubleshooting, decision record, CLAUDE.md và index.md cho kho mới.

## Công cụ

- [kb_lint.py](tools/kb_lint.py) — kiểm tra frontmatter, TL;DR, tag, link, mục lục, độ dài, độ cũ, bí mật; thoát mã 1 nếu có lỗi.
- [kb_index.py](tools/kb_index.py) — sinh khối AUTO-INDEX trong `_index.md` từ title + TL;DR, giữ phần viết tay.
- [new_page.py](tools/new_page.py) — tạo trang mới từ template, cập nhật `_index.md` và `log.md`.
- [kb_common.py](tools/kb_common.py) — hàm dùng chung: đọc frontmatter, tìm link, danh mục tag.
- [kb_session_hook.py](tools/kb_session_hook.py) — hàng đợi phiên Claude Code cho hook SessionEnd/SessionStart; lệnh list, digest, done, skip, scan.
- [Skill kb-capture](tools/claude/skills/kb-capture/SKILL.md) — quy trình ghi phiên vào kho; cài và dùng: `operations/session-capture.md`.

## Optional

- [README.md](README.md) — hướng dẫn nhanh cho người.
- [log.md](log.md) — nhật ký thay đổi (chỉ ghi thêm).
