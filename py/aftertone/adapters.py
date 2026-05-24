"""Normalize post-reply hook payloads from supported agent adapters.

Adapters are intentionally thin: each harness should provide a small JSON object with
the assistant text and a stable session identifier, then the shared Aftertone pipeline
handles filtering, summary extraction, daemon posting, and playback.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

AdapterName = Literal["cursor", "claude", "codex", "opencode", "generic"]

ADAPTERS: tuple[AdapterName, ...] = (
    "cursor",
    "claude",
    "codex",
    "opencode",
    "generic",
)

POST_REPLY_EVENTS = frozenset(
    {
        "afterAgentResponse",
        "Stop",
        "SubagentStop",
        "aftertone.response",
    }
)

_TEXT_KEYS = (
    "last_assistant_message",
    "output_text",
    "assistant_text",
    "text",
    "response",
    "message",
    "content",
)

_SESSION_KEYS = (
    "conversation_id",
    "conversationId",
    "session_id",
    "sessionId",
    "thread_id",
    "threadId",
)


def hook_event_name(hook: dict) -> str:
    return str(hook.get("hook_event_name") or hook.get("hookEventName") or "")


def adapter_name(hook: dict) -> AdapterName:
    """Return the normalized adapter name for a hook payload.

    Explicit `adapter` / `harness` metadata wins. Heuristics are only for legacy
    Cursor and Claude payloads, plus Codex Stop payloads that identify themselves
    through model/session fields but do not need an adapter field in Codex hooks.
    """

    raw = str(hook.get("adapter") or hook.get("harness") or "").strip().lower()
    if raw in ADAPTERS:
        return raw  # type: ignore[return-value]

    event = hook_event_name(hook)
    if event == "afterAgentResponse":
        return "cursor"

    transcript = str(hook.get("transcript_path") or "")
    transcript_norm = transcript.replace("\\", "/")
    if "/.claude/" in transcript_norm or transcript_norm.startswith("~/.claude"):
        return "claude"
    if "/.codex/" in transcript_norm or transcript_norm.startswith("~/.codex"):
        return "codex"

    if event in ("Stop", "SubagentStop"):
        # Claude and Codex share Stop-style fields. Claude's installed wrapper now
        # adds `adapter`, while older Claude installs still resolve correctly via
        # transcript_path. Codex Stop payloads include OpenAI model names, so keep
        # legacy no-model Stop hooks in the Claude bucket for per-chat allowlists.
        model = str(hook.get("model") or "").strip().lower()
        if model.startswith("gpt") or "codex" in model or "openai" in model:
            return "codex"
        return "claude"

    return "generic"


def assistant_text(hook: dict) -> str:
    for key in _TEXT_KEYS:
        value = hook.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def session_id(hook: dict, adapter: AdapterName | None = None) -> str | None:
    for key in _SESSION_KEYS:
        value = hook.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()

    transcript = hook.get("transcript_path")
    if isinstance(transcript, str) and transcript.strip():
        return f"transcript:{transcript.strip()}"

    cwd = hook.get("cwd") or hook.get("workspace_path") or hook.get("workspacePath")
    if isinstance(cwd, str) and cwd.strip():
        return f"cwd:{cwd.strip()}"

    return None


def transcript_path(hook: dict) -> str:
    value = hook.get("transcript_path") or os.environ.get("CURSOR_TRANSCRIPT_PATH")
    return value if isinstance(value, str) else ""
