"""Build POST /say JSON from Cursor hook stdin (v2 entry)."""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime

from expression_tags import apply_expression

from aftertone.config import cfg_enabled, load_config, summary_mode
from aftertone.extract import hook_event_name, resolve_raw_text
from aftertone.hook_json import decode_hook_bytes, loads_hook_json
from aftertone.paths import install_root
from aftertone.summary import build_speakable_text
from aftertone.text_utils import cfg_float_bounded, cfg_int_bounded, in_quiet_hours


def prepare_payload(hook: dict, cfg: dict | None = None, root=None) -> dict | None:
    cfg = cfg if cfg is not None else load_config(root)
    if not cfg_enabled(cfg):
        return None

    quiet = str(cfg.get("quiet_hours", ""))
    if os.environ.get("SPEAK_SUMMARY_IGNORE_QUIET", "").strip() not in (
        "1",
        "true",
        "yes",
    ) and in_quiet_hours(datetime.now().astimezone(), quiet):
        return None

    min_chars = int(cfg.get("min_chars", 5))
    max_chars = int(cfg.get("max_chars", 2000))
    h_max = cfg_int_bounded(cfg, "heuristic_max_sentences", 2, 1, 3)
    h_code_max = cfg_int_bounded(cfg, "heuristic_max_sentences_code_heavy", 1, 1, 3)
    fence_thr = cfg_float_bounded(cfg, "heuristic_code_fence_fraction", 0.35, 0.05, 0.95)

    event = hook_event_name(hook)
    if event and event != "afterAgentResponse":
        return None

    raw_text = resolve_raw_text(hook, event)
    if not raw_text:
        return None

    mode = summary_mode(cfg)
    text, _source = build_speakable_text(
        raw_text,
        cfg,
        mode,
        min_chars=min_chars,
        max_chars=max_chars,
        h_max=h_max,
        h_code_max=h_code_max,
        fence_thr=fence_thr,
        apply_expression_fn=apply_expression,
    )
    if not text:
        return None

    return {
        "text": text,
        "generation_id": hook.get("generation_id"),
        "conversation_id": hook.get("conversation_id"),
        "totalStep": int(cfg.get("total_step", 8)),
        "speed": float(cfg.get("speed", 1.0)),
        "lang": str(cfg.get("lang", "en")),
        "mode": str(cfg.get("mode", "queue")).lower(),
    }


def main() -> None:
    raw_hook = decode_hook_bytes(sys.stdin.buffer.read())
    try:
        hook = loads_hook_json(raw_hook)
    except json.JSONDecodeError as exc:
        print(f"hook_json_invalid: {exc}", file=sys.stderr)
        print("{}")
        return

    try:
        root = install_root()
    except FileNotFoundError as exc:
        print(f"{exc}", file=sys.stderr)
        print("{}")
        return

    cfg = load_config(root)
    out = prepare_payload(hook, cfg, root)
    if out is None:
        print("{}")
        return
    print(json.dumps(out, ensure_ascii=False))
