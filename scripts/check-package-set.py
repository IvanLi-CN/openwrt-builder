#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "config" / "components.lock.json"
DEVICES = ROOT / "config" / "devices.json"

EXTERNAL_PACKAGES = {
    "docker",
    "docker-compose",
    "dockerd",
    "luci-app-argon-config",
    "luci-app-dockerman",
    "luci-app-mosdns",
    "luci-app-netdata",
    "luci-app-netspeedtest",
    "luci-app-nikki",
    "luci-app-openclash",
    "luci-app-ramfree",
    "luci-app-socat",
    "luci-app-tailscale",
    "luci-app-wolplus",
    "luci-app-zerotier",
    "luci-theme-argon",
    "mihomo-meta",
    "nikki",
}


def load_package_names(*paths):
    names = []
    for path in paths:
        for line in Path(path).read_text().splitlines():
            line = line.strip()
            if line.startswith("CONFIG_PACKAGE_") and line.endswith("=y"):
                names.append(line[len("CONFIG_PACKAGE_"):-2])
    return names


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True, choices=("lite", "server"))
    parser.add_argument("--device", required=True, choices=tuple(json.loads(DEVICES.read_text()).keys()))
    parser.add_argument("--verify-upstreams", action="store_true")
    args = parser.parse_args()

    packages = load_package_names(ROOT / "config" / "packages.common")
    if args.version == "server":
        packages.extend(load_package_names(ROOT / "config" / "server.config"))

    lock = json.loads(LOCK.read_text())
    selected_packages = set(packages)
    errors = []
    for component in lock["components"]:
        if component["name"] not in selected_packages:
            errors.append(f"locked component is not selected: {component['name']}")

    for pkg in packages:
        if pkg in EXTERNAL_PACKAGES:
            continue
        if not pkg:
            errors.append("empty package name")

    if args.verify_upstreams:
        for component in lock["components"]:
            repo = component["repo"]
            ref = component["ref"]
            if repo == "local":
                continue
            r = subprocess.run(["git", "ls-remote", "--heads", repo, ref], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if r.returncode != 0 or not r.stdout.strip():
                errors.append(f"upstream ref unavailable: {component['name']} {repo} {ref}")

    if errors:
        print("package set check failed:", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print(f"package set check passed for {args.version}/{args.device}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
