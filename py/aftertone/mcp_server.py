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


def _repo_args():
    class A:
        repo_root = None

    return A()


def _capture_stdout(fn) -> str:
    buf: list[str] = []

    class Capturing:
        def write(self, s):
            buf.append(s)

    old = sys.stdout
    sys.stdout = Capturing()  # type: ignore[assignment]
    try:
        fn()
    finally:
        sys.stdout = old
    return "".join(buf)


def _status_impl() -> str:
    from aftertone.cli import cmd_status

    return _capture_stdout(lambda: cmd_status(_repo_args()))


def _doctor_impl() -> str:
    from aftertone.doctor import run_doctor

    return _capture_stdout(lambda: run_doctor(None))


def _run_cli(fn) -> str:
    rc = fn(_repo_args())
    return "ok" if rc == 0 else f"failed rc={rc}"


def _set_args(**kwargs):
    class A:
        repo_root = None

    ns = A()
    for key, value in kwargs.items():
        setattr(ns, key, value)
    return ns


def _speak_impl(text: str) -> str:
    from aftertone.cli import cmd_speak

    rc = cmd_speak(_set_args(text=text))
    return "ok" if rc == 0 else f"failed rc={rc}"


def _set_lang_impl(code: str) -> str:
    from aftertone.cli import cmd_set_lang

    rc = cmd_set_lang(_set_args(code=code))
    return f"lang={code}" if rc == 0 else f"failed rc={rc}"


def _set_speed_impl(value: str) -> str:
    from aftertone.cli import cmd_set_speed

    rc = cmd_set_speed(_set_args(value=value))
    return f"speed={value}" if rc == 0 else f"failed rc={rc}"


def _set_mode_impl(mode: str) -> str:
    from aftertone.cli import cmd_set_mode

    rc = cmd_set_mode(_set_args(mode=mode))
    return f"mode={mode}" if rc == 0 else f"failed rc={rc}"


def _set_expression_impl(mode: str) -> str:
    from aftertone.cli import cmd_set_expression

    rc = cmd_set_expression(_set_args(mode=mode))
    return f"expression={mode}" if rc == 0 else f"failed rc={rc}"


def _set_voice_impl(preset: str, ensure: bool, restart: bool) -> str:
    from aftertone.cli import cmd_set_voice

    rc = cmd_set_voice(
        _set_args(
            preset=preset,
            ensure=ensure,
            restart=restart,
        )
    )
    if rc != 0:
        return f"failed rc={rc}"
    extras = []
    if ensure:
        extras.append("ensure")
    if restart:
        extras.append("restart")
    suffix = f" ({', '.join(extras)})" if extras else ""
    return f"voice={preset}{suffix}"


def main() -> None:
    mcp = _require_mcp()

    @mcp.tool()
    def aftertone_status() -> str:
        """Daemon and config status."""
        return _status_impl()

    @mcp.tool()
    def aftertone_on() -> str:
        from aftertone.cli import cmd_on

        rc = cmd_on(_repo_args())
        return "on" if rc == 0 else f"failed rc={rc}"

    @mcp.tool()
    def aftertone_off() -> str:
        from aftertone.cli import cmd_off

        rc = cmd_off(_repo_args())
        return "off" if rc == 0 else f"failed rc={rc}"

    @mcp.tool()
    def aftertone_speak(text: str) -> str:
        """Speak arbitrary text through the daemon."""
        return _speak_impl(text)

    @mcp.tool()
    def aftertone_doctor() -> str:
        return _doctor_impl()

    @mcp.tool()
    def aftertone_restart() -> str:
        from aftertone.cli import cmd_restart

        return _run_cli(cmd_restart)

    @mcp.tool()
    def aftertone_repair() -> str:
        from aftertone.cli import cmd_repair

        return _run_cli(cmd_repair)

    @mcp.tool()
    def aftertone_set_lang(code: str) -> str:
        """Set spoken-summary language and sync the rule."""
        return _set_lang_impl(code)

    @mcp.tool()
    def aftertone_set_speed(value: str) -> str:
        """Set playback speed."""
        return _set_speed_impl(value)

    @mcp.tool()
    def aftertone_set_mode(mode: str) -> str:
        """Set playback mode to queue or interrupt."""
        return _set_mode_impl(mode)

    @mcp.tool()
    def aftertone_set_expression(mode: str) -> str:
        """Set expression mode."""
        return _set_expression_impl(mode)

    @mcp.tool()
    def aftertone_set_voice(
        preset: str, ensure: bool = False, restart: bool = True
    ) -> str:
        """Set voice preset. Restart is on by default."""
        return _set_voice_impl(preset, ensure, restart)

    mcp.run()


if __name__ == "__main__":
    main()
