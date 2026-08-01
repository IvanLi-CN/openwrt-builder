#!/usr/bin/env python3
"""Resolve the highest stable tag for the configured OpenWrt series."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys

from openwrt_version import latest_stable_tag


def remote_refs(repo: str) -> list[str]:
    result = subprocess.run(
        ["git", "ls-remote", "--tags", "--refs", repo],
        check=True,
        capture_output=True,
        text=True,
    )
    return [line.split("\t", 1)[1] for line in result.stdout.splitlines() if "\t" in line]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True)
    parser.add_argument("--series", required=True)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        tag = latest_stable_tag(remote_refs(args.repo), args.series)
    except (OSError, subprocess.CalledProcessError, ValueError) as exc:
        print(f"failed to resolve OpenWrt version: {exc}", file=sys.stderr)
        return 1
    if args.json:
        print(json.dumps({"series": args.series, "tag": tag}, sort_keys=True))
    else:
        print(tag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
