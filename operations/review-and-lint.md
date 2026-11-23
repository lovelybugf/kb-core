---
title: Rà soát định kỳ và lint kho tri thức
tags: [process, kb-meta, kb-tooling]
source: kb-core (chuẩn nội bộ)
reliability: official
updated: 2026-11-23
owner: lovelybugf
---
**TL;DR:** Chạy `kb_lint.py` trước mỗi commit (phải 0 lỗi) và rà soát sâu mỗi tháng: trang mồ côi, link hỏng, trang quá cũ (`updated` quá 180 ngày), tag lạ, trang quá dài. Lỗi chặn commit; cảnh báo xử lý trong buổi rà soát.

## Lệnh

Chạy ở thư mục chứa các kho (glob `kb-*` được script tự mở rộng, dùng được cả trên PowerShell):

```bash
python kb-core/tools/kb_index.py kb-*            # cập nhật _index.md trước
python kb-core/tools/kb_lint.py kb-*             # 0 = sạch, 1 = có lỗi
python kb-core/tools/kb_lint.py kb-* --strict    # coi cảnh báo là lỗi (dùng trong buổi rà soát)
python kb-core/tools/kb_lint.py kb-* -q          # chỉ in lỗi
python kb-core/tools/kb_index.py kb-* --check    # CI: báo nếu _index.md chưa cập nhật
```

Tuỳ chọn khác: `--stale-days 180`, `--max-lines 500`, `--today YYYY-MM-DD` (mô phỏng ngày), `--tags <đường dẫn tags.md>`.

## Các kiểm tra

| Kiểm tra | Mức | Cách sửa |
|---|---|---|
| Thiếu `CLAUDE.md`, `index.md`, `log.md`, `README.md`, `.gitignore`, `raw/` | Lỗi | Tạo từ [templates](../templates/_index.md) |
| `CLAUDE.md` > 40 dòng, `index.md` > 200 dòng | Lỗi | Rút gọn, chuyển chi tiết xuống `_index.md` |
| `log.md` sai dạng `YYYY-MM-DD \| ingest\|update\|lint \| mô tả` | Lỗi | Sửa dòng mới nhất (không sửa lịch sử đúng dạng) |
| Thiếu frontmatter / trường bắt buộc / giá trị sai | Lỗi | Xem [frontmatter.md](../standards/frontmatter.md) |
| Thiếu dòng `**TL;DR:**` ngay sau frontmatter | Lỗi | Thêm 1–2 câu trả lời cốt lõi |
| Tag không có trong [tags.md](../standards/tags.md) | Lỗi | Đổi sang tag có sẵn, hoặc bổ sung tag vào kb-core trước |
| Placeholder `{{...}}` còn sót | Lỗi | Điền nội dung |
| Trang > 500 dòng | Lỗi | Tách trang theo chủ đề con |
| Link tương đối hỏng, sai hoa/thường, trỏ ổ đĩa cục bộ | Lỗi | Sửa đường dẫn; dời trang thì sửa mọi link trỏ tới |
| Trang không có trong `_index.md` (trang ở gốc: không có trong `index.md`) | Lỗi | Chạy `kb_index.py` hoặc thêm tay |
| `_index.md` không được `index.md`/`_index.md` cấp trên trỏ tới | Lỗi | Thêm dòng vào `index.md` |
| `updated` quá 180 ngày hoặc ở tương lai | Cảnh báo | Rà nội dung, cập nhật `updated`, ghi log |
| Tên file/thư mục không kebab-case, trường lạ, > 6 tag | Cảnh báo | Đổi tên (sửa link), bỏ trường lạ |
| Nghi chứa mật khẩu, khóa, token, IP nội bộ | Cảnh báo | Thay bằng placeholder `<...>`; nếu đã commit bí mật thật → đổi bí mật đó ngay |
| Link sang kho khác chưa có trên máy | Cảnh báo | Clone đủ các kho cạnh nhau rồi chạy lại |

## Lịch rà soát

- **Mỗi commit:** `kb_index.py` + `kb_lint.py` (0 lỗi).
- **Hàng tháng:** `kb_lint.py kb-* --strict`; xử lý trang quá cũ; trang `unverified` quá 90 ngày → kiểm chứng hoặc xoá; ghi `YYYY-MM-DD | lint | <kết quả>` vào `log.md` từng kho.
- **Hàng quý:** tìm trùng lặp giữa các kho (cùng chủ đề ở 2 nơi → giữ 1, nơi kia đặt link); gộp trang quá ngắn; xem lại danh mục tag (tag ít dùng, tag thiếu).
- **Khi nâng cấp sản phẩm:** rà các trang có `product` phiên bản cũ.

## Tự động hoá (tuỳ chọn)

Git hook `pre-commit` trong từng kho (file `.git/hooks/pre-commit`, cấp quyền chạy):

```bash
#!/bin/sh
python ../kb-core/tools/kb_index.py . --check || { echo "Chạy kb_index.py trước khi commit"; exit 1; }
python ../kb-core/tools/kb_lint.py . -q
```

Khi có remote, có thể chạy cùng hai lệnh trên trong CI (GitHub Actions/GitLab CI) với kb-core được checkout cạnh kho.

## Liên quan

- [Quy trình ingest](ingest.md) · [Khuôn trang](../standards/page-structure.md)
