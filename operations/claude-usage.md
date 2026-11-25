---
title: Dùng kho tri thức với Claude (Projects, Claude Code, API)
tags: [howto, claude, kb-meta]
product: Claude Code, Claude API (model claude-opus-5-5)
source: https://platform.claude.com/docs/en/build-with-claude/prompt-caching
reliability: unverified
updated: 2026-11-25
owner: lovelybugf
---
**TL;DR:** Cho Claude đọc theo tầng: `CLAUDE.md` → `index.md` → `_index.md` của chủ đề → 2–3 trang cần thiết, không nạp cả kho. Với API, đặt `CLAUDE.md` + `index.md` (phần ổn định) ở đầu system prompt có `cache_control` để các câu hỏi sau đọc từ cache với giá thấp hơn nhiều.

## Nguyên tắc chung

- Đọc mục lục trước (progressive disclosure): mỗi tầng chỉ vài trăm token, đủ để chọn đúng trang.
- Câu hỏi thuộc kho nào → chỉ mở kho đó (bảng ở [kb-hub](https://github.com/lovelybugf/kb-hub/blob/main/index.md)).
- Giữ `CLAUDE.md` ≤ 40 dòng, `index.md` ≤ 200 dòng: đây là phần nạp mọi lần.
- Link sang kho khác là URL GitHub (`https://github.com/lovelybugf/<kho>/blob/main/...`); khi các kho đã clone cạnh nhau, Claude đọc file `../<kho>/...` trên máy thay vì tải web.
- Dữ liệu số (CSV ở kb-market-vn) không nạp vào ngữ cảnh; cho Claude lọc bằng công cụ (grep, pandas).

## Claude Code

Làm việc trong một kho:

```bash
cd kb-redhat
claude
```

`CLAUDE.md` ở thư mục làm việc được nạp tự động. Cần nhiều kho cùng lúc:

```bash
cd kb-hub
claude --add-dir ../kb-redhat --add-dir ../kb-core
```

`CLAUDE.md` của thư mục thêm bằng `--add-dir` có thể không được nạp tự động; nhắc Claude đọc `../kb-redhat/CLAUDE.md` trước. Prompt mẫu:

```text
Đọc kb-redhat/CLAUDE.md và index.md, mở _index.md của satellite, rồi trả lời:
đổi lifecycle environment cho host đã đăng ký thế nào? Trích nguồn và đường dẫn trang.
```

Khi Claude viết hoặc sửa trang: yêu cầu tuân theo [khuôn trang](../standards/page-structure.md), đặt `reliability: unverified`, chạy `kb_index.py` + `kb_lint.py` và ghi `log.md`.

## Claude Projects (claude.ai)

- Project instructions: dán nội dung `CLAUDE.md` của kho.
- Project knowledge: tải `index.md`, các `_index.md` và chỉ những trang liên quan tới mục đích Project; không tải `raw/` hay CSV lớn.
- Mỗi Project nên gắn với một kho (hoặc một chủ đề) để tri thức nền gọn.
- Sau khi sửa trang trong Git, tải lại file tương ứng vào Project (Project không tự đồng bộ với repo).

## Claude API: prompt caching cho CLAUDE.md + index.md

Cache khớp theo tiền tố (prefix): thứ tự dựng prompt là `tools` → `system` → `messages`; đổi một byte trong tiền tố làm mất cache phía sau. Vì vậy:

1. Đầu system prompt: nội dung ổn định — `CLAUDE.md` + `index.md` (+ `_index.md` hay dùng). Đặt `cache_control` ở khối cuối của phần ổn định.
2. Sau đó mới tới phần thay đổi theo câu hỏi: trang được chọn, câu hỏi của người dùng (trong `messages`).
3. Không chèn thời gian hiện tại, ID yêu cầu… vào phần ổn định.

```python
from pathlib import Path
import anthropic

kb = Path("kb-redhat")
stable = "\n\n".join((kb / f).read_text(encoding="utf-8") for f in ("CLAUDE.md", "index.md"))

client = anthropic.Anthropic()  # đọc ANTHROPIC_API_KEY từ biến môi trường
response = client.messages.create(
    model="claude-opus-5-5",
    max_tokens=16000,
    system=[
        {"type": "text", "text": "Bạn trả lời dựa trên kho tri thức dưới đây. Trích đường dẫn trang."},
        {"type": "text", "text": stable, "cache_control": {"type": "ephemeral"}},
    ],
    messages=[{"role": "user", "content": "Đổi Capsule cho host đã đăng ký thế nào?"}],
)
print(response.usage.cache_creation_input_tokens, response.usage.cache_read_input_tokens)
```

Số liệu cần nhớ (theo tài liệu prompt caching, kiểm lại trước khi tính chi phí):

| Mục | Giá trị |
|---|---|
| TTL mặc định | 5 phút (`{"type": "ephemeral"}`), mỗi lần đọc trúng làm mới TTL |
| TTL dài | 1 giờ (`{"type": "ephemeral", "ttl": "1h"}`) — đáng dùng khi các câu hỏi cách nhau 5–60 phút |
| Giá ghi cache | ~1,25× giá input (TTL 5 phút), ~2× (TTL 1 giờ) |
| Giá đọc cache | ~0,1× giá input; Claude Opus 5.5 khoảng 0,05× |
| Tiền tố tối thiểu | 512 token với các model thế hệ 5.x; ngắn hơn thì không cache (không báo lỗi) |
| Số breakpoint tối đa | 4 `cache_control` mỗi request |

- Kiểm tra cache hoạt động: `usage.cache_read_input_tokens` phải > 0 từ lần gọi thứ hai trở đi.
- `CLAUDE.md` + `index.md` của một kho thường chỉ vài nghìn token, vượt ngưỡng tối thiểu nên rẻ khi đọc lại.
- Để Claude tự chọn trang: khai báo một tool `read_page(path)` chỉ cho đọc file `.md` trong kho; trả nội dung trang làm `tool_result`. Phần này nằm sau breakpoint nên không làm hỏng cache.
- Đưa vào production: xử lý `stop_reason` (`max_tokens`, `refusal`) trước khi đọc nội dung trả về; xem hướng dẫn chính thức về fallback khi bị từ chối.

## Sự cố khi dùng Claude Code trên Windows

Đã gặp và kiểm chứng ngày 2026-11-25:

- **App Claude desktop (gói MSIX) ảo hoá `%LOCALAPPDATA%`:** thư mục mới mà lệnh chạy từ Claude (công cụ Bash/PowerShell) tạo dưới `%LOCALAPPDATA%` thực ra nằm ở `AppData\Local\Packages\Claude_<id>\LocalCache\Local\...`; tiến trình ngoài app (Task Scheduler, terminal riêng) dùng đường dẫn thật. Hệ quả: file log do scheduled task ghi trông như không đổi khi Claude đọc. Kiểm tra bằng task tạm `cmd /c copy "%LOCALAPPDATA%\<...>\file" "%TEMP%\<...>"` rồi đọc bản sao; `%TEMP%`, `%USERPROFILE%\.claude` và thư mục dự án không bị ảnh hưởng.
- **Hook trên Windows:** dùng dạng exec — `command` là đường dẫn `python.exe`, `args` là danh sách tham số — không qua shell nên đường dẫn có dấu cách không cần trích dẫn. SessionEnd mặc định chỉ có 1,5 giây: đặt `timeout`. Chi tiết: [session-capture.md](session-capture.md).
- **`python` trỏ tới alias Microsoft Store** (`WindowsApps\python.exe`) trong shell mở trước khi cài Python: gọi đường dẫn đầy đủ hoặc mở shell mới.
- **In tiếng Việt từ Python bị lỗi** khi đầu ra bị chuyển hướng (console dùng bảng mã cp125x): gọi `sys.stdout.reconfigure(encoding="utf-8", errors="replace")` ở đầu script.

## Liên quan

- [Quy trình ingest](ingest.md) · [Khuôn trang](../standards/page-structure.md) · [Rà soát và lint](review-and-lint.md)
- [Tự ghi phiên Claude Code vào kho (kb-capture)](session-capture.md)

## Nguồn

- Anthropic, Prompt caching — https://platform.claude.com/docs/en/build-with-claude/prompt-caching
- Claude Code docs — https://code.claude.com/docs
- Trang do AI soạn ngày 2026-11-23 (`unverified`): kiểm lại bảng số liệu với tài liệu chính thức trước khi dùng để tính chi phí.
