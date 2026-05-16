#!/usr/bin/env python3
"""
Build JSON payload for POST /say from agent / IDE hook stdin.

Handles:
- afterAgentResponse (Cursor and compatible hooks): uses inline `text` when
  hook_event_name is afterAgentResponse (avoids transcript_path, which stop often lacks).
- Other events: reads transcript jsonl from transcript_path when present.

Emits one line JSON for /say or {} if nothing to speak.
"""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, time as dtime
from pathlib import Path

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib  # type: ignore[import-not-found,no-redef]


def _load_toml(path: Path) -> dict:
    if not path.is_file():
        return {}
    with path.open("rb") as f:
        return tomllib.load(f)


def _parse_hhmm(s: str) -> dtime | None:
    s = s.strip()
    m = re.match(r"^(\d{1,2}):(\d{2})$", s)
    if not m:
        return None
    h, mi = int(m.group(1)), int(m.group(2))
    if h > 23 or mi > 59:
        return None
    return dtime(h, mi)


def _in_quiet_hours(now_local: datetime, spec: str) -> bool:
    spec = (spec or "").strip()
    if not spec or spec.lower() in ("none", "off", "false"):
        return False
    m = re.match(r"^(\d{1,2}:\d{2})\s*-\s*(\d{1,2}:\d{2})$", spec)
    if not m:
        return False
    a = _parse_hhmm(m.group(1))
    b = _parse_hhmm(m.group(2))
    if a is None or b is None:
        return False
    t = now_local.time().replace(tzinfo=None)
    if a <= b:
        return a <= t < b
    # overnight window e.g. 22:00-08:00
    return t >= a or t < b


def _assistant_text_blocks(lines: list[str]) -> str:
    last_assistant: dict | None = None
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if obj.get("role") != "assistant":
            continue
        last_assistant = obj
    if not last_assistant:
        return ""
    if isinstance(last_assistant.get("content"), str):
        return str(last_assistant["content"]).strip()
    msg = last_assistant.get("message")
    if isinstance(msg, str):
        return msg.strip()
    if not isinstance(msg, dict):
        return ""
    parts = msg.get("content")
    if isinstance(parts, str):
        return parts.strip()
    if not isinstance(parts, list):
        return ""
    texts: list[str] = []
    for p in parts:
        if isinstance(p, dict) and p.get("type") == "text":
            t = p.get("text")
            if isinstance(t, str) and t.strip():
                texts.append(t.strip())
    return "\n".join(texts)


def _extract_spoken_summary(raw: str) -> str | None:
    m = re.search(
        r"<spoken_summary>\s*(.*?)\s*</spoken_summary>",
        raw,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if not m:
        return None
    inner = m.group(1).strip()
    return inner if inner else None


def _without_spoken_block(raw: str) -> str:
    """Remove tag block so markdown heuristics do not mangle `spoken_summary` underscores."""
    return re.sub(
        r"<spoken_summary>\s*[\s\S]*?\s*</spoken_summary>",
        " ",
        raw,
        flags=re.DOTALL | re.IGNORECASE,
    ).strip()


def _demote_code_fences(raw: str) -> str:
    """Replace fenced blocks so markdown stripping does not erase the whole reply."""
    return re.sub(r"```[\s\S]*?```", " code example ", raw)


def _strip_markdownish(s: str) -> str:
    s = re.sub(r"```[\s\S]*?```", " ", s)
    s = re.sub(r"`[^`]+`", " ", s)
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", s)
    s = re.sub(r"[#*_~>`]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _first_sentence(s: str) -> str:
    s = _strip_markdownish(s)
    if not s:
        return ""
    # Split on sentence end; keep first chunk reasonable
    for sep in (". ", "! ", "? ", "\n"):
        if sep in s:
            s = s.split(sep)[0].strip()
            if sep != "\n" and s:
                s += "."
            break
    return s


def _plain_excerpt(raw: str, max_chars: int) -> str:
    """Last-resort speakable string: stripped markdown on demoted code + no spoken block."""
    s = _strip_markdownish(_demote_code_fences(_without_spoken_block(raw)))
    return _clamp(s, max_chars) if s else ""


def _clamp(s: str, max_chars: int) -> str:
    """Trim speakable text. max_chars <= 0 means no limit (full string)."""
    s = s.strip()
    if max_chars <= 0 or len(s) <= max_chars:
        return s
    return s[: max_chars - 3].rsplit(" ", 1)[0] + "..."


def _cfg_enabled(cfg: dict) -> bool:
    v = cfg.get("enabled", True)
    if isinstance(v, str):
        return v.strip().lower() not in ("0", "false", "no", "off")
    return bool(v)


def main() -> None:
    raw_hook = sys.stdin.read()
    try:
        hook = json.loads(raw_hook) if raw_hook.strip() else {}
    except json.JSONDecodeError:
        print("{}")
        return

    repo = Path(
        os.environ.get("AFTERTONE_REPO", "").strip()
        or os.environ.get("SUPERTONIC_REPO", "").strip()
        or Path(__file__).resolve().parent.parent
    ).resolve()
    cfg_path = repo / ".cursor" / "hooks" / "speak_summary.toml"
    cfg = _load_toml(cfg_path)
    if not _cfg_enabled(cfg):
        print("{}")
        return

    quiet = str(cfg.get("quiet_hours", ""))
    if os.environ.get("SPEAK_SUMMARY_IGNORE_QUIET", "").strip() not in (
        "1",
        "true",
        "yes",
    ) and _in_quiet_hours(datetime.now().astimezone(), quiet):
        print("{}")
        return

    min_chars = int(cfg.get("min_chars", 5))
    max_chars = int(cfg.get("max_chars", 2000))

    # Prefer afterAgentResponse: Cursor sends final assistant text here. The `stop` hook
    # often has no transcript_path or an empty payload; afterAgentThought also has `text`
    # (thinking) — do not use that for TTS.
    event = str(
        hook.get("hook_event_name")
        or hook.get("hookEventName")
        or ""
    )
    inline = hook.get("text")
    if event == "afterAgentResponse" and isinstance(inline, str) and inline.strip():
        raw_text = inline.strip()
    else:
        transcript = hook.get("transcript_path") or os.environ.get(
            "CURSOR_TRANSCRIPT_PATH"
        )
        if not transcript or not os.path.isfile(transcript):
            print("{}")
            return
        with open(transcript, encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        raw_text = _assistant_text_blocks(lines)
        if not raw_text:
            print("{}")
            return

    spoken = _extract_spoken_summary(raw_text)
    base = _without_spoken_block(raw_text)

    if spoken:
        text = _clamp(spoken, max_chars)
    else:
        text = _clamp(_first_sentence(base), max_chars)
        if len(text) < min_chars:
            text = _clamp(_first_sentence(_demote_code_fences(base)), max_chars)
        if len(text) < min_chars:
            text = _plain_excerpt(raw_text, max_chars)

    if not text.strip():
        print("{}")
        return
    if not spoken and len(text) < min_chars:
        print("{}")
        return

    out = {
        "text": text,
        "generation_id": hook.get("generation_id"),
        "conversation_id": hook.get("conversation_id"),
        "totalStep": int(cfg.get("total_step", 4)),
        "speed": float(cfg.get("speed", 1.05)),
        "mode": str(cfg.get("mode", "queue")).lower(),
    }
    print(json.dumps(out, ensure_ascii=False))


if __name__ == "__main__":
    main()
