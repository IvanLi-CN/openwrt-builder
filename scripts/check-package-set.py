#!/usr/bin/env python3
"""Check profile composition before and after OpenWrt defconfig."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config"
LOCK = CONFIG / "components.lock.json"
DEVICES = CONFIG / "devices.json"
CAPABILITIES = CONFIG / "capabilities.json"
PACKAGE_RE = re.compile(r"^CONFIG_PACKAGE_([^=]+)=y$")


def package_names(paths: list[Path]) -> set[str]:
    packages: set[str] = set()
    for path in paths:
        for line in path.read_text().splitlines():
            match = PACKAGE_RE.fullmatch(line.strip())
            if match:
                packages.add(match.group(1))
    return packages


def profile_paths(version: str, no_apps: bool) -> list[Path]:
    paths = [CONFIG / "packages.base", CONFIG / f"{version}.config"]
    if not no_apps:
        paths.append(CONFIG / "packages.apps")
        if version == "server":
            paths.append(CONFIG / "server.apps")
    return paths


def all_tracked_config() -> str:
    return "\n".join(path.read_text() for path in CONFIG.glob("*.config")) + "\n" + (CONFIG / "packages.base").read_text() + (CONFIG / "packages.apps").read_text() + (CONFIG / "server.apps").read_text()


def verify_upstreams(lock: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for component in lock["components"]:
        repo = component["repo"]
        if repo == "local":
            continue
        ref = component["ref"]
        result = subprocess.run(
            ["git", "ls-remote", "--exit-code", repo, f"refs/heads/{ref}", f"refs/tags/{ref}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        if result.returncode != 0 or not result.stdout.strip():
            errors.append(f"upstream ref unavailable: {component['name']} {repo} {ref}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True, choices=("lite", "server"))
    parser.add_argument("--device", required=True, choices=("x86_64",))
    parser.add_argument("--no-apps", action="store_true")
    parser.add_argument("--resolved-config", type=Path)
    parser.add_argument("--verify-upstreams", action="store_true")
    args = parser.parse_args()

    capabilities = json.loads(CAPABILITIES.read_text())
    lock = json.loads(LOCK.read_text())
    devices = json.loads(DEVICES.read_text())
    errors: list[str] = []
    if set(devices) != {"x86_64"}:
        errors.append("only x86_64 may be declared as a published device")

    selected = package_names(profile_paths(args.version, args.no_apps))
    if args.resolved_config:
        selected = package_names([args.resolved_config])
    required = set(capabilities["base"])
    if not args.no_apps:
        required.update(capabilities["apps"])
    if args.version == "server":
        required.update(capabilities["server"])
        if not args.no_apps:
            required.update(capabilities["server_apps"])
    missing = sorted(required - selected)
    if missing:
        errors.append("missing required packages: " + ", ".join(missing))

    if args.no_apps:
        leaked = sorted(set(capabilities["apps"]) & selected)
        if leaked:
            errors.append("NO_APPS leaked optional packages: " + ", ".join(leaked))
        if args.version == "server":
            docker = {"docker", "dockerd", "docker-compose", "luci-app-dockerman"}
            leaked = sorted(docker & selected)
            if leaked:
                errors.append("NO_APPS leaked server application runtime: " + ", ".join(leaked))

    lite = package_names(profile_paths("lite", False))
    server = package_names(profile_paths("server", False))
    if not lite < server:
        errors.append("server package set must be a strict superset of lite")

    tracked = all_tracked_config()
    for forbidden in capabilities["forbidden_config"]:
        if forbidden in tracked:
            errors.append(f"forbidden configuration is enabled: {forbidden}")
    if "rockchip" in tracked.lower():
        errors.append("non-x86 target configuration is not allowed")

    providers = {package for component in lock["components"] for package in component["provides"]}
    expected_component_providers = {
        "luci-app-argon-config", "luci-theme-argon", "luci-app-mosdns", "luci-app-netdata",
        "luci-app-netspeedtest", "luci-app-nikki", "luci-app-openclash", "luci-app-ramfree",
        "luci-app-socat", "luci-app-zerotier", "mihomo-meta", "nikki", "kmod-ngbe",
        "kmod-sound-core-x86-64", "kmod-sound-hda-codec-realtek-x86-64",
        "kmod-sound-hda-core-x86-64", "kmod-sound-hda-intel-x86-64", "kmod-txgbe",
        "kmod-wangxun-libwx",
    }
    if providers != expected_component_providers:
        errors.append("component providers do not match the declared custom package source set")
    if args.verify_upstreams:
        errors.extend(verify_upstreams(lock))

    if errors:
        print("package set check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    scope = "resolved" if args.resolved_config else "tracked"
    print(f"package set check passed for {args.version}/{args.device} ({scope})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
