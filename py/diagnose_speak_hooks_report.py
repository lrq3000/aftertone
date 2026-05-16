"""Verdict for hook_payload_trace.jsonl — invoked by diagnose_speak_hooks.sh (DIAG_REPO env)."""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def main() -> None:
    repo = Path(os.environ.get("DIAG_REPO", ".")).resolve()
    trace = repo / ".cursor" / "hooks" / "state" / "hook_payload_trace.jsonl"
    hook_log = repo / ".cursor" / "hooks" / "state" / "speak_summary-hook.log"

    print("")
    print("=== verdict (latest trace line) ===")
    if not trace.is_file():
        print("No hook_payload_trace.jsonl — hooks have not run yet (or wrong repo path).")
        return

    lines = [ln for ln in trace.read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not lines:
        print("Trace file is empty.")
        return

    last = json.loads(lines[-1])
    ts_s = str(last.get("ts") or "")
    gen = last.get("generation_id")
    ev = last.get("hook_event_name")
    try:
        ts = datetime.fromisoformat(ts_s.replace("Z", "+00:00"))
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        age = datetime.now(timezone.utc) - ts
        age_s = int(age.total_seconds())
    except (TypeError, ValueError):
        age_s = -1

    print(f"Newest trace ts: {ts_s}  (~{age_s}s ago)" if age_s >= 0 else f"Newest trace ts: {ts_s}")
    print(f"Newest line: hook_event_name={ev!r} generation_id={gen!r}")

    if gen == "pipeline-test" or gen == "stop-trace-test":
        print("")
        print("NOTE: This looks like the automated test (pipeline-test / stop-trace-test),")
        print("      NOT a live Cursor agent session. Run an Agent reply in Cursor, then")
        print("      run this script again — you should see a new generation_id.")

    if age_s >= 0 and age_s > 600 and gen not in ("pipeline-test", "stop-trace-test"):
        print("")
        print("NOTE: Newest trace is over 10 minutes old. If you just used the agent,")
        print("      project hooks may not be running (trust workspace, reload window,")
        print("      or open the folder that contains .cursor/hooks.json).")

    resp_lines: list[dict] = []
    for ln in lines[-50:]:
        try:
            o = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if o.get("hook_event_name") != "afterAgentResponse":
            continue
        if o.get("generation_id") == "pipeline-test":
            continue
        resp_lines.append(o)
    if resp_lines:
        r = resp_lines[-1]
        ok = r.get("inline_after_response_ok")
        print("")
        print(f"Found non-test afterAgentResponse trace: inline_after_response_ok={ok}")
        if ok:
            print("→ Cursor IS delivering response text to the hook; if silent, check tts-daemon / audio.")
        else:
            print("→ Response hook ran but text was empty / wrong shape; check Cursor version.")

    wo_recent: list[dict] = []
    for ln in lines[-200:]:
        try:
            o = json.loads(ln)
        except json.JSONDecodeError:
            continue
        if o.get("hook_event_name") == "workspaceOpen":
            wo_recent.append(o)
    if wo_recent:
        w = wo_recent[-1]
        cdir = str(w.get("cursor_project_dir") or "")[:120]
        print("")
        print(f"Legacy workspaceOpen trace (older config): ts={w.get('ts')}")
        if cdir:
            print(f"  CURSOR_PROJECT_DIR: {cdir}")

    hook_tail = ""
    if hook_log.is_file():
        hook_tail = "\n".join(hook_log.read_text(encoding="utf-8").splitlines()[-3:])

    if hook_tail:
        last_hook = hook_tail.splitlines()[-1] if hook_tail else ""
        if "hook_invoked" in last_hook and "pipeline-test" not in last_hook and age_s >= 0 and age_s < 600:
            print("")
            print("Recent speak_summary-hook.log tail looks non-test — compare timestamps with trace.")


if __name__ == "__main__":
    main()
