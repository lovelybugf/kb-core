# CLAUDE.md — {{kb_name}}

Phạm vi: {{kho này chứa gì, không chứa gì (1–2 câu)}}

## Thứ tự đọc
1. File này → [index.md](index.md) → `_index.md` của thư mục chủ đề → mở 2–3 trang cần thiết.
2. Không đọc toàn bộ kho; chỉ mở `raw/` khi cần đối chiếu tài liệu gốc.

## Quy ước
- Chuẩn chung ở [kb-core](https://github.com/lovelybugf/kb-core/blob/main/index.md): khuôn trang, frontmatter, đặt tên, tag (chỉ dùng tag trong `kb-core/standards/tags.md`).
- Link sang kho khác là URL `https://github.com/lovelybugf/<kho>/blob/main/<đường-dẫn>` — đọc file `../<kho>/<đường-dẫn>` trên máy, không tải web.
- Mỗi trang 1 chủ đề, ≤ 500 dòng, frontmatter + dòng `**TL;DR:**` ngay đầu.
- Lệnh trong code block; giá trị môi trường dùng placeholder `<SATELLITE_FQDN>`, `<ORG>`.
- Khi trả lời: nêu đường dẫn trang đã dùng và `reliability` nếu không phải `official`/`internal-tested`.
- Sửa trang → cập nhật `updated`, chạy `python ../kb-core/tools/kb_index.py .` và `python ../kb-core/tools/kb_lint.py .`, ghi 1 dòng vào [log.md](log.md).

## Kho liên quan
- Cổng vào: [kb-hub/index.md](https://github.com/lovelybugf/kb-hub/blob/main/index.md)
- {{kho khác và quan hệ}}

## Không được
- Không lưu mật khẩu, API key, token, IP/hostname nội bộ của khách hàng.
- Không chép kiến thức đã có ở kho khác — đặt link tương đối.
- Không sửa/xoá dòng cũ trong `log.md`.
- {{điều cấm riêng của kho}}
