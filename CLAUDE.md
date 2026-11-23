# CLAUDE.md — kb-core

Phạm vi: chuẩn viết và vận hành tri thức dùng chung cho mọi kho `kb-*` (khuôn trang, frontmatter, đặt tên, tag, nguồn), quy trình ingest/lint, template và công cụ Python. Không chứa kiến thức kỹ thuật sản phẩm.

## Thứ tự đọc
1. File này → [index.md](index.md) → `_index.md` của nhóm cần (standards, operations, templates) → mở 1–2 trang.
2. Không đọc toàn bộ kho; `tools/*.py` chỉ mở khi cần sửa công cụ.

## Quy ước
- Mỗi trang 1 chủ đề, ≤ 500 dòng, frontmatter + dòng `**TL;DR:**` ngay sau frontmatter.
- Tag chỉ lấy từ [standards/tags.md](standards/tags.md); thêm tag mới = sửa file đó trước.
- Lệnh trong code block; giá trị môi trường dùng placeholder `<SATELLITE_FQDN>`, `<ORG>`.
- Đổi chuẩn ở đây có thể làm kho khác lỗi lint → chạy lint cho mọi kho trước khi commit.

## Công cụ (Python 3.8+, chỉ thư viện chuẩn, chạy ở thư mục chứa các kho)
- `python kb-core/tools/kb_lint.py kb-*` — kiểm tra, thoát mã 1 nếu có lỗi.
- `python kb-core/tools/kb_index.py kb-*` — sinh lại khối AUTO-INDEX trong `_index.md`.
- `python kb-core/tools/new_page.py <kho>/<thu-muc>/<ten-file> "Tiêu đề"` — tạo trang từ template.

## Kho liên quan
- Cổng vào: [../kb-hub/index.md](../kb-hub/index.md). Mọi kho khác tham chiếu chuẩn ở đây bằng link `../kb-core/...`.

## Không được
- Không lưu mật khẩu, API key, token, IP/hostname nội bộ của khách hàng.
- Không chép nội dung chuẩn sang kho khác — chỉ đặt link tương đối.
- Không sửa/xoá dòng cũ trong `log.md` (chỉ ghi thêm).
- Không thêm thư viện ngoài vào `tools/` (chỉ thư viện chuẩn Python).
