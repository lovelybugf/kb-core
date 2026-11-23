# Vận hành

> Quy trình vận hành kho: đưa tài liệu mới vào kho, rà soát và lint định kỳ, dùng kho với Claude.

## Trang

<!-- AUTO-INDEX START -->
- [Dùng kho tri thức với Claude (Projects, Claude Code, API)](claude-usage.md) — Cho Claude đọc theo tầng: `CLAUDE.md` → `index.md` → `_index.md` của chủ đề → 2–3 trang cần thiết, không nạp cả kho.
- [Quy trình đưa tài liệu mới vào kho (ingest)](ingest.md) — Tài liệu mới (docx, pdf, web) đi qua 7 bước: chọn kho, lưu gốc vào `raw/`, trích văn bản, viết trang tóm lược trong thư mục chủ đề, cập nhật `_index.md`/`index.md`, ghi `log.md`, chạy lint rồi commit.
- [Rà soát định kỳ và lint kho tri thức](review-and-lint.md) — Chạy `kb_lint.py` trước mỗi commit (phải 0 lỗi) và rà soát sâu mỗi tháng: trang mồ côi, link hỏng, trang quá cũ (`updated` quá 180 ngày), tag lạ, trang quá dài.
<!-- AUTO-INDEX END -->
