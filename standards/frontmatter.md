---
title: Đặc tả frontmatter
tags: [standard, kb-meta, reference]
source: kb-core (chuẩn nội bộ)
reliability: official
updated: 2026-11-23
owner: lovelybugf
---
**TL;DR:** Mọi trang nội dung bắt đầu bằng frontmatter YAML có 6 trường bắt buộc (title, tags, source, reliability, updated, owner) và 1 trường tuỳ chọn (product). Mỗi trường nằm trên một dòng, danh sách viết dạng `[a, b]` để cả YAML chuẩn lẫn `kb_lint.py` đọc được.

## Mẫu

```yaml
---
title: <tiêu đề>
tags: [<tag trong kb-core/standards/tags.md>]
product: <sản phẩm + phiên bản, nếu có>
source: <URL hoặc tài liệu gốc>
reliability: official | community | internal-tested | unverified
updated: YYYY-MM-DD
owner: <người phụ trách>
---
**TL;DR:** <1–2 câu trả lời cốt lõi>
```

## Các trường

| Trường | Bắt buộc | Kiểu | Quy tắc |
|---|---|---|---|
| `title` | có | chuỗi | Tiếng Việt, ≤ 80 ký tự, nói rõ chủ đề. Chứa `: ` thì đặt trong nháy kép. |
| `tags` | có | danh sách | 1–6 tag, chỉ lấy từ [tags.md](tags.md); nên có 1 tag loại trang (`howto`, `runbook`, ...). |
| `product` | không | chuỗi | Sản phẩm + phiên bản đã đối chiếu: `Red Hat Satellite 6.16`, `RHEL 9`. Bỏ trống nếu không gắn sản phẩm. |
| `source` | có | chuỗi | URL hoặc tên tài liệu gốc + chương/mục. Nhiều nguồn: ngăn bằng `;`, chi tiết ghi ở mục `## Nguồn`. |
| `reliability` | có | enum | `official`, `community`, `internal-tested`, `unverified` — xem [sources-and-versions.md](sources-and-versions.md). |
| `updated` | có | ngày | `YYYY-MM-DD`, ngày sửa nội dung có ý nghĩa gần nhất (sửa chính tả không cần đổi). |
| `owner` | có | chuỗi | Người phụ trách nội dung (tên đăng nhập Git). |

## Cú pháp được phép

- Một trường một dòng: `key: value`. Không viết giá trị nhiều dòng (`|`, `>`).
- Danh sách: `[a, b, c]` trên một dòng (khuyến nghị) hoặc mỗi phần tử một dòng `- a` ngay dưới khoá.
- Giá trị chứa `: ` hoặc bắt đầu bằng ký tự đặc biệt YAML (`[`, `{`, `*`, `&`, `#`, `-`, ...) → đặt trong nháy kép.
- Không thêm trường ngoài danh sách trên; cần trường mới thì sửa trang này và `tools/kb_common.py` trước.

## File không cần frontmatter

`CLAUDE.md`, `README.md`, `index.md`, `_index.md`, `log.md`, mọi file trong `raw/`, `templates/`, `tools/`, `data/` ở cấp 1 của kho.

## Kiểm tra

`python kb-core/tools/kb_lint.py <kho>` báo lỗi khi thiếu frontmatter, thiếu/rỗng trường bắt buộc, `reliability` ngoài danh sách, `updated` sai định dạng, tag không có trong danh mục; cảnh báo khi `updated` quá 180 ngày hoặc có trường lạ.

## Liên quan

- [Khuôn trang](page-structure.md) · [Danh mục tag](tags.md) · [Nguồn và phiên bản](sources-and-versions.md)
