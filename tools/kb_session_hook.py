#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hàng đợi phiên Claude Code cần ghi vào kho tri thức kb-* (dùng cùng skill kb-capture).

Hook trong ~/.claude/settings.json (gọi thẳng python, không qua shell):
  SessionEnd   → kb_session_hook.py session-end    đọc JSON hook từ stdin, thêm phiên vào hàng đợi
  SessionStart → kb_session_hook.py session-start  còn phiên chưa ghi → nhắc Claude và người dùng
Lệnh cho skill kb-capture và người dùng:
  list                        liệt kê phiên đang chờ ghi vào KB
  digest <session|đường dẫn>  in phần hội thoại (lời người dùng + câu trả lời dạng chữ), bỏ kết quả tool
  done <session...>           đánh dấu đã ghi vào KB      skip <session...>  bỏ qua (không có gì đáng ghi)
  scan <file...>              tìm từ cấm (tên khách hàng, ...) trong blocklist cục bộ; mã thoát 1 nếu có
Dữ liệu cục bộ, không vào Git: ~/.claude/kb-capture/ (queue.jsonl, blocklist.txt, hook.log);
đổi thư mục bằng biến môi trường KB_CAPTURE_DIR. Hook không bao giờ làm hỏng phiên: lỗi chỉ ghi vào hook.log.
"""

import argparse
import datetime as dt
import json
import os
import re
import sys
import traceback
from pathlib import Path

STATE_DIR = Path(os.environ.get("KB_CAPTURE_DIR") or (Path.home() / ".claude" / "kb-capture"))
QUEUE = STATE_DIR / "queue.jsonl"
BLOCKLIST = STATE_DIR / "blocklist.txt"
HOOK_LOG = STATE_DIR / "hook.log"
PROJECTS_DIR = Path.home() / ".claude" / "projects"
SKILL_COMMAND = "/kb-capture"
MIN_ASSISTANT_CHARS = 200       # phiên quá ngắn thì không đưa vào hàng đợi
REMIND_EVERY = dt.timedelta(hours=6)
SYSTEM_PREFIXES = ("<task-notification", "<command-name>", "<command-message>", "<command-args>",
                   "<local-command", "<system-reminder", "<bash-input>", "<bash-stdout>",
                   "<bash-stderr>", "<user-memory-input>", "Caveat:")


# ------------------------------------------------------------------- tiện ích
def setup_stdout():
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass


def now():
    return dt.datetime.now().astimezone()


def log(message):
    try:
        STATE_DIR.mkdir(parents=True, exist_ok=True)
        with open(str(HOOK_LOG), "a", encoding="utf-8") as f:
            f.write("%s %s\n" % (now().isoformat(timespec="seconds"), message))
    except OSError:
        pass


def append_event(event):
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    event.setdefault("at", now().isoformat(timespec="seconds"))
    with open(str(QUEUE), "a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def read_events():
    if not QUEUE.is_file():
        return []
    events = []
    with open(str(QUEUE), encoding="utf-8") as f:
        for line in f:
            try:
                events.append(json.loads(line))
            except ValueError:
                continue
    return events


def sessions_state(events=None):
    """Gộp các sự kiện thành trạng thái mới nhất của từng phiên."""
    state = {}
    for e in events if events is not None else read_events():
        sid = e.get("session_id")
        if not sid:
            continue
        if e.get("event") == "end":
            entry = state.setdefault(sid, {})
            entry.update({k: v for k, v in e.items() if k not in ("event",)})
            entry["status"] = "pending"
        elif e.get("event") in ("done", "skip") and sid in state:
            state[sid]["status"] = e["event"]
            state[sid]["note"] = e.get("note", "")
    return state


def read_stdin_json():
    try:
        raw = sys.stdin.read()
    except (OSError, ValueError):
        return {}
    try:
        return json.loads(raw) if raw.strip() else {}
    except ValueError:
        return {}


# ------------------------------------------------------------------- transcript
def _texts(content):
    if isinstance(content, str):
        return [content]
    if isinstance(content, list):
        return [b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text"]
    return []


def read_transcript(path):
    """(tiêu đề, [(vai, văn bản, thời điểm)], có_gọi_kb_capture) — chỉ hội thoại chính, bỏ tool."""
    title, messages, capture_session = "", [], False
    with open(str(path), encoding="utf-8", errors="replace") as f:
        for line in f:
            if '"custom-title"' not in line and '"type":"user"' not in line \
                    and '"type":"assistant"' not in line:
                continue  # bỏ nhanh các dòng không cần (file có thể hàng trăm MB)
            try:
                o = json.loads(line)
            except ValueError:
                continue
            kind = o.get("type")
            if kind == "custom-title":
                title = o.get("customTitle") or title
                continue
            if kind not in ("user", "assistant") or o.get("isSidechain") or o.get("isMeta"):
                continue
            msg = o.get("message") or {}
            content = msg.get("content")
            if kind == "assistant" and isinstance(content, list):
                for b in content:  # Claude tự gọi skill kb-capture (không qua lệnh /kb-capture)
                    if isinstance(b, dict) and b.get("type") == "tool_use" and b.get("name") == "Skill" \
                            and str((b.get("input") or {}).get("skill", "")).endswith("kb-capture"):
                        capture_session = True
            for text in _texts(content):
                text = text.strip()
                if not text:
                    continue
                if kind == "user" and "<command-name>%s</command-name>" % SKILL_COMMAND in text:
                    capture_session = True
                if kind == "user" and text.startswith(SYSTEM_PREFIXES):
                    continue
                messages.append(("user" if kind == "user" else "assistant", text, o.get("timestamp", "")))
    return title, messages, capture_session


def find_transcript(ref):
    """Đường dẫn transcript từ đường dẫn, mã phiên hoặc tiền tố mã phiên."""
    path = Path(ref)
    if path.suffix == ".jsonl" and path.is_file():
        return path
    for sid, entry in sessions_state().items():
        if sid.startswith(ref) and Path(entry.get("transcript_path", "")).is_file():
            return Path(entry["transcript_path"])
    matches = sorted(PROJECTS_DIR.glob("*/%s*.jsonl" % ref)) if PROJECTS_DIR.is_dir() else []
    return matches[0] if len(matches) == 1 else None


def clip(text, limit):
    if len(text) <= limit:
        return text
    head = int(limit * 0.7)
    return text[:head] + "\n[… lược %d ký tự …]\n" % (len(text) - limit) + text[-(limit - head):]


def render_digest(path, max_chars):
    title, messages, _ = read_transcript(path)
    user_limit, asst_limit = 4000, 2500
    while True:
        parts = []
        for role, text, ts in messages:
            label = "Người dùng" if role == "user" else "Claude"
            parts.append("### %s %s\n%s" % (label, ts[:16].replace("T", " "),
                                            clip(text, user_limit if role == "user" else asst_limit)))
        body = "\n\n".join(parts)
        if len(body) <= max_chars or asst_limit <= 300:
            break
        asst_limit //= 2
        user_limit = max(1500, user_limit // 2)
    if len(body) > max_chars:
        body = clip(body, max_chars)
    header = "# Digest phiên: %s\n- transcript: %s\n- số lời người dùng: %d · số câu trả lời: %d\n" % (
        title or "(chưa đặt tên)", path, sum(1 for m in messages if m[0] == "user"),
        sum(1 for m in messages if m[0] == "assistant"))
    return header + "\n" + body


# ------------------------------------------------------------------- lệnh
def cmd_session_end(_args):
    data = read_stdin_json()
    sid, tpath = data.get("session_id", ""), data.get("transcript_path", "")
    if not sid or not tpath or not Path(tpath).is_file():
        log("session-end: bỏ qua, thiếu session_id/transcript (%s)" % sid)
        return 0
    title, messages, capture_session = read_transcript(tpath)
    prompts = [m for m in messages if m[0] == "user"]
    answer_chars = sum(len(m[1]) for m in messages if m[0] == "assistant")
    if capture_session:
        log("session-end: %s là phiên kb-capture, không đưa vào hàng đợi" % sid)
        return 0
    if not prompts or answer_chars < MIN_ASSISTANT_CHARS:
        log("session-end: %s quá ngắn (%d lời, %d ký tự trả lời), bỏ qua" % (sid, len(prompts), answer_chars))
        return 0
    first = " ".join(prompts[0][1].split())[:120]
    append_event({"event": "end", "session_id": sid, "transcript_path": str(tpath),
                  "cwd": data.get("cwd", ""), "reason": data.get("reason", ""),
                  "title": title, "first_prompt": first, "prompts": len(prompts)})
    log("session-end: đã thêm %s (%d lời)" % (sid, len(prompts)))
    return 0


def cmd_session_start(_args):
    data = read_stdin_json()
    current = data.get("session_id", "")
    events = read_events()
    state = sessions_state(events)
    pending = [e for sid, e in state.items() if e.get("status") == "pending" and sid != current
               and Path(e.get("transcript_path", "")).is_file()]
    if not pending:
        return 0
    last = None
    for e in events:
        if e.get("event") == "reminded":
            last = e
    if last and last.get("count") == len(pending):
        try:
            if now() - dt.datetime.fromisoformat(last["at"]) < REMIND_EVERY:
                return 0
        except (KeyError, ValueError):
            pass
    newest = max(pending, key=lambda e: e.get("at", ""))
    label = newest.get("title") or newest.get("first_prompt") or newest.get("session_id")
    context = ("[kb-capture] Còn %d phiên Claude Code đã kết thúc chưa được ghi vào kho tri thức kb-* "
               "(mới nhất: \"%s\", %s). Trong câu trả lời đầu tiên của phiên này, thêm MỘT dòng nhắc "
               "người dùng và đề nghị chạy /kb-capture queue. Không tự ghi vào kho khi người dùng chưa "
               "đồng ý; nếu người dùng từ chối thì không nhắc lại trong phiên này."
               % (len(pending), label[:80], newest.get("at", "")[:16].replace("T", " ")))
    append_event({"event": "reminded", "session_id": current or "-", "count": len(pending)})
    print(json.dumps({
        "systemMessage": "Kho tri thức: còn %d phiên chưa ghi — gõ /kb-capture queue để ghi." % len(pending),
        "hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context},
    }, ensure_ascii=True))
    return 0


def cmd_list(_args):
    pending = sorted((e for e in sessions_state().values() if e.get("status") == "pending"),
                     key=lambda e: e.get("at", ""))
    if not pending:
        print("Không có phiên nào đang chờ.")
        return 0
    for e in pending:
        exists = Path(e.get("transcript_path", "")).is_file()
        print("%s  %s  %2d lời  %s%s\n    cwd: %s" % (
            e["session_id"][:8], e.get("at", "")[:16].replace("T", " "), e.get("prompts", 0),
            (e.get("title") or e.get("first_prompt") or "")[:70],
            "" if exists else "  [MẤT transcript]", e.get("cwd", "")))
    print("Tổng: %d phiên đang chờ" % len(pending))
    return 0


def cmd_digest(args):
    path = find_transcript(args.ref)
    if path is None:
        print("Không tìm thấy transcript cho %r" % args.ref, file=sys.stderr)
        return 2
    print(render_digest(path, args.max_chars))
    return 0


def _mark(args, status):
    state = sessions_state()
    code = 0
    for ref in args.sessions:
        hits = [sid for sid in state if sid.startswith(ref)]
        if len(hits) != 1:
            print("Mã phiên %r: %d kết quả khớp (cần đúng 1)" % (ref, len(hits)), file=sys.stderr)
            code = 2
            continue
        append_event({"event": status, "session_id": hits[0], "note": args.note or ""})
        print("%s %s" % (status.upper(), hits[0]))
    return code


def cmd_scan(args):
    terms = []
    if BLOCKLIST.is_file():
        for line in BLOCKLIST.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                terms.append(line)
    if not terms:
        print("Blocklist trống hoặc chưa có: %s" % BLOCKLIST, file=sys.stderr)
    pattern = re.compile("|".join(re.escape(t) for t in terms), re.I) if terms else None
    hits = 0
    for name in args.files:
        path = Path(name)
        if not path.is_file():
            continue
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if pattern is not None and pattern.search(line):
                hits += 1
                print("%s:%d: chứa từ cấm: %s" % (name, n, pattern.search(line).group(0)))
    print("scan: %d file, %d vị trí vi phạm" % (len(args.files), hits))
    return 1 if hits else 0


def main(argv=None):
    setup_stdout()
    ap = argparse.ArgumentParser(description="Hàng đợi phiên Claude Code cho skill kb-capture")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("session-end")
    sub.add_parser("session-start")
    sub.add_parser("list")
    p = sub.add_parser("digest")
    p.add_argument("ref", help="mã phiên (hoặc tiền tố) hoặc đường dẫn transcript .jsonl")
    p.add_argument("--max-chars", type=int, default=60000)
    for name in ("done", "skip"):
        p = sub.add_parser(name)
        p.add_argument("sessions", nargs="+")
        p.add_argument("--note", default="")
    p = sub.add_parser("scan")
    p.add_argument("files", nargs="+")
    args = ap.parse_args(argv)
    handlers = {"session-end": cmd_session_end, "session-start": cmd_session_start, "list": cmd_list,
                "digest": cmd_digest, "done": lambda a: _mark(a, "done"), "skip": lambda a: _mark(a, "skip"),
                "scan": cmd_scan}
    if args.cmd not in handlers:
        ap.print_help()
        return 2
    if args.cmd in ("session-end", "session-start"):
        try:
            return handlers[args.cmd](args)
        except Exception:  # hook không bao giờ được làm hỏng phiên
            log("%s lỗi:\n%s" % (args.cmd, traceback.format_exc()))
            return 0
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
