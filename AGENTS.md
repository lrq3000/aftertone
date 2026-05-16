## Project map

- **`.cursor/hooks.json`** — register `afterAgentResponse` + optional `stop` trace; must include `"version": 1`.
- **`.cursor/hooks/`** — `speak_summary.sh`, `speak_summary.toml`, `hook_payload_trace.sh`.
- **`py/`** — `tts_daemon.py`, `tts_daemon_ctl.py`, `speak_summary_prepare.py`, vendored `helper.py` (Supertonic), `tts_io.py`, `fetch_assets.py`, diagnostics scripts.
- **`scripts/bootstrap.sh`** — one-shot `uv sync` + HF assets if missing.

## Commands

- Bootstrap: `bash scripts/bootstrap.sh` from repo root.
- Python: `cd py && uv run python tts_daemon_ctl.py start --repo-root ..` (PID/port under `.cursor/hooks/state/`).
- When giving `uv run` examples, use `cd py` first or `uv run --directory py …` from repo root.

## Learned facts

- Model assets: Hugging Face `Supertone/supertonic-3`; `fetch_assets.py` snapshots into `./assets/`.
- Hooks are **per workspace** (this repo’s `.cursor/`). For global behavior see Cursor user hooks under `~/.cursor/` (different path rules).
