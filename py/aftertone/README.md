# Aftertone v2 runtime

Modular package for post-reply TTS. The hook calls `aftertone.prepare`; control plane is `python -m aftertone`.

| Module | Role |
|--------|------|
| `config.py` | TOML load, `summary_mode` (`tag_only` default / `auto` / `heuristic`) |
| `defaults.py` | Install defaults: `tag_only`, `total_step = 8`, full tag (`spoken_summary_max_sentences = 0`) |
| `hook_json.py` | UTF-16 stdin, Windows JSON path escapes |
| `adapters.py` | Normalize Cursor, Claude, Codex, OpenCode, and generic post-reply payloads |
| `extract.py` | Hook + transcript text resolution |
| `summary.py` | Tag vs auto-extract router |
| `prepare.py` | Build `/say` JSON from hook stdin |
| `sessions.py` | Per-chat allowlist (`enabled_sessions.json`, pending on/off) |
| `cli.py` | Cross-platform `aftertone` commands |
| `doctor.py` | Install / hook / daemon diagnostics |
| `mcp_server.py` | Optional MCP control tools (not the speech trigger); used by the Codex plugin and available for other adapters |

Audit notes: [`docs/V2_AUDIT.md`](../../docs/V2_AUDIT.md).
