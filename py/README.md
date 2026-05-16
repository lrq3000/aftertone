# Python (Cursor TTS daemon)

See the [repository README](../README.md) for setup. Quick refs:

```bash
cd py
uv sync
uv run python tts_daemon_ctl.py start --repo-root ..
```

Models: `bash ../scripts/bootstrap.sh` or `uv run --with huggingface_hub python fetch_assets.py` from `py/`.
