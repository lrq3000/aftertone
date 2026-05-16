#!/usr/bin/env python3
"""
Append one JSONL line describing the hook JSON Cursor sent on stdin.

Usage: printf '%s' "$HOOK_JSON" | python hook_payload_trace.py /path/to/hook_payload_trace.jsonl

Does not log full `text` (privacy); only length and whether inline TTS would trigger.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    if len(sys.argv) < 2:
        print("usage: hook_payload_trace.py <jsonl_path>", file=sys.stderr)
        sys.exit(2)
    path = Path(sys.argv[1])
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = sys.stdin.read()
    obj: dict = {}
    try:
        obj = json.loads(raw) if raw.strip() else {}
    except json.JSONDecodeError:
        obj = {"_parse_error": True}

    text = obj.get("text")
    text_len = len(text) if isinstance(text, str) else 0
    ev = str(obj.get("hook_event_name") or obj.get("hookEventName") or "")
    inline_ok = ev == "afterAgentResponse" and text_len > 0

    line = {
        "ts": datetime.now(timezone.utc).isoformat(),
        "stdin_bytes": len(raw.encode("utf-8")) if raw else 0,
        "hook_event_name": ev,
        "text_len": text_len,
        "inline_after_response_ok": inline_ok,
        "has_transcript_path": bool(obj.get("transcript_path")),
        "generation_id": obj.get("generation_id") or obj.get("generationId"),
        "status": obj.get("status"),
        "top_keys": sorted(obj.keys())[:30],
    }
    cproj = os.environ.get("CURSOR_PROJECT_DIR", "").strip()
    if cproj:
        line["cursor_project_dir"] = cproj
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
