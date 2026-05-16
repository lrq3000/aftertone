# cursor-supertonic-tts

**Cursor IDE hooks** that speak a short summary after each agent reply, using **on-device [Supertonic](https://github.com/supertone-inc/supertonic) ONNX** inference via a tiny **local HTTP daemon** (models stay loaded; the hook stays fast).

## Features

- `afterAgentResponse` → optional TTS from inline reply text (prefers `<spoken_summary>…</spoken_summary>`).
- `speak_summary_prepare.py` builds the `/say` JSON; `tts_daemon.py` serves `POST /say` on localhost.
- Optional `stop` hook payload trace for debugging.
- `bash scripts/bootstrap.sh` — `uv sync`, Hugging Face asset download if needed, optional `web/` npm (disabled here by default: no `web/package.json` in this repo).

## Requirements

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [Cursor](https://cursor.com/) with **Hooks** enabled and a **trusted** workspace
- ONNX assets under `./assets` (from `Supertone/supertonic-3` — see bootstrap)

## Quick start

```bash
git clone https://github.com/YOUR_USER/cursor-supertonic-tts.git
cd cursor-supertonic-tts
bash scripts/bootstrap.sh
```

Then open **this folder** as the Cursor workspace root so `.cursor/hooks.json` loads.

- **Control daemon:** `cd py && uv run python tts_daemon_ctl.py status --repo-root ..`
- **Smoke test (needs assets + working audio):** `bash py/test_speak_summary_pipeline.sh`
- **Diagnostics:** `bash py/diagnose_speak_hooks.sh`

### Use in another project (copy-in)

Copy into your app repo:

- `.cursor/` (hooks + rules + keep `hooks.json` **`"version": 1`**)
- `py/` (this Python tree, or symlink it)

Set paths in `speak_summary.toml` (`onnx_dir`, `voice_style`) relative to `py/` as today (`../assets/onnx`, etc.). Set `SUPERTONIC_REPO` is inferred from the hook script walk to the tree that contains `py/speak_summary_prepare.py`.

## Configuration

| File | Role |
|------|------|
| `.cursor/hooks/speak_summary.toml` | Port, `quiet_hours`, `min_chars` / `max_chars`, GPU flag |
| `.cursor/rules/spoken-summary.mdc` | Agent rule: when/how to emit `<spoken_summary>` |

Disable TTS: `enabled = false` in `speak_summary.toml`.

## License

MIT — see [LICENSE](LICENSE). ONNX helper code attribution: [NOTICE](NOTICE).

## Publish to GitHub

This tree can live anywhere; if you already have a local copy with `git` history, add a remote and push:

```bash
cd /path/to/cursor-supertonic-tts
git remote add origin https://github.com/YOUR_USER/cursor-supertonic-tts.git
git push -u origin main
```

Create the empty repository on GitHub first (no README/license there to avoid conflicts), **or** install the [GitHub CLI](https://cli.github.com/) and run:

```bash
gh repo create cursor-supertonic-tts --public --source=. --remote=origin --push
```
