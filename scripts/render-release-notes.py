#!/usr/bin/env python3
"""Render deterministic release tags and notes from collected build metadata."""

from __future__ import annotations

import argparse
from pathlib import Path

from build_metadata import load_metadata


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--metadata", required=True, type=Path)
    parser.add_argument("--format", choices=("tag", "notes"), required=True)
    parser.add_argument("--flavor")
    parser.add_argument("--device")
    parser.add_argument("--timestamp")
    parser.add_argument("--workflow-url")
    parser.add_argument("--commit")
    args = parser.parse_args()
    metadata = load_metadata(args.metadata)
    openwrt = metadata["openwrt"]
    if args.format == "tag":
        if not all((args.flavor, args.device, args.timestamp)):
            parser.error("tag format requires --flavor, --device, and --timestamp")
        print(f"{openwrt['resolved_tag']}-{args.flavor}-{args.device}-{args.timestamp}")
        return 0

    if not all((args.flavor, args.device, args.workflow_url, args.commit)):
        parser.error("notes format requires flavor, device, workflow URL, and commit")
    print(f"OpenWrt {openwrt['resolved_tag']} {args.flavor} {args.device} build.")
    print()
    print("Build parameters:")
    print(f"- OpenWrt commit: `{openwrt['commit']}`")
    print(f"- Official feeds: `{openwrt['feeds_ref']}`")
    for name, value in metadata["build_options"].items():
        print(f"- `{name}={value}`")
    print()
    print("Build evidence:")
    print(f"- Workflow run: {args.workflow_url}")
    print(f"- Builder commit: {args.commit}")
    print()
    print("Verify downloads with `sha256sum -c sha256sums.txt`.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
