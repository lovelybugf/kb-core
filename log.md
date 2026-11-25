# Nhật ký kb-core

> Chỉ ghi thêm. Mỗi dòng: `YYYY-MM-DD | ingest|update|lint | mô tả`.

2026-11-23 | update | khởi tạo kho: standards (5 trang), operations (3 trang), templates (6 khuôn), tools kb_lint/kb_index/new_page
2026-11-23 | lint | kb_index.py + kb_lint.py kb-* --strict: 0 lỗi, 0 cảnh báo (5 kho, 27 trang)
2026-11-23 | update | link sang kho khác đổi sang URL GitHub (4 link + template kb-CLAUDE.md); kb_lint kiểm tra URL GitHub với bản clone, báo lỗi link tương đối ra ngoài kho; cập nhật page-structure, review-and-lint, claude-usage
2026-11-25 | update | skill kb-capture + tools/kb_session_hook.py (hook SessionEnd/SessionStart, hàng đợi phiên, digest, scan blocklist); trang operations/session-capture.md
