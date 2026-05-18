"""Layer-by-layer diagnostics for Aftertone v2."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path

from aftertone.config import cfg_enabled, load_config, summary_mode
from aftertone.paths import config_path, install_root, state_dir


def _read_port(root: Path) -> int:
    port_file = state_dir(root) / "tts-daemon.port"
    if port_file.is_file():
        try:
            return int(port_file.read_text(encoding="utf-8").strip())
        except ValueError:
            pass
    cfg = load_config(root)
    try:
        return int(cfg.get("port", 8765))
    except (TypeError, ValueError):
        return 8765


def _daemon_health(port: int) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(
            f"http://127.0.0.1:{port}/healthz", timeout=0.5
        ) as resp:
            if resp.status == 200:
                return True, "ok"
            return False, f"status={resp.status}"
    except urllib.error.URLError as exc:
        return False, str(exc.reason if hasattr(exc, "reason") else exc)


def run_doctor(root: Path | None = None) -> int:
    issues: list[str] = []
    ok: list[str] = []

    try:
        r = install_root(root)
        ok.append(f"install_root={r}")
    except FileNotFoundError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        return 1

    cfg_path = config_path(r)
    if not cfg_path.is_file():
        issues.append(f"missing_config={cfg_path}")
    else:
        cfg = load_config(r)
        ok.append(f"enabled={cfg_enabled(cfg)}")
        ok.append(f"summary_mode={summary_mode(cfg)}")
        ok.append(f"lang={cfg.get('lang', 'en')}")

    hooks_json = Path.home() / ".cursor" / "hooks.json"
    if hooks_json.is_file():
        data = json.loads(hooks_json.read_text(encoding="utf-8-sig"))
        entries = (data.get("hooks") or {}).get("afterAgentResponse") or []
        has = any(
            isinstance(e, dict) and "aftertone-speak_summary" in (e.get("command") or "")
            for e in entries
        )
        if has:
            ok.append("global_hook=registered")
        else:
            issues.append("global_hook=missing_afterAgentResponse")
    else:
        issues.append(f"missing_hooks_json={hooks_json}")

    port = _read_port(r)
    healthy, detail = _daemon_health(port)
    if healthy:
        ok.append(f"daemon=up port={port}")
    else:
        issues.append(f"daemon=down port={port} ({detail})")

    hook_log = state_dir(r) / "speak_summary-hook.log"
    if hook_log.is_file():
        lines = hook_log.read_text(encoding="utf-8", errors="replace").strip().splitlines()
        ok.append(f"last_hook_log={lines[-1][:120] if lines else 'empty'}")
    else:
        issues.append("hook_log=never_run")

    result = {"ok": len(issues) == 0, "checks_ok": ok, "issues": issues}
    print(json.dumps(result, indent=2))
    return 0 if result["ok"] else 1
