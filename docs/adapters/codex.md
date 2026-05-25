# Codex adapter

Aftertone speaks after Codex turns via the **Aftertone Codex plugin**. The plugin bundles **Stop** and **SubagentStop** lifecycle hooks plus MCP control tools.

## Install

Run the normal global install:

```bash
curl -fsSL https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.sh | bash -s -- --install-uv --start-daemon
```

The installer registers the repo-local Aftertone marketplace in `~/.codex/config.toml` and enables `aftertone@aftertone`. Restart Codex if it was already open.

Codex still requires hook trust review for non-managed hooks. In Codex, run `/hooks` if prompted and trust the Aftertone Stop hook.

Legacy fallback for older Codex builds:

```bash
cd ~/aftertone/py
uv run python install_global_codex_hooks.py --install-dir ..
```

That path writes directly to `~/.codex/hooks.json`, but it is no longer the default.

## Payload

Codex sends one JSON object on stdin. Aftertone uses:

| Field | Role |
|-------|------|
| `hook_event_name` | `Stop` or `SubagentStop` |
| `last_assistant_message` | Preferred source for `<spoken_summary>` |
| `session_id` | Per-chat allowlist id |
| `transcript_path` | Fallback only |
| `model` | Helps identify Codex Stop payloads |

The plugin hook wrapper delegates to the shared `.cursor/hooks/speak_summary.sh` pipeline and forces the `codex` adapter bucket when needed. It never sends text to a cloud TTS service.

## Control

The plugin also exposes the shared Aftertone MCP control plane from `python -m aftertone.mcp_server`:

- `aftertone_status`
- `aftertone_on`
- `aftertone_off`
- `aftertone_restart`
- `aftertone_repair`
- `aftertone_set_lang`
- `aftertone_set_speed`
- `aftertone_set_mode`
- `aftertone_set_expression`
- `aftertone_set_voice`

## Daily use

Use the shared CLI controls:

```bash
cd ~/aftertone
uv run --directory py python -m aftertone on
uv run --directory py python -m aftertone status
```

With the default `session_mode = "allowlist"`, run `aftertone on` and send one Codex reply in that session so the Stop hook can register `session_id`.

## Troubleshooting

- Run `uv run --directory ~/aftertone/py python -m aftertone doctor`.
- Check `~/aftertone/.cursor/hooks/state/speak_summary-hook.log`.
- Restart Codex after install or update if the plugin was already loaded.
- Confirm `/hooks` shows the Aftertone Stop hook as trusted.
- If a tag is missing and `summary_mode = "tag_only"`, silence is expected.

## Status

The Aftertone installer now enables a Codex plugin that owns the post-reply lifecycle hooks. Direct `~/.codex/hooks.json` registration remains only as a compatibility fallback.
