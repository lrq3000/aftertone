"""Install root resolution."""

from __future__ import annotations

from pathlib import Path

from aftertone_paths import resolve_repo_root


def install_root(explicit: Path | None = None) -> Path:
    return resolve_repo_root(explicit)


def config_path(root: Path | None = None) -> Path:
    r = root or install_root()
    return r / ".cursor" / "hooks" / "speak_summary.toml"


def state_dir(root: Path | None = None) -> Path:
    r = root or install_root()
    return r / ".cursor" / "hooks" / "state"
