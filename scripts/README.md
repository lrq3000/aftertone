# `scripts/`

- **`bootstrap.sh`** — from repo root: `uv sync` in `py/`, download `Supertone/supertonic-3` into `assets/` when ONNX files are missing, optional `npm install` in `web/` if that directory exists.

Env: `SKIP_ASSETS=1`, `SKIP_WEB=1`, `FORCE_ASSETS=1` — see [README](../README.md).
