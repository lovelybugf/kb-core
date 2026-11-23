---
title: Khuôn trang tri thức
tags: [standard, kb-meta]
source: kb-core (chuẩn nội bộ)
reliability: official
updated: 2026-11-23
owner: lovelybugf
---
**TL;DR:** Mỗi trang chỉ nói về một chủ đề, dài tối đa 500 dòng, mở đầu bằng frontmatter rồi tới ngay dòng `**TL;DR:**`, thân trang chia bằng `##`. Trang dài hơn thì tách, nối với nhau bằng link tương đối; kiến thức chỉ nằm ở một kho duy nhất.

## Bố cục bắt buộc

1. Frontmatter YAML theo [frontmatter.md](frontmatter.md).
2. Dòng không rỗng đầu tiên sau frontmatter: `**TL;DR:** <1–2 câu trả lời cốt lõi>`.
3. Thân trang chia bằng `##` / `###`. Không dùng H1 (`#`): tiêu đề đã nằm ở trường `title`, viết lại chỉ tốn token.
4. Hai mục cuối nên có: `## Liên quan` (link chéo) và `## Nguồn` (tài liệu, chương/mục, URL).

```markdown
---
title: Mở rộng Logical Volume
tags: [howto, linux, lvm]
product: RHEL 9
source: https://docs.redhat.com/en/documentation/red_hat_enterprise_linux/9
reliability: internal-tested
updated: 2026-11-23
owner: lovelybugf
---
**TL;DR:** Dùng `lvextend -r` để tăng LV và filesystem trong một lệnh, không cần umount.

## Các bước
...

## Liên quan
- [LVM cơ bản](storage-lvm.md)

## Nguồn
- RHEL 9, Configuring and managing logical volumes, chương 4 — <URL>
```

## Quy tắc TL;DR

- Trả lời thẳng câu hỏi chính của trang; người đọc (và Claude) dừng ở đây được nếu chỉ cần ý chính.
- 1–2 câu, khoảng ≤ 300 ký tự. Câu đầu tiên tự đứng được vì `kb_index.py` lấy nó làm tóm tắt trong `_index.md`.
- Câu đầu không chứa chữ viết tắt có dấu chấm theo sau là khoảng trắng (kiểu "vd. ", "v.v. "): công cụ tách câu tại dấu `.` + khoảng trắng.
- Không in đậm cả câu; không đặt bảng hay khối lệnh trong TL;DR.

## Độ dài và tách trang

- Khuyến nghị ≤ 300 dòng; trần cứng 500 dòng (`kb_lint.py` báo lỗi).
- Một trang trả lời được một nhóm câu hỏi gần nhau. Khi trang vượt trần hoặc có hai chủ đề độc lập → tách:
  trang gốc giữ phần tổng quan + link, mỗi chủ đề con thành một trang (`storage-lvm.md` → `storage-lvm-extend.md`, `storage-lvm-snapshot.md`).
- Trang quá ngắn (< 15 dòng) cùng chủ đề nên gộp lại.

## Link chéo

- Chỉ dùng link Markdown tương đối, kể cả sang kho khác: `[systemd](../../kb-base-devops/linux/systemd-basics.md)`.
- Không dùng đường dẫn ổ đĩa (`C:\...`), `file://`, hay link tuyệt đối tới máy cá nhân.
- Không trùng lặp: kiến thức nằm ở đúng một kho (chọn theo [kb-hub](../../kb-hub/index.md)); nơi khác chỉ đặt link.
- Đúng chữ hoa/thường: Windows bỏ qua, GitHub/Linux thì không (lint kiểm tra).
- Link ra Internet chỉ dùng cho nguồn chính thức, ổn định.

## Câu lệnh, cấu hình, ví dụ

- Luôn đặt trong code block có ghi ngôn ngữ (`bash`, `yaml`, `ini`, `powershell`); không dùng ảnh chụp lệnh.
- Không ghi dấu nhắc `$`/`#` trong khối lệnh để copy chạy được; lệnh cần root thì ghi chú "chạy bằng root" phía trên.
- Giá trị phụ thuộc môi trường dùng placeholder chữ HOA trong `<>`: `<SATELLITE_FQDN>`, `<ORG>`, `<HOST_FQDN>`, `<LIFECYCLE_ENV>`, `<CONTENT_VIEW>`, `<REPO_ID>`.
- Tuyệt đối không ghi mật khẩu, API key, token, IP/hostname thật của khách hàng (lint cảnh báo khi phát hiện).

## Liên quan

- [Frontmatter](frontmatter.md) · [Đặt tên](naming.md) · [Tag](tags.md) · [Nguồn và phiên bản](sources-and-versions.md)
- Khuôn có sẵn: [templates/](../templates/_index.md)
