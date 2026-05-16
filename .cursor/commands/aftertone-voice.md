---
name: aftertone-voice
description: Pick an Aftertone voice preset, apply it, and restart the TTS daemon
---

## Speed rule (required)

**Do not** plan, explain, or run shell before the user picks a voice.

Your **first** tool call must be **AskQuestion** (unless the user already named a preset or display name, e.g. `/aftertone-voice F4`, `/aftertone-voice Confident`, `M2`).

## Picker (first tool call)

One question, `allow_multiple: false`. Use these options (`id` = TOML preset, `label` = friendly name):

| id | label |
|----|-------|
| F1 | Calm (F1) |
| F2 | Cheerful (F2) |
| F3 | Announcer (F3) |
| F4 | Confident (F4) |
| F5 | Soothing (F5) |
| M1 | Upbeat (M1) |
| M2 | Deep calm (M2) |
| M3 | Authoritative (M3) |
| M4 | Gentle (M4) |
| M5 | Warm (M5) |

Prompt example: `Choose a voice (daemon restarts after apply).`

(Optional check: `uv run --directory py python speak_summary_config.py voice-picker` prints the same `id|label` lines.)

## Apply (only after the user picks)

From **repository root** (`PRESET` = chosen **id**, e.g. `F4`, not the display name):

```bash
uv run --directory py python speak_summary_config.py set voice PRESET --restart --ensure
```

Report stdout briefly. Do not hand-edit TOML.
