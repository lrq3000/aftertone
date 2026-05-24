# Generic adapter template

Use this template when adding Aftertone support for another agentic harness.

## Design rule

Keep the adapter thin. The harness integration should only capture final assistant text and session metadata, then send one normalized JSON payload to the existing Aftertone pipeline.

Do not duplicate TTS, summary extraction, TOML parsing, daemon control, quiet hours, or per-session filtering in the adapter.

## Normalized payload

Send this JSON on stdin to `.cursor/hooks/speak_summary.sh` or to `python -m aftertone.hook_run --stdin` with `AFTERTONE_INSTALL_DIR` set:

```json
{
  "hook_event_name": "aftertone.response",
  "adapter": "generic",
  "session_id": "stable-chat-or-thread-id",
  "last_assistant_message": "Full final assistant text, ideally ending with <spoken_summary>...</spoken_summary>",
  "generation_id": "optional-turn-id",
  "conversation_id": "optional-conversation-id",
  "model": "optional-model-name"
}
```

Supported `adapter` values are `cursor`, `claude`, `codex`, `opencode`, and `generic`. New adapters can start as `generic`; add a concrete adapter name only when per-session buckets or diagnostics need to distinguish it.

## Required hook timing

Run after the assistant turn is complete and the final assistant text is available. Avoid pre-response, token-stream, or tool-completion hooks unless the harness has no post-reply lifecycle event.

## Text fields

Aftertone checks these fields in order:

1. `last_assistant_message`
2. `output_text`
3. `assistant_text`
4. `text`
5. `response`
6. `message`
7. `content`

Prefer `last_assistant_message` for Stop-style hooks and `output_text` for plugin-style hooks.

## Session fields

Aftertone checks these fields in order:

1. `conversation_id`
2. `conversationId`
3. `session_id`
4. `sessionId`
5. `thread_id`
6. `threadId`
7. `transcript_path`
8. `cwd` / `workspace_path`

Use a stable chat/thread id so `/aftertone-on` can enable one session without enabling every workspace.

## Installer checklist

- Copy adapter scripts into a user-level harness config directory.
- Write or reuse `~/.cursor/hooks/aftertone-install-dir` or an adapter-specific install marker.
- Merge config instead of replacing user files.
- Remove old Aftertone entries before adding new ones so OS/path changes do not stack duplicates.
- Keep unrelated user hooks, commands, plugins, and settings intact.
- Add uninstall support that removes only Aftertone files and entries.

## Contribution checklist

- Add tests for install, merge, and uninstall behavior.
- Add one payload test in `py/tests/test_aftertone_adapters.py` if a new adapter name is added.
- Document hook trust or restart steps in `docs/adapters/<name>.md`.
- Run `python -m pytest` from `py/` before claiming support.
