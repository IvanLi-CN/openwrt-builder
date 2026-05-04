#!/usr/bin/env python3
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "config" / "components.lock.json"


def run(cmd, cwd=None):
    print("+", " ".join(map(str, cmd)))
    subprocess.run(cmd, cwd=cwd, check=True)


def copy_path(src: Path, dst: Path):
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_dir():
        shutil.copytree(src, dst, ignore=shutil.ignore_patterns(".git", ".github"))
    else:
        shutil.copy2(src, dst)


def install_component(component, openwrt_dir: Path, cache_dir: Path):
    repo = component["repo"]
    if repo == "local":
        for rel in component["paths"]:
            src = ROOT / rel
            dst = openwrt_dir / component["destination"]
            copy_path(src, dst)
        return

    name = component["name"]
    ref = component["ref"]
    checkout_dir = cache_dir / name
    if checkout_dir.exists():
        shutil.rmtree(checkout_dir)
    run(["git", "clone", "--depth", "1", "--branch", ref, repo, str(checkout_dir)])

    paths = component["paths"]
    if paths == ["."]:
        copy_path(checkout_dir, openwrt_dir / component["destination"])
        return

    dest_root = openwrt_dir / component["destination"]
    for rel in paths:
        src = checkout_dir / rel
        dst = dest_root / Path(rel).name
        copy_path(src, dst)


def main():
    if len(sys.argv) != 2:
        print("usage: install-components.py <openwrt-dir>", file=sys.stderr)
        return 2
    openwrt_dir = Path(sys.argv[1]).resolve()
    if not (openwrt_dir / "include" / "toplevel.mk").exists():
        print(f"not an OpenWrt tree: {openwrt_dir}", file=sys.stderr)
        return 2
    lock = json.loads(LOCK.read_text())
    cache_dir = Path(os.environ.get("COMPONENT_CACHE", ROOT / "work" / "components"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    for component in lock["components"]:
        print(f"==> installing {component['name']}")
        install_component(component, openwrt_dir, cache_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
