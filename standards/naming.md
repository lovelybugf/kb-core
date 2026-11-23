---
title: Quy tắc đặt tên file, thư mục, tag
tags: [standard, kb-meta]
source: kb-core (chuẩn nội bộ)
reliability: official
updated: 2026-11-23
owner: lovelybugf
---
**TL;DR:** Tên file và thư mục dùng tiếng Anh, chữ thường, kebab-case, không dấu, mô tả chủ đề chứ không mô tả loại tài liệu. Các ngoại lệ cố định gồm file đặc biệt của kho, script Python và file dữ liệu CSV.

## File và thư mục Markdown

- Mẫu: `^[a-z0-9]+(-[a-z0-9]+)*\.md$` → `storage-lvm.md`, `activation-key-registration-only.md`.
- Tên = chủ đề, đọc là hiểu: `download-policy.md` thay vì `note-01.md` hay `satellite-tips.md`.
- Không đưa tên người, tên khách hàng vào tên file. Chỉ đưa phiên bản hoặc kỳ thời gian khi chủ đề gắn với nó: `upgrade-6-16-to-6-18.md`, ghi chú thị trường theo kỳ `sjc-world-gap-2026-11.md` (kỳ đặt cuối tên).
- Thư mục chủ đề: danh từ, kebab-case: `container-orchestration/`, `ansible-aap/`.
- Không lồng quá 2 cấp thư mục chủ đề (`kho/chu-de/chu-de-con/trang.md` là sâu nhất).

## Tên dành riêng và ngoại lệ

| Tên | Ý nghĩa |
|---|---|
| `CLAUDE.md`, `README.md`, `index.md`, `log.md` | File bắt buộc ở gốc mỗi kho |
| `_index.md` | Mục lục của thư mục chủ đề (dấu `_` để luôn đứng đầu danh sách) |
| `raw/`, `templates/`, `tools/`, `data/` (cấp 1) | Thư mục dành riêng, không chứa trang nội dung |
| `templates/kb-CLAUDE.md` | Template của `CLAUDE.md`, giữ chữ hoa cho dễ nhận |
| `*.py` | snake_case (`kb_lint.py`) vì Python phải import được |
| `*.csv` | snake_case theo nội dung + tần suất: `gold_sjc_daily.csv` |
| `tickers/<MA>.csv` | Mã chứng khoán viết HOA đúng như sàn niêm yết: `FPT.csv` |

## Kho

- `kb-<lĩnh-vực>`: `kb-core`, `kb-redhat`, `kb-market-vn`. Một kho = một repo Git.

## Tài liệu gốc trong raw/

- `YYYY-MM-DD-<nguon>-<ten-ngan>.<ext>` với ngày = ngày lấy về: `2026-11-23-redhat-satellite-6-16-managing-content.pdf`.

## Tag

- Tiếng Anh, chữ thường, kebab-case, số ít: `container`, không `containers`; `kubernetes`, không `k8s`.
- Chỉ dùng tag có trong [tags.md](tags.md).

## Placeholder

- Chữ HOA, gạch dưới, trong `<>`: `<SATELLITE_FQDN>`, `<ORG>`, `<HOST_FQDN>`, `<CAPSULE_FQDN>`.

## Git

- Nhánh chính: `main`. Commit theo Conventional Commits, mô tả tiếng Việt:
  `docs(satellite): thêm trang download policy`, `fix(linux): sửa link LVM`, `chore: cập nhật mục lục`.

## Liên quan

- [Khuôn trang](page-structure.md) · [Danh mục tag](tags.md)
