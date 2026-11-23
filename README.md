# kb-core

Chuẩn chung và công cụ cho hệ thống kho tri thức Markdown `kb-*`. Mọi kho khác tuân theo chuẩn ở đây.

## Cấu trúc

| Thư mục | Nội dung |
|---|---|
| `standards/` | Khuôn trang, frontmatter, đặt tên, danh mục tag, nguồn và độ tin cậy |
| `operations/` | Quy trình ingest, rà soát/lint, dùng kho với Claude |
| `templates/` | Khuôn trang, runbook, troubleshooting, decision record, CLAUDE.md/index.md cho kho mới |
| `tools/` | `kb_lint.py`, `kb_index.py`, `new_page.py` (Python 3.8+, chỉ thư viện chuẩn) |
| `raw/` | Tài liệu gốc (pdf/docx không vào Git) |

## Bắt đầu nhanh

Đặt các kho cạnh nhau trong cùng một thư mục, chạy lệnh ở thư mục đó:

```bash
python kb-core/tools/new_page.py kb-base-devops/linux/selinux-basics "SELinux cơ bản" --tags concept,linux,security
python kb-core/tools/kb_index.py kb-*
python kb-core/tools/kb_lint.py kb-*
```

Chi tiết: [operations/ingest.md](operations/ingest.md), [operations/review-and-lint.md](operations/review-and-lint.md).
