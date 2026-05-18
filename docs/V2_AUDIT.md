# Aftertone v1 → v2 audit

## Keep (reuse in v2)

| Component | Path | Role in v2 |
|-----------|------|------------|
| Daemon + ONNX | `py/tts_daemon.py`, `py/helper.py`, `py/tts_io.py` | Long-running TTS; unchanged core |
| Daemon control | `py/tts_daemon_ctl.py` | Start/stop/restart; called from CLI |
| Global hooks install | `py/install_global_hooks.py` | Register `~/.cursor/hooks.json` |
| Hook shell | `.cursor/hooks/speak_summary.sh` | Thin stdin → prepare → POST |
| Hook JSON fixes | `py/hook_stdin_normalize.py` | Windows UTF-16 / path escapes → `aftertone.hook_json` |
| Path resolution | `py/aftertone_paths.py` | Install root → `aftertone.paths` |
| Voice presets | `py/voice_presets.py` | CLI / config |
| Assets fetch | `py/fetch_assets.py` | Bootstrap |
| Expression tags | `py/expression_tags.py` | Optional prosody |

## Replace or wrap

| Component | Issue | v2 change |
|-----------|-------|-----------|
| `speak_summary_prepare.py` | Monolith; tag-only default caused silence | `aftertone.prepare` + `summary_mode=auto` default |
| Slash commands | Bash/`$HOME` chains fail on Windows | `aftertone` CLI (`uv run aftertone on`) |
| `only_speak_spoken_summary` | Confusing name | `summary_mode`: `auto` \| `tag_only` \| `heuristic` |
| `aftertone-root.sh` in commands | Agent runs shell gymnastics | CLI resolves install dir internally |
| Diagnostics | Scattered logs | `aftertone doctor` with layer-by-layer verdict |
| MCP | Not present | Optional `aftertone.mcp_server` for control only |

## Do not use as primary speech path

- User rules alone (model may skip `<spoken_summary>`)
- MCP tools alone (agent may not call them)
- `/aftertone-on` without hook + daemon running

## v2 guarantee

Hook + daemon + `summary_mode=auto` → speak after every substantive reply without requiring model tags.
