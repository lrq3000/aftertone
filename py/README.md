# Aftertone — Python

Inference stack + HTTP daemon for **Aftertone** (see [repository README](../README.md)).

```bash
cd py
uv sync
uv run python tts_daemon_ctl.py start --repo-root ..
```

Models: `bash ../scripts/bootstrap.sh` or `uv run --with huggingface_hub python fetch_assets.py`.
