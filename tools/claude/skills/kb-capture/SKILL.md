---
name: kb-capture
description: Ghi kiến thức dùng lại được từ phiên Claude Code vào hệ thống kho tri thức kb-* (kb-core, kb-base-devops, kb-redhat, kb-market-vn) đúng chuẩn kb-core — chọn kho, tránh trùng, lọc tên khách hàng và bí mật, chạy kb_index/kb_lint, ghi log, commit và push. Dùng khi người dùng gõ /kb-capture, nói "lưu vào kb", "ghi vào kho tri thức", "cập nhật kb", "kết thúc phiên", hoặc khi lời nhắc [kb-capture] đầu phiên báo còn phiên chưa ghi và người dùng đồng ý xử lý.
argument-hint: "[current | queue | <mã-phiên>]"
---

# kb-capture — ghi phiên làm việc vào kho tri thức

Trả lời người dùng bằng tiếng Việt. Nguồn cần ghi: `$ARGUMENTS` (trống = `current`).

## 0. Chuẩn bị

- Cần hai biến môi trường (đặt trong `~/.claude/settings.json`, khoá `env`): `KB_ROOT` — thư mục chứa các kho `kb-*`; `KB_PYTHON` — đường dẫn `python.exe`. Thiếu biến nào → dừng và báo người dùng.
- Helper (gọi bằng Bash, mọi đường dẫn trong nháy kép vì có dấu cách):
  `"$KB_PYTHON" "$KB_ROOT/kb-core/tools/kb_session_hook.py" <lệnh>` — lệnh: `list`, `digest <mã>`, `done <mã> --note "..."`, `skip <mã> --note "..."`, `scan <file...>`.
- Chạy `git -C "$KB_ROOT/<kho>" pull --ff-only` cho các kho sắp sửa (kb-market-vn còn được GitHub Actions commit).

## 1. Chọn nguồn

| `$ARGUMENTS` | Làm gì |
|---|---|
| trống / `current` | Ghi từ chính phiên đang chạy (nội dung đã có trong ngữ cảnh). |
| `queue` | `list` → xử lý lần lượt từng phiên đang chờ, cũ trước; mỗi phiên lấy nội dung bằng `digest <mã>`. |
| `<mã-phiên>` | `digest <mã>` rồi xử lý phiên đó. |

Không mở trực tiếp file transcript `.jsonl` (hàng chục–hàng trăm MB): chỉ dùng `digest`. Digest có thể bị lược bớt ở giữa; chi tiết nào cần mà bị lược thì bỏ qua, không đoán.

## 2. Lọc ý đáng ghi

Ghi: quy trình đã chạy thành công, lệnh đã kiểm chứng kèm kết quả, triệu chứng → nguyên nhân → cách xử lý, quyết định kèm lý do, giải thích khái niệm có nguồn, kết quả đối chiếu tài liệu hãng (chương/mục).

Không ghi: trạng thái công việc dở dang; chi tiết riêng của dự án/khách hàng (tên, FQDN, IP, tài khoản, cấu hình riêng); việc chỉ làm một lần; suy đoán chưa kiểm; thứ đã có trong kho; chuyện vận hành chính hệ thống kb (trừ khi đổi chuẩn kb-core).

Liệt kê mỗi ý thành một câu hỏi mà trang sẽ trả lời. Không còn ý nào → `skip <mã> --note "không có kiến thức dùng lại"`, báo người dùng một dòng và dừng với phiên đó.

## 3. Chọn kho và trang

1. Đọc `$KB_ROOT/kb-hub/index.md` (định tuyến) → `CLAUDE.md` + `index.md` của kho đích → `_index.md` của thư mục chủ đề.
2. Tìm trùng trước khi tạo: `grep -ril "<từ khoá>" "$KB_ROOT"/kb-*/ --include=*.md`. Đã có trang cùng chủ đề → bổ sung trang đó (thêm mục, cập nhật `updated`, thêm nguồn), không tạo trang thứ hai.
3. Trang mới (chạy trong `$KB_ROOT`):
   `"$KB_PYTHON" kb-core/tools/new_page.py <kho>/<thu-muc>/<ten-file> "Tiêu đề" -t page|runbook|troubleshooting|decision-record --tags a,b --product "..."`
   Thư mục chủ đề mới → thêm một dòng vào `index.md` của kho. Tag mới → thêm vào `kb-core/standards/tags.md` trước.

## 4. Viết theo chuẩn kb-core

- Khuôn: `kb-core/standards/page-structure.md` — frontmatter đủ trường, dòng `**TL;DR:**` ngay sau frontmatter, không H1, ≤ 500 dòng; tag chỉ lấy từ `kb-core/standards/tags.md`.
- `source`: tài liệu gốc (nếu có) + `Phiên Claude Code YYYY-MM-DD (<8 ký tự đầu mã phiên>)`.
- `reliability`: `internal-tested` khi lệnh đã chạy thật trong phiên và có kết quả; `official` khi đã đối chiếu tài liệu hãng (ghi chương/mục ở `## Nguồn`); còn lại `unverified`.
- Tóm lược bằng lời mình; lệnh trong code block; giá trị thật thay bằng placeholder `<SATELLITE_FQDN>`, `<ORG>`, `<HOST_FQDN>`...
- Link trong cùng kho: tương đối. Sang kho khác: `https://github.com/lovelybugf/<kho>/blob/main/<đường-dẫn>`.

## 5. Lọc thông tin nhạy cảm — bắt buộc, các kho là repo PUBLIC

- Rà từng trang đã sửa: không còn tên khách hàng/tổ chức, tên người, FQDN, IP, hostname, tài khoản, email, mật khẩu, token, khoá, đường dẫn máy cá nhân.
- Chạy `scan <các file đã sửa>` (đối chiếu blocklist cục bộ `~/.claude/kb-capture/blocklist.txt`) → phải 0 vi phạm. Không bao giờ chép nội dung blocklist vào kho hay vào câu trả lời.
- Còn nghi ngờ một chi tiết là riêng khách hàng hoặc bí mật → bỏ chi tiết đó.

## 6. Kiểm tra và ghi log

- Trong `$KB_ROOT`: `"$KB_PYTHON" kb-core/tools/kb_index.py <kho>` rồi `"$KB_PYTHON" kb-core/tools/kb_lint.py kb-* --strict` → phải 0 lỗi, 0 cảnh báo; sửa tới khi sạch.
- Ghi `log.md` của kho, mỗi trang một dòng: `YYYY-MM-DD | ingest | <đường-dẫn-trang> ← phiên Claude Code <id8>`.

## 7. Commit và push

Người dùng đã cho phép push ngay, không cần hỏi lại. Với mỗi kho có thay đổi:

```bash
git -C "$KB_ROOT/<kho>" add -A
git -C "$KB_ROOT/<kho>" commit -m "docs(<chủ-đề>): <mô tả ngắn>"   # thêm trailer attribution mà phiên quy định, nếu có
git -C "$KB_ROOT/<kho>" push
```

Push lỗi (xung đột, mạng) → `pull --rebase` một lần rồi push lại; vẫn lỗi thì báo người dùng, không force push.

## 8. Đóng hàng đợi và báo cáo

- Phiên lấy từ hàng đợi: `done <mã> --note "<n> trang"` (hoặc `skip` như bước 2).
- Báo cáo ngắn: mỗi trang tạo/cập nhật kèm URL GitHub, các ý đã bỏ qua và lý do, commit đã push.
