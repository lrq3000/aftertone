# OpenCode And Codex Adapters Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add installer-managed global OpenCode and Codex post-reply TTS support, plus a generic adapter template for future harnesses.

**Architecture:** Keep adapters thin. Each harness emits a normalized post-reply JSON payload into the existing `speak_summary.sh` -> `aftertone.hook_run` -> daemon pipeline. Core code in `aftertone.adapters` identifies adapter/session/text fields while the daemon, config, summary extraction, and CLI remain shared.

**Tech Stack:** Python 3.13, pytest, Bash/PowerShell wrappers, Codex lifecycle hooks, OpenCode JavaScript plugin hooks, static docs.

---

### Task 1: Generic Adapter Normalization

**Files:**
- Create: `py/aftertone/adapters.py`
- Modify: `py/aftertone/extract.py`
- Modify: `py/aftertone/sessions.py`
- Test: `py/tests/test_aftertone_adapters.py`

- [ ] Add tests for explicit `adapter`, Codex `Stop`, OpenCode normalized payloads, and generic fallback.
- [ ] Run `uv run pytest tests/test_aftertone_adapters.py -q` from `py/` and confirm the new tests fail because `aftertone.adapters` does not exist.
- [ ] Implement `aftertone.adapters` with `adapter_name()`, `session_id()`, and `assistant_text()` helpers.
- [ ] Delegate existing extraction/session code to these helpers with no behavioral regression for Cursor/Claude.
- [ ] Re-run the focused tests and existing `test_aftertone_v2.py`.

### Task 2: Codex Global Adapter

**Files:**
- Create: `scripts/codex-global/hooks.json`
- Create: `scripts/codex-global/aftertone-codex-speak-on-stop.sh`
- Create: `py/install_global_codex_hooks.py`
- Modify: `py/install_global_hooks.py`
- Modify: `py/uninstall_global_hooks.py`
- Test: `py/tests/test_install_global_codex_hooks.py`

- [ ] Add tests for merging `~/.codex/hooks.json`, copying the wrapper into `~/.cursor/hooks/`, preserving unrelated hooks, and uninstall cleanup.
- [ ] Run the focused tests and confirm they fail before implementation.
- [ ] Implement Codex installer with `Stop` and `SubagentStop` hooks that call `bash ~/.cursor/hooks/aftertone-codex-speak-on-stop.sh`.
- [ ] Implement uninstall removal using command marker matching without deleting unrelated Codex settings.
- [ ] Wire Codex install into the global install orchestrator and repair path.

### Task 3: OpenCode Global Adapter

**Files:**
- Create: `scripts/opencode-global/aftertone-plugin.js`
- Create: `scripts/opencode-global/spoken-summary.md`
- Create: `py/install_global_opencode_hooks.py`
- Modify: `py/install_global_hooks.py`
- Modify: `py/uninstall_global_hooks.py`
- Test: `py/tests/test_install_global_opencode_hooks.py`

- [ ] Add tests for copying a global plugin/rule into `~/.config/opencode/`, preserving existing config, and uninstall cleanup.
- [ ] Run the focused tests and confirm they fail before implementation.
- [ ] Implement an OpenCode plugin that listens for post-turn idle/message events, creates a normalized payload with `adapter = "opencode"`, and invokes `python -m aftertone.hook_run --stdin` through the install root.
- [ ] Keep plugin output quiet and non-blocking; log failures under Aftertone state only.
- [ ] Wire OpenCode install into the global install orchestrator and repair path.

### Task 4: Docs And Generic Template

**Files:**
- Create: `docs/adapters/codex.md`
- Create: `docs/adapters/opencode.md`
- Create: `docs/adapters/generic.md`
- Modify: `README.md`
- Modify: `CONTRIBUTING.md`
- Modify: `docs/docs.html`
- Modify: `docs/index.html`
- Modify: `docs/README.md`
- Test: `py/tests/test_aftertone_v2.py` if doc-linked constants or rules change; otherwise run grep checks for new doc links.

- [ ] Document Codex global install, `/hooks` trust review, `Stop` payload, and troubleshooting.
- [ ] Document OpenCode global plugin install, restart requirement, and troubleshooting.
- [ ] Document the generic normalized adapter payload, event timing requirements, stdout rules, installer checklist, uninstall checklist, and contribution acceptance criteria.
- [ ] Update public adapter tables to list only Cursor, Claude Code, Codex, and OpenCode.

### Task 5: Verification

**Files:**
- All touched code and docs.

- [ ] Run `uv run pytest` from `py/`.
- [ ] Run targeted installer tests again if full suite fails for environment-only reasons.
- [ ] Run `git diff --check`.
- [ ] Summarize implemented adapters, commands run, and any unverified runtime behavior.

---

## Self-Review

- Spec coverage: installer-managed Codex/OpenCode support, `aftertone.adapters`, generic template docs, and contribution guidance are covered.
- Placeholder scan: no task relies on undefined “later” work; OpenCode event names will be implemented against documented OpenCode plugin event APIs.
- Type consistency: normalized adapter names are lowercase strings: `cursor`, `claude`, `codex`, `opencode`, `generic`.
