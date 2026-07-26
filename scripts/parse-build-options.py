#!/usr/bin/env python3
"""CLI adapter for the safe build option parser."""

from __future__ import annotations

import argparse
import json
import os
import sys

from build_options import BuildOptionError, parse_build_options


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=("json", "nul"), default="json")
    parser.add_argument("value", nargs="?", default=os.environ.get("BUILD_OPTIONS", ""))
    args = parser.parse_args()
    try:
        options = parse_build_options(args.value)
    except BuildOptionError as exc:
        print(f"invalid build_options: {exc}", file=sys.stderr)
        return 2

    if args.format == "json":
        print(json.dumps(options, sort_keys=True))
        return 0

    for name, value in options.items():
        sys.stdout.buffer.write(name.encode() + b"\0" + value.encode() + b"\0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
