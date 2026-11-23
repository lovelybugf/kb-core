# Template

> Khuôn có sẵn để tạo trang và kho mới; dùng qua `tools/new_page.py` hoặc sao chép tay.

Placeholder dạng `{{...}}`. `new_page.py` tự điền `title`, `tags`, `updated`, `owner` (và `product`, `source` nếu truyền tham số); phần còn lại điền tay — `kb_lint.py` báo lỗi nếu còn sót. Thư mục này không phải trang nội dung nên không bị lint frontmatter/link.

## Trang nội dung

- [page.md](page.md) — khuôn trang chung: bối cảnh, nội dung chính, lưu ý, liên quan, nguồn (`-t page`).
- [runbook.md](runbook.md) — quy trình vận hành: điều kiện, kiểm tra trước, các bước có kiểm tra, rollback (`-t runbook`).
- [troubleshooting.md](troubleshooting.md) — triệu chứng → chẩn đoán → nguyên nhân → xử lý → phòng ngừa (`-t troubleshooting`).
- [decision-record.md](decision-record.md) — ghi nhận quyết định: bối cảnh, phương án, quyết định, hệ quả (`-t decision-record`).

## Kho mới

- [kb-CLAUDE.md](kb-CLAUDE.md) — khuôn `CLAUDE.md` (≤ 40 dòng) cho gốc kho mới.
- [kb-index.md](kb-index.md) — khuôn `index.md` (≤ 200 dòng) theo định dạng llms.txt.

Tạo kho mới: tạo thư mục `kb-<lĩnh-vực>`, chép hai file trên thành `CLAUDE.md`, `index.md`, thêm `README.md`, `log.md`, `.gitignore`, `.gitattributes`, `raw/.gitkeep` (lấy mẫu từ một kho có sẵn), `git init`, rồi thêm kho vào bảng ở `kb-hub/index.md`.
