---
title: Quy trình đưa tài liệu mới vào kho (ingest)
tags: [process, kb-meta, kb-tooling]
source: kb-core (chuẩn nội bộ)
reliability: official
updated: 2026-11-23
owner: lovelybugf
---
**TL;DR:** Tài liệu mới (docx, pdf, web) đi qua 7 bước: chọn kho, lưu gốc vào `raw/`, trích văn bản, viết trang tóm lược trong thư mục chủ đề, cập nhật `_index.md`/`index.md`, ghi `log.md`, chạy lint rồi commit. Trang tóm lược là thứ Claude đọc; file gốc chỉ để đối chiếu.

## 1. Chọn kho và kiểm tra trùng

- Xác định kho theo bảng phạm vi ở [kb-hub](https://github.com/lovelybugf/kb-hub/blob/main/index.md). Kiến thức chung (Linux, container) vào `kb-base-devops`; riêng sản phẩm Red Hat vào `kb-redhat`.
- Tìm trang đã có trước khi tạo mới:

```bash
grep -ril "download policy" kb-*/ --include=*.md
```

- Đã có trang cùng chủ đề → bổ sung vào trang đó, không tạo trang thứ hai.

## 2. Lưu tài liệu gốc vào raw/

- Đặt tên `YYYY-MM-DD-<nguon>-<ten-ngan>.<ext>` (xem [naming.md](../standards/naming.md)).
- `raw/*.pdf`, `raw/*.docx` (và pptx, xlsx) nằm trong `.gitignore`: không vào Git. Ghi vị trí lưu gốc (URL, thư mục chia sẻ) vào trường `source` của trang tóm lược.
- Trang web: lưu URL + ngày truy cập; chỉ lưu bản sao (`.md`, `.html`) khi trang hay thay đổi và điều khoản cho phép.
- Không lưu tài liệu có mật khẩu, thông tin truy cập, IP nội bộ khách hàng vào kho; làm sạch trước.

## 3. Trích văn bản (tuỳ chọn, để viết nhanh hơn)

```bash
pandoc raw/<file>.docx -t gfm -o /tmp/<file>.md          # Word → Markdown
pdftotext -layout raw/<file>.pdf /tmp/<file>.txt          # PDF → text (poppler-utils)
```

Bản trích chỉ là nháp làm việc, không commit vào thư mục chủ đề.

## 4. Viết trang tóm lược

```bash
python kb-core/tools/new_page.py kb-redhat/satellite/<ten-trang> "Tiêu đề" --tags howto,satellite --product "Red Hat Satellite 6.16" --source "<URL hoặc tài liệu, chương/mục>"
```

- Theo [khuôn trang](../standards/page-structure.md): TL;DR trả lời ngay, lệnh trong code block, placeholder thay giá trị thật.
- Tóm lược bằng lời mình, giữ lệnh và chỉ mục nguồn (chương/mục); không chép nguyên văn dài.
- Chọn `reliability` theo [sources-and-versions.md](../standards/sources-and-versions.md). Nội dung AI sinh: `unverified` cho tới khi người kiểm.
- Một tài liệu lớn thường thành nhiều trang nhỏ, mỗi trang một chủ đề.

## 5. Cập nhật mục lục

```bash
python kb-core/tools/kb_index.py kb-redhat
```

- `kb_index.py` sinh lại khối AUTO-INDEX trong `_index.md` của mọi thư mục chủ đề.
- Thêm thư mục chủ đề mới → thêm tay 1 dòng vào `index.md` của kho: `- [Tiêu đề](thu-muc/_index.md) — tóm tắt 1 câu`.

## 6. Ghi log.md

Mỗi lần ingest một dòng, chỉ ghi thêm, không sửa dòng cũ:

```text
2026-11-23 | ingest | satellite/download-policy.md ← Satellite 6.16 Administering, Phụ lục B.7
```

## 7. Kiểm tra và commit

```bash
python kb-core/tools/kb_lint.py kb-redhat
git -C kb-redhat add -A
git -C kb-redhat commit -m "docs(satellite): thêm trang download policy"
```

Lint phải 0 lỗi. Rà lại cảnh báo "nghi chứa bí mật" trước khi commit.

## Liên quan

- [Rà soát định kỳ và lint](review-and-lint.md) · [Dùng kho với Claude](claude-usage.md) · [Template](../templates/_index.md)
