#!/usr/bin/env python3
"""Write redacted source and option provenance into an OpenWrt worktree."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from build_metadata import write_metadata
from build_options import parse_build_options


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--openwrt-repo", required=True)
    parser.add_argument("--resolved-tag", required=True)
    parser.add_argument("--openwrt-commit", required=True)
    parser.add_argument("--feeds-ref", required=True)
    parser.add_argument("--components", required=True, type=Path)
    parser.add_argument("--build-options", default="")
    args = parser.parse_args()
    component_payload = json.loads(args.components.read_text())
    write_metadata(
        args.output,
        openwrt_repo=args.openwrt_repo,
        resolved_tag=args.resolved_tag,
        openwrt_commit=args.openwrt_commit,
        feeds_ref=args.feeds_ref,
        components=component_payload["components"],
        build_options=parse_build_options(args.build_options),
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
