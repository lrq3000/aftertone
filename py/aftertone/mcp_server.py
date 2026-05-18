#!/usr/bin/env python3
"""
Optional MCP control plane for Aftertone (not the speech trigger).

Run: uv run python -m aftertone.mcp_server
Requires: pip install mcp (optional dependency).
"""

from __future__ import annotations

import json
import sys


def _require_mcp():
    try:
        from mcp.server.fastmcp import FastMCP  # type: ignore[import-not-found]
    except ImportError as exc:
        print(
            "Install MCP SDK: uv pip install mcp",
            file=sys.stderr,
        )
        raise SystemExit(1) from exc
    return FastMCP("aftertone")


def main() -> None:
    mcp = _require_mcp()

    @mcp.tool()
    def aftertone_status() -> str:
        """Daemon and config status."""
        from aftertone.cli import cmd_status
        import argparse

        class A:
            repo_root = None

        buf: list[str] = []

        class Capturing:
            def write(self, s):
                buf.append(s)

        old = sys.stdout
        sys.stdout = Capturing()  # type: ignore[assignment]
        try:
            cmd_status(A())
        finally:
            sys.stdout = old
        return "".join(buf)

    @mcp.tool()
    def aftertone_on() -> str:
        from aftertone.cli import cmd_on
        import argparse

        class A:
            repo_root = None

        rc = cmd_on(A())
        return "on" if rc == 0 else f"failed rc={rc}"

    @mcp.tool()
    def aftertone_off() -> str:
        from aftertone.cli import cmd_off
        import argparse

        class A:
            repo_root = None

        rc = cmd_off(A())
        return "off" if rc == 0 else f"failed rc={rc}"

    @mcp.tool()
    def aftertone_speak(text: str) -> str:
        """Speak arbitrary text through the daemon."""
        from aftertone.cli import cmd_speak
        import argparse

        class A:
            repo_root = None
            text = text

        rc = cmd_speak(A())
        return "ok" if rc == 0 else f"failed rc={rc}"

    @mcp.tool()
    def aftertone_doctor() -> str:
        from aftertone.doctor import run_doctor

        buf: list[str] = []

        class Capturing:
            def write(self, s):
                buf.append(s)

        old = sys.stdout
        sys.stdout = Capturing()  # type: ignore[assignment]
        try:
            run_doctor(None)
        finally:
            sys.stdout = old
        return "".join(buf)

    mcp.run()


if __name__ == "__main__":
    main()
