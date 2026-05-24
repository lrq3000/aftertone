# OpenCode adapter

Aftertone speaks after OpenCode turns via a user-level OpenCode plugin under `~/.config/opencode/plugins/aftertone.js`.

## Install

Run the normal global install:

```bash
curl -fsSL https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.sh | bash -s -- --install-uv --start-daemon
```

The installer copies:

| Path | Purpose |
|------|---------|
| `~/.config/opencode/plugins/aftertone.js` | Listens for OpenCode post-turn events and calls Aftertone |
| `~/.config/opencode/rules/aftertone-spoken-summary.md` | Spoken-summary guidance for OpenCode sessions |
| `~/.config/opencode/aftertone-install-dir` | Install-root marker used by the plugin |

Restart OpenCode after installing so global plugins reload.

## How it works

The plugin tracks assistant message events containing `<spoken_summary>`, then on `session.idle` sends this normalized payload to the shared Aftertone hook pipeline:

```json
{
  "hook_event_name": "aftertone.response",
  "adapter": "opencode",
  "session_id": "...",
  "last_assistant_message": "<spoken_summary>...</spoken_summary>",
  "model": "..."
}
```

No speech logic lives in the plugin. The daemon, TOML config, quiet hours, per-session allowlist, and language settings are shared with Cursor, Claude Code, and Codex.

## Daily use

Use the shared CLI controls:

```bash
cd ~/aftertone
uv run --directory py python -m aftertone on
uv run --directory py python -m aftertone status
```

With the default `session_mode = "allowlist"`, run `aftertone on` and send one OpenCode reply in that session so the plugin can register the OpenCode session id.

## Troubleshooting

- Restart OpenCode after install or repair.
- Run `uv run --directory ~/aftertone/py python -m aftertone doctor`.
- Check `~/aftertone/.cursor/hooks/state/speak_summary-hook.log`.
- Confirm the final assistant message contains `<spoken_summary>` when `summary_mode = "tag_only"`.

## Status

Global OpenCode plugin support ships with the Aftertone installer. If OpenCode changes plugin event shapes, update only the thin plugin and keep the normalized payload contract stable.
