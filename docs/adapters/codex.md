# Codex adapter

Aftertone speaks after Codex turns via user-level **Stop** and **SubagentStop** lifecycle hooks in `~/.codex/hooks.json`.

## Install

Run the normal global install:

```bash
curl -fsSL https://raw.githubusercontent.com/omarelkhal/aftertone/main/scripts/install.sh | bash -s -- --install-uv --start-daemon
```

The installer copies `~/.cursor/hooks/aftertone-codex-speak-on-stop.sh` and merges Aftertone entries into `~/.codex/hooks.json`.

Codex requires hook trust review for non-managed hooks. In Codex, run `/hooks` if prompted and trust the Aftertone Stop hook.

## Payload

Codex sends one JSON object on stdin. Aftertone uses:

| Field | Role |
|-------|------|
| `hook_event_name` | `Stop` or `SubagentStop` |
| `last_assistant_message` | Preferred source for `<spoken_summary>` |
| `session_id` | Per-chat allowlist id |
| `transcript_path` | Fallback only |
| `model` | Helps identify Codex Stop payloads |

The wrapper delegates to the shared `.cursor/hooks/speak_summary.sh` pipeline. It never sends text to a cloud TTS service.

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
- Confirm `/hooks` shows the Aftertone Stop hook as trusted.
- If a tag is missing and `summary_mode = "tag_only"`, silence is expected.

## Status

Global Codex hooks ship with the Aftertone installer. Codex MCP can still be used for control tools, but post-reply speech uses lifecycle hooks.
