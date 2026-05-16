## Aftertone — agent map

- **Goal:** post-reply **local TTS** for coding agents (Cursor today; Claude & Codex adapters tracked in [CONTRIBUTING.md](CONTRIBUTING.md)).
- **`.cursor/hooks.json`** — Cursor adapter; must include `"version": 1`.
- **`.cursor/hooks/`** — `speak_summary.sh`, `speak_summary.toml`, `hook_payload_trace.sh`.
- **`py/`** — `tts_daemon.py`, `tts_daemon_ctl.py`, `speak_summary_prepare.py`, vendored `helper.py` (Supertonic), `tts_io.py`, `fetch_assets.py`, diagnostics.
- **`speak_summary.toml`** — `max_chars` caps text sent to TTS (default 2000). Use **`max_chars = 0`** for no cap on the chosen excerpt (long replies = long audio). Without `<spoken_summary>`, only a **first-sentence** fallback is spoken unless you use the tag for full control. Inside the tag, **write for speech**: expand “e.g.” / “etc.” into full words (see `.cursor/rules/spoken-summary.mdc`).
- **`scripts/bootstrap.sh`** — `uv sync` + HF snapshot if ONNX dir missing.

## Commands

- Bootstrap: `bash scripts/bootstrap.sh` from repo root.
- Daemon: `cd py && uv run python tts_daemon_ctl.py start --repo-root ..`
- `uv run` examples: `cd py` first, or `uv run --directory py …` from repo root.

## Env

- **`AFTERTONE_REPO`** — preferred repo root for hooks/daemon.
- **`SUPERTONIC_REPO`** — legacy alias (still set by shell hooks for older forks).

## Facts

- Assets: Hugging Face `Supertone/supertonic-3` via `fetch_assets.py` → `./assets/`.
- Cursor hooks are **per workspace** `.cursor/`. User-wide hooks live under `~/.cursor/` (different layout).
