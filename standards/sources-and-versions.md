---
title: Ghi nguồn, phiên bản và độ tin cậy
tags: [standard, kb-meta]
source: kb-core (chuẩn nội bộ)
reliability: official
updated: 2026-11-23
owner: lovelybugf
---
**TL;DR:** Mỗi trang ghi nguồn ngắn ở trường `source`, nguồn chi tiết (tài liệu, phiên bản, chương/mục, URL) ở mục `## Nguồn`, phiên bản sản phẩm đã đối chiếu ở `product`. Độ tin cậy chọn một trong 4 mức official, internal-tested, community, unverified; nội dung do AI sinh mặc định là unverified cho tới khi người kiểm tra.

## Ghi nguồn

- Trường `source`: một dòng, đủ để tìm lại tài liệu: URL, hoặc `"<Sản phẩm phiên bản> — <Tên tài liệu>, <chương/mục>"`.
- Mục `## Nguồn` cuối trang, mỗi nguồn một dòng:
  `- <Tên tài liệu>, <phiên bản>, <chương/mục> — <URL>`.
- Trích nguồn đến mức chương/mục để người khác kiểm lại được; với web ghi thêm ngày truy cập nếu trang hay thay đổi.
- Tài liệu gốc lưu ở `raw/` (xem [ingest](../operations/ingest.md)); file lớn bị `.gitignore` thì ghi vị trí gốc (URL, thư mục chia sẻ) trong `source`.
- Không chép nguyên văn dài từ tài liệu có bản quyền; tóm lược bằng lời mình + lệnh + chỉ mục nguồn.

## Phiên bản sản phẩm

- `product` ghi phiên bản đã đối chiếu thật sự: `Red Hat Satellite 6.16`, không ghi `Satellite 6.x`.
- Nội dung đúng cho nhiều phiên bản: ghi phiên bản thấp nhất đã kiểm, thêm câu "Áp dụng từ 6.16; đã đối chiếu 6.19" trong thân trang.
- Khác biệt giữa phiên bản: tách mục `### Từ 6.18` hoặc tách trang, không trộn lẫn.
- Khi nâng cấp sản phẩm: rà các trang có `product` cũ, cập nhật hoặc ghi "chưa kiểm trên phiên bản mới".
- `_index.md` của mỗi sản phẩm ghi phiên bản đang dùng và link tài liệu chính thức.

## Độ tin cậy (`reliability`)

| Mức | Khi nào dùng | Được dùng làm căn cứ thay đổi production? |
|---|---|---|
| `official` | Đối chiếu với tài liệu chính thức của hãng/tổ chức phát hành (docs.redhat.com, kubernetes.io, man page), hoặc chuẩn nội bộ đã duyệt (kb-core). | Có, sau khi kiểm phiên bản |
| `internal-tested` | Đã chạy thử trong lab/môi trường của mình; ghi ngày, phiên bản, kết quả trong trang. | Có |
| `community` | Blog, forum, Stack Overflow, bài viết cộng đồng; chưa đối chiếu tài liệu hãng. | Không, phải kiểm trước |
| `unverified` | Ghi chép nhanh, nhớ lại, nội dung do AI sinh chưa có người kiểm. | Không |

Nâng mức: `unverified`/`community` → `official` khi đã đối chiếu tài liệu hãng; → `internal-tested` khi đã chạy lab. Hạ mức khi phát hiện sai lệch hoặc phiên bản mới thay đổi hành vi. Mỗi lần đổi mức ghi 1 dòng `update` vào `log.md`.

## Dữ liệu số (kb-market-vn)

- Mỗi dòng dữ liệu có cột `source`; danh mục nguồn, điều khoản, tần suất cập nhật ở `kb-market-vn/sources.md`.
- Không tự điền, nội suy hay ước đoán số liệu.

## Liên quan

- [Frontmatter](frontmatter.md) · [Khuôn trang](page-structure.md) · [Quy trình ingest](../operations/ingest.md)
