#!/usr/bin/env bash
# Cursor hook: append one diagnostic JSONL line (which hook fired, sizes, keys).
# Does not speak. Use to verify Cursor is invoking hooks after a real agent turn:
#   tail -20 .cursor/hooks/state/hook_payload_trace.jsonl

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="${SCRIPT_DIR}"
while [[ "${REPO}" != "/" ]]; do
  if [[ -f "${REPO}/py/speak_summary_prepare.py" ]]; then
    break
  fi
  REPO="$(dirname "${REPO}")"
done
[[ -f "${REPO}/py/speak_summary_prepare.py" ]] || exit 0

PY="${REPO}/py"
STATE_DIR="${REPO}/.cursor/hooks/state"
mkdir -p "${STATE_DIR}"
TRACE="${STATE_DIR}/hook_payload_trace.jsonl"

if [[ -x "${PY}/.venv/bin/python" ]]; then
  cat | "${PY}/.venv/bin/python" "${PY}/hook_payload_trace.py" "${TRACE}"
elif command -v uv >/dev/null 2>&1; then
  cat | (cd "${PY}" && uv run python hook_payload_trace.py "${TRACE}")
else
  cat | PYTHONPATH="${PY}" python3 "${PY}/hook_payload_trace.py" "${TRACE}"
fi
exit 0
