# `scripts/`

- **`bootstrap.sh`** — one-shot dev setup from the repo root: `uv sync` in `py/`, download `Supertone/supertonic-3` into `assets/` when ONNX files are missing (via `py/fetch_assets.py` + `huggingface_hub`), and `npm install` in `web/`. See the root [README](../README.md#getting-started) for env vars (`SKIP_ASSETS`, `SKIP_WEB`, `FORCE_ASSETS`).
