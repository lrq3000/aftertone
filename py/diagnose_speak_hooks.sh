#!/usr/bin/env bash
# Show recent Cursor hook diagnostics (after a real agent turn, reload Cursor if you changed hooks.json).
# Usage:
#   bash py/diagnose_speak_hooks.sh
#   bash py/diagnose_speak_hooks.sh path/to/hook.json   # replay hook JSON through speak_summary.sh

set -euo pipefail
REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -n "${1:-}" ]]; then
  HOOK_JSON="$1"
  if [[ ! -f "${HOOK_JSON}" ]]; then
    echo "hook JSON not found: ${HOOK_JSON}" >&2
    exit 1
  fi
  INSTALL="${AFTERTONE_INSTALL_DIR:-${HOME}/aftertone}"
  if [[ ! -f "${INSTALL}/py/speak_summary_prepare.py" ]]; then
    INSTALL="${REPO}"
  fi
  export AFTERTONE_REPO="${INSTALL}" AFTERTONE_INSTALL_DIR="${INSTALL}"
  ST="${INSTALL}/.cursor/hooks/state"
  echo "==> replay: ${HOOK_JSON} -> ${INSTALL}/.cursor/hooks/speak_summary.sh"
  echo "    log: ${ST}/speak_summary-hook.log"
  cat "${HOOK_JSON}" | bash "${INSTALL}/.cursor/hooks/speak_summary.sh"
  echo ""
  echo "==> last log lines:"
  tail -8 "${ST}/speak_summary-hook.log" 2>/dev/null || echo "(missing)"
  exit 0
fi

ST="${REPO}/.cursor/hooks/state"
echo "=== last 15 lines: hook_payload_trace.jsonl (did Cursor run afterAgentResponse / stop?) ==="
tail -15 "${ST}/hook_payload_trace.jsonl" 2>/dev/null || echo "(missing — no hook ran yet)"
echo ""
echo "=== last 20 lines: speak_summary-hook.log ==="
tail -20 "${ST}/speak_summary-hook.log" 2>/dev/null || echo "(missing)"

export DIAG_REPO="${REPO}"
# shellcheck source=../.cursor/hooks/venv_python.sh
source "${REPO}/.cursor/hooks/venv_python.sh"
vpy=""
if vpy="$(aftertone_venv_python "${REPO}/py")"; then
  "${vpy}" "${REPO}/py/diagnose_speak_hooks_report.py"
else
  echo ""
  echo "(Install venv: cd py && uv sync — then verdict script can run.)"
fi

echo ""
echo "Tip: run one Agent message in Cursor, wait until the reply FINISHES, then re-run:"
echo "  bash py/diagnose_speak_hooks.sh"
echo "You want a NEW line with a fresh timestamp and a generation_id that is NOT pipeline-test."
