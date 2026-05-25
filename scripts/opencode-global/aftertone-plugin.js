// User-level OpenCode plugin (~/.config/opencode/plugins/aftertone.js).
// It keeps the adapter thin: collect the latest assistant text, then send one
// normalized post-reply JSON payload into the shared Aftertone hook runner.

import { existsSync, readFileSync } from "node:fs"
import { homedir } from "node:os"
import { join } from "node:path"
import { spawn } from "node:child_process"

const latestBySession = new Map()

function installRoot() {
  const opencodeMarker = join(homedir(), ".config", "opencode", "aftertone-install-dir")
  if (existsSync(opencodeMarker)) return readFileSync(opencodeMarker, "utf8").trim()
  const cursorMarker = join(homedir(), ".cursor", "hooks", "aftertone-install-dir")
  if (existsSync(cursorMarker)) return readFileSync(cursorMarker, "utf8").trim()
  return join(homedir(), "aftertone")
}

function sessionId(event) {
  return (
    event?.session_id ||
    event?.sessionId ||
    event?.session?.id ||
    event?.thread_id ||
    event?.threadId ||
    "opencode-default"
  )
}

function findText(value, depth = 0) {
  if (depth > 6 || value == null) return ""
  if (typeof value === "string") {
    return value.includes("<spoken_summary") ? value : ""
  }
  if (Array.isArray(value)) {
    for (const item of value) {
      const found = findText(item, depth + 1)
      if (found) return found
    }
    return ""
  }
  if (typeof value === "object") {
    for (const key of ["last_assistant_message", "output_text", "assistant_text", "text", "content", "message"]) {
      const found = findText(value[key], depth + 1)
      if (found) return found
    }
    for (const nested of Object.values(value)) {
      const found = findText(nested, depth + 1)
      if (found) return found
    }
  }
  return ""
}

function runAftertone(payload) {
  const root = installRoot()

  const envPatch = {
    ...process.env,
    AFTERTONE_REPO: root,
    AFTERTONE_INSTALL_DIR: root,
  }

  if (process.platform === "win32") {
    // On Windows plain "bash" resolves to WSL which opens a visible terminal
    // and closes immediately.  Route through the existing .cmd wrapper that
    // finds Git Bash correctly and runs headless.
    const cmdScript = join(root, ".cursor", "hooks", "speak_summary.cmd")
    if (existsSync(cmdScript)) {
      const child = spawn("cmd.exe", ["/c", cmdScript], {
        env: envPatch,
        stdio: ["pipe", "ignore", "ignore"],
        windowsHide: true,
        detached: true,
      })
      child.stdin.end(JSON.stringify(payload))
      child.unref()
      return
    }
    // Fallback: Git Bash at the standard install path.
    const gitBash = join(process.env["ProgramFiles"] || "C:\\Program Files", "Git", "bin", "bash.exe")
    if (existsSync(gitBash)) {
      const bashScript = join(root, ".cursor", "hooks", "speak_summary.sh")
      if (existsSync(bashScript)) {
        const child = spawn(gitBash, [bashScript], {
          env: envPatch,
          stdio: ["pipe", "ignore", "ignore"],
          windowsHide: true,
          detached: true,
        })
        child.stdin.end(JSON.stringify(payload))
        child.unref()
        return
      }
    }
  }

  // Non-Windows — or Windows fallback when no .cmd / Git Bash found.
  const shScript = join(root, ".cursor", "hooks", "speak_summary.sh")
  if (!existsSync(shScript)) return
  const child = spawn("bash", [shScript], {
    env: envPatch,
    stdio: ["pipe", "ignore", "ignore"],
    windowsHide: true,
    detached: true,
  })
  child.stdin.end(JSON.stringify(payload))
  child.unref()
}

export const AftertonePlugin = async () => {
  return {
    event: async ({ event }) => {
      const sid = sessionId(event)
      const text = findText(event)
      if (text) latestBySession.set(sid, text)

      if (event?.type !== "session.idle") return
      const last = latestBySession.get(sid)
      if (!last) return
      latestBySession.delete(sid)
      runAftertone({
        hook_event_name: "aftertone.response",
        adapter: "opencode",
        session_id: sid,
        last_assistant_message: last,
        model: event?.model,
      })
    },
  }
}
