---
title: Tự ghi phiên Claude Code vào kho tri thức (skill kb-capture)
tags: [process, claude, kb-tooling]
product: Claude Code (CLI, tab Code của app desktop)
source: "https://code.claude.com/docs/en/hooks; https://code.claude.com/docs/en/skills"
reliability: internal-tested
updated: 2026-11-25
owner: lovelybugf
---
**TL;DR:** Khi một phiên Claude Code kết thúc, hook SessionEnd đưa phiên vào hàng đợi trên máy; phiên sau mở ra, hook SessionStart nhắc "còn N phiên chưa ghi". Người dùng gõ `/kb-capture queue` (hoặc `/kb-capture` để ghi phiên đang chạy), skill sẽ lọc ý đáng ghi, viết trang theo chuẩn kb-core, lọc thông tin nhạy cảm, lint, commit và push.

## Thành phần

| Thành phần | Vị trí | Vai trò |
|---|---|---|
| Skill `kb-capture` | `tools/claude/skills/kb-capture/SKILL.md` (kho này), nối vào `~/.claude/skills/kb-capture` bằng junction | Quy trình ghi: chọn nguồn → lọc ý → chọn kho, tránh trùng → viết trang → lọc nhạy cảm → lint → log → commit, push |
| Script hàng đợi | `tools/kb_session_hook.py` | Hook `session-end`, `session-start`; lệnh `list`, `digest`, `done`, `skip`, `scan` |
| Hook | `~/.claude/settings.json` | SessionEnd → `session-end`; SessionStart (`startup`, `resume`) → `session-start` |
| Hàng đợi, blocklist, log | `~/.claude/kb-capture/` (`queue.jsonl`, `blocklist.txt`, `hook.log`) | Chỉ trên máy, không vào Git |

## Luồng hoạt động

1. **Phiên kết thúc** → `session-end` đọc transcript (bỏ qua phần lớn dòng, file 130 MB mất < 1 giây), đưa phiên vào hàng đợi trừ khi: không có lời người dùng, câu trả lời quá ngắn, hoặc phiên đó đã chạy kb-capture (tránh vòng lặp).
2. **Phiên mới mở** → `session-start` đếm phiên đang chờ; có thì đưa lời nhắc vào ngữ cảnh của Claude và hiện một dòng cho người dùng. Chỉ nhắc lại sau 6 giờ, trừ khi số phiên chờ thay đổi.
3. **Người dùng đồng ý** → `/kb-capture queue`: skill đọc từng phiên qua `digest` (chỉ lời người dùng và câu trả lời dạng chữ, bỏ kết quả tool), ghi trang, rồi `done`/`skip` phiên đó.
4. Bất kỳ lúc nào: `/kb-capture` (phiên hiện tại) hoặc `/kb-capture <mã-phiên>`; nói "lưu vào kb" cũng kích hoạt skill.

## Cài đặt trên máy mới

1. Clone 5 kho cạnh nhau (xem `README.md` của kb-hub); cài Python 3.8+.
2. Nối skill (PowerShell, không cần quyền admin):

```powershell
New-Item -ItemType Junction -Path "$env:USERPROFILE\.claude\skills\kb-capture" -Target "<KB_ROOT>\kb-core\tools\claude\skills\kb-capture"
```

3. Thêm vào `~/.claude/settings.json` (gộp với nội dung sẵn có, JSON thuần, không chú thích):

```json
{
  "env": {"KB_ROOT": "<KB_ROOT dạng C:/...>", "KB_PYTHON": "<đường dẫn python.exe dạng C:/...>"},
  "hooks": {
    "SessionEnd": [{"hooks": [{"type": "command", "command": "<python.exe>",
      "args": ["-I", "<KB_ROOT>\\kb-core\\tools\\kb_session_hook.py", "session-end"], "timeout": 30}]}],
    "SessionStart": [{"matcher": "startup|resume", "hooks": [{"type": "command", "command": "<python.exe>",
      "args": ["-I", "<KB_ROOT>\\kb-core\\tools\\kb_session_hook.py", "session-start"], "timeout": 15}]}]
  }
}
```

4. Tạo `~/.claude/kb-capture/blocklist.txt`: mỗi dòng một tên khách hàng, tên miền, tên người cần chặn (không phân biệt hoa/thường). File này không bao giờ đưa vào Git.
5. Mở phiên mới (hook và skill đọc lúc phiên khởi động), kiểm tra bằng `/hooks` và gõ thử `/kb-capture`.

Dạng `command` + `args` gọi thẳng `python.exe`, không qua shell nên đường dẫn có dấu cách không cần trích dẫn. SessionEnd mặc định chỉ có 1,5 giây nên phải đặt `timeout`.

## Lệnh tay

```bash
"$KB_PYTHON" "$KB_ROOT/kb-core/tools/kb_session_hook.py" list                     # phiên đang chờ
"$KB_PYTHON" "$KB_ROOT/kb-core/tools/kb_session_hook.py" digest <mã-phiên>        # xem nội dung rút gọn
"$KB_PYTHON" "$KB_ROOT/kb-core/tools/kb_session_hook.py" skip <mã-phiên> --note "không cần ghi"
"$KB_PYTHON" "$KB_ROOT/kb-core/tools/kb_session_hook.py" scan <file.md>           # kiểm từ cấm trước khi commit
```

Mã phiên nhận tiền tố (8 ký tự đầu là đủ).

## An toàn

- Các kho là repo **public**: skill bắt buộc thay giá trị thật bằng placeholder, chạy `scan` (blocklist) và `kb_lint.py --strict` (bắt mật khẩu, khoá, IP nội bộ) trước khi commit; nghi ngờ thì bỏ chi tiết đó.
- Nội dung ghi từ phiên mặc định `reliability: unverified`, chỉ nâng lên `internal-tested` khi lệnh đã chạy thật trong phiên có kết quả.
- Skill commit và push ngay (người dùng đã chọn); muốn duyệt trước khi push thì sửa bước 7 trong SKILL.md.

## Giới hạn đã biết

- Chỉ áp dụng cho phiên Claude Code trên máy này; chat trên claude.ai không có hook và không ghi được file local.
- Đóng phiên trên app desktop có kích hoạt SessionEnd hay không: tài liệu không nói rõ — xem `~/.claude/kb-capture/hook.log` sau vài phiên để xác nhận.
- Định dạng transcript là định dạng nội bộ của Claude Code, có thể đổi giữa các phiên bản; khi `digest` ra rỗng hoặc lạ, kiểm tra lại `read_transcript()` trong script.
- Transcript bị xoá sau `cleanupPeriodDays` (mặc định 30 ngày): phiên chờ quá lâu sẽ mất nội dung (`list` đánh dấu "MẤT transcript").

## Liên quan

- [Dùng kho với Claude](claude-usage.md) · [Quy trình ingest](ingest.md) · [Rà soát và lint](review-and-lint.md)

## Nguồn

- Claude Code docs — Hooks reference (SessionStart, SessionEnd, exec form `args`) — https://code.claude.com/docs/en/hooks
- Claude Code docs — Skills (`~/.claude/skills`, frontmatter, `$ARGUMENTS`) — https://code.claude.com/docs/en/skills
- Đã chạy thử 2026-11-25: `session-end` trên transcript 8–133 MB (0,3–0,7 giây), lọc phiên kb-capture/phiên ngắn, `session-start` xuất JSON nhắc và chặn nhắc lặp, `scan` bắt từ cấm.
