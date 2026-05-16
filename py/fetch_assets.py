#!/usr/bin/env python3
"""Download Supertone/supertonic-3 model assets into <repo>/assets (gitignored by default)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _marker_ok(assets: Path) -> bool:
    onnx = assets / "onnx" / "tts.json"
    return onnx.is_file()


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
        help="Repository root (parent of py/).",
    )
    p.add_argument(
        "--repo-id",
        default="Supertone/supertonic-3",
        help="Hugging Face Hub repo id.",
    )
    p.add_argument(
        "--force",
        action="store_true",
        help="Download even if assets/onnx/tts.json already exists.",
    )
    args = p.parse_args()
    root: Path = args.repo_root.resolve()
    dest = root / "assets"
    if _marker_ok(dest) and not args.force:
        print(f"fetch_assets: already present ({dest / 'onnx' / 'tts.json'}); use --force to re-download.")
        return 0
    try:
        from huggingface_hub import snapshot_download
    except ImportError:
        print(
            "fetch_assets: huggingface_hub is required. Install with:\n"
            "  uv pip install huggingface_hub\n"
            "or run the repo bootstrap script which uses `uv run --with huggingface_hub`.",
            file=sys.stderr,
        )
        return 1
    dest.mkdir(parents=True, exist_ok=True)
    print(f"fetch_assets: downloading {args.repo_id} -> {dest} …", flush=True)
    snapshot_download(repo_id=args.repo_id, local_dir=str(dest))
    if not _marker_ok(dest):
        print(
            f"fetch_assets: download finished but {dest / 'onnx' / 'tts.json'} not found; "
            "check the Hub repo layout.",
            file=sys.stderr,
        )
        return 1
    print("fetch_assets: done.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
