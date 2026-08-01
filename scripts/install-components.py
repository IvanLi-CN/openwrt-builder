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


def patch_openwrt_25_12_compat(openwrt_dir: Path):
    for package in ("luci-app-netdata", "luci-app-zerotier"):
        makefile = openwrt_dir / "package" / "custom" / package / "Makefile"
        if makefile.exists():
            text = makefile.read_text()
            # Lean's selected applications expect to be nested below its LuCI tree.
            text = text.replace("include ../../luci.mk", "include $(TOPDIR)/feeds/luci/luci.mk")
            if package == "luci-app-netdata":
                text = text.replace("+netdata-ssl", "+netdata")
            makefile.write_text(text)


def destination_paths(component):
    destination = Path(component["destination"])
    if component["repo"] == "local" or component["paths"] == ["."]:
        return [destination]
    return [destination / Path(path).name for path in component["paths"]]


def validate_destinations(components):
    owners = {}
    for component in components:
        for destination in destination_paths(component):
            key = str(destination)
            previous = owners.get(key)
            if previous:
                raise ValueError(
                    f"component destination collision: {key} is provided by {previous} and {component['name']}"
                )
            owners[key] = component["name"]


def install_component(component, openwrt_dir: Path, cache_dir: Path):
    repo = component["repo"]
    if repo == "local":
        for rel in component["paths"]:
            src = ROOT / rel
            dst = openwrt_dir / component["destination"]
            copy_path(src, dst)
        return {"name": component["name"], "repo": repo, "ref": component["ref"], "commit": "local"}

    name = component["name"]
    ref = component["ref"]
    checkout_dir = cache_dir / name
    if checkout_dir.exists():
        shutil.rmtree(checkout_dir)
    run(["git", "clone", "--depth", "1", "--branch", ref, repo, str(checkout_dir)])
    revision = subprocess.run(
        ["git", "-C", str(checkout_dir), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    paths = component["paths"]
    if paths == ["."]:
        copy_path(checkout_dir, openwrt_dir / component["destination"])
        return {"name": name, "repo": repo, "ref": ref, "commit": revision}

    dest_root = openwrt_dir / component["destination"]
    for rel in paths:
        src = checkout_dir / rel
        dst = dest_root / Path(rel).name
        copy_path(src, dst)
    return {"name": name, "repo": repo, "ref": ref, "commit": revision}


def main():
    if len(sys.argv) != 2:
        print("usage: install-components.py <openwrt-dir>", file=sys.stderr)
        return 2
    openwrt_dir = Path(sys.argv[1]).resolve()
    if not (openwrt_dir / "include" / "toplevel.mk").exists():
        print(f"not an OpenWrt tree: {openwrt_dir}", file=sys.stderr)
        return 2
    lock = json.loads(LOCK.read_text())
    validate_destinations(lock["components"])
    cache_dir = Path(os.environ.get("COMPONENT_CACHE", ROOT / "work" / "components"))
    cache_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for component in lock["components"]:
        print(f"==> installing {component['name']}")
        records.append(install_component(component, openwrt_dir, cache_dir))
    patch_openwrt_25_12_compat(openwrt_dir)
    (openwrt_dir / "openwrt-builder-components.json").write_text(
        json.dumps({"components": records}, indent=2, sort_keys=True) + "\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
