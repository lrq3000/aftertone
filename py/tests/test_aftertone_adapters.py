"""Generic adapter normalization tests for post-reply harness payloads."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aftertone.adapters import adapter_name, assistant_text, session_id
from aftertone.extract import resolve_raw_text
from aftertone.prepare import prepare_payload
from aftertone.sessions import load_sessions, save_sessions


def _tag(text: str) -> str:
    return f"<spoken_summary>{text}</spoken_summary>"


def test_explicit_adapter_field_wins_over_event_heuristics() -> None:
    hook = {
        "hook_event_name": "Stop",
        "adapter": "opencode",
        "session_id": "sess-opencode",
        "last_assistant_message": _tag("OpenCode spoke through a normalized Stop payload!!"),
    }

    assert adapter_name(hook) == "opencode"
    assert session_id(hook) == "sess-opencode"
    assert "OpenCode spoke" in assistant_text(hook)


def test_codex_stop_payload_resolves_last_assistant_message() -> None:
    hook = {
        "hook_event_name": "Stop",
        "model": "gpt-5.5",
        "session_id": "codex-session-1",
        "last_assistant_message": _tag("Codex Stop hooks now feed Aftertone!!"),
    }

    assert adapter_name(hook) == "codex"
    assert resolve_raw_text(hook, "Stop") == hook["last_assistant_message"]


def test_legacy_claude_stop_without_model_stays_claude() -> None:
    hook = {
        "hook_event_name": "Stop",
        "session_id": "claude-session-1",
        "last_assistant_message": _tag("Legacy Claude Stop hooks still use the Claude session bucket!!"),
    }

    assert adapter_name(hook) == "claude"


def test_opencode_normalized_payload_accepts_output_text_alias() -> None:
    hook = {
        "hook_event_name": "aftertone.response",
        "adapter": "opencode",
        "sessionId": "opencode-session-1",
        "output_text": _tag("OpenCode plugins can emit the generic adapter payload!!"),
    }

    assert adapter_name(hook) == "opencode"
    assert session_id(hook) == "opencode-session-1"
    assert "generic adapter" in resolve_raw_text(hook, "aftertone.response")


def test_generic_payload_prepares_speech_and_preserves_generation_metadata() -> None:
    hook = {
        "hook_event_name": "aftertone.response",
        "adapter": "generic",
        "session_id": "generic-session-1",
        "generation_id": "turn-123",
        "conversation_id": "conv-123",
        "text": _tag("Generic harness adapters only need one normalized JSON object!!"),
    }
    cfg = {
        "enabled": True,
        "session_mode": "all",
        "summary_mode": "tag_only",
        "only_speak_spoken_summary": True,
        "min_chars": 5,
        "max_chars": 2000,
        "spoken_summary_max_chars": 360,
        "expression_mode": "off",
    }

    out = prepare_payload(hook, cfg)

    assert out is not None
    assert "Generic harness" in out["text"]
    assert out["generation_id"] == "turn-123"
    assert out["conversation_id"] == "conv-123"


def test_generic_payload_auto_mode_can_use_inline_text_without_tag() -> None:
    hook = {
        "hook_event_name": "aftertone.response",
        "adapter": "generic",
        "session_id": "generic-session-2",
        "text": "The generic adapter finished the task and tests passed.",
    }
    cfg = {
        "enabled": True,
        "session_mode": "all",
        "summary_mode": "auto",
        "min_chars": 5,
        "max_chars": 2000,
        "heuristic_max_sentences": 2,
        "heuristic_max_sentences_code_heavy": 1,
        "heuristic_code_fence_fraction": 0.35,
        "expression_mode": "off",
    }

    out = prepare_payload(hook, cfg)

    assert out is not None
    assert "generic adapter" in out["text"]


def test_allowlist_sessions_are_bucketed_by_new_adapter_names(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    hooks = repo / ".cursor" / "hooks"
    hooks.mkdir(parents=True)
    (hooks / "speak_summary.toml").write_text(
        'enabled = true\nsession_mode = "allowlist"\n', encoding="utf-8"
    )
    save_sessions(repo, {"opencode": ["opencode-session-1"]})

    cfg = {
        "enabled": True,
        "session_mode": "allowlist",
        "summary_mode": "tag_only",
        "only_speak_spoken_summary": True,
        "min_chars": 5,
        "max_chars": 2000,
        "spoken_summary_max_chars": 360,
        "expression_mode": "off",
    }
    hook = {
        "hook_event_name": "aftertone.response",
        "adapter": "opencode",
        "session_id": "blocked-session",
        "last_assistant_message": _tag("This should stay muted!!"),
    }

    assert prepare_payload(hook, cfg, repo) is None

    hook["session_id"] = "opencode-session-1"
    out = prepare_payload(hook, cfg, repo)
    assert out is not None
    assert "stay muted" in out["text"]
    assert load_sessions(repo)["opencode"] == ["opencode-session-1"]
