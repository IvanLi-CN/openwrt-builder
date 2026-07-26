#!/usr/bin/env python3
"""Validate narrow, branch/tag-based third-party component sourcing."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "config" / "components.lock.json"
DENY = ("github.com/pmkol/", "pmkol/openwrt-feeds", "pmkol/openwrt-source")
SHA_RE = re.compile(r"^[0-9a-f]{40}$", re.IGNORECASE)
REF_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
VALID_TIERS = {"local", "package-upstream", "selected-directory"}
LEAN_REPO = "https://github.com/coolsnowwolf/luci.git"
LEAN_PATHS = {"applications/luci-app-netdata", "applications/luci-app-zerotier"}


def main() -> int:
    lock = json.loads(LOCK.read_text())
    errors: list[str] = []
    openwrt = lock.get("openwrt", {})
    if openwrt.get("series") != "25.12":
        errors.append("OpenWrt series must be 25.12")
    if "ref" in openwrt:
        errors.append("OpenWrt must resolve the v25.12.x tag at build time, not store a fixed ref")
    for key in ("repo", "series", "feeds_ref"):
        if not openwrt.get(key):
            errors.append(f"missing openwrt.{key}")

    providers: dict[str, str] = {}
    for component in lock.get("components", []):
        name = component.get("name", "<unnamed>")
        repo = component.get("repo", "")
        ref = component.get("ref", "")
        for key in ("name", "repo", "ref", "paths", "destination", "provides", "source_tier"):
            if key not in component:
                errors.append(f"missing {key} in component: {name}")
        if any(token in repo for token in DENY):
            errors.append(f"forbidden dependency for {name}: {repo}")
        if component.get("source_tier") not in VALID_TIERS:
            errors.append(f"invalid source tier for {name}: {component.get('source_tier')}")
        if repo == "local":
            if ref != "local":
                errors.append(f"local component must use local ref: {name}")
        else:
            if not repo.startswith("https://github.com/"):
                errors.append(f"external component must use GitHub HTTPS URL: {name} => {repo}")
            if not REF_RE.fullmatch(ref) or SHA_RE.fullmatch(ref):
                errors.append(f"component ref must be a branch or tag, not a commit SHA: {name} => {ref}")
        if repo == LEAN_REPO:
            if component.get("source_tier") != "selected-directory":
                errors.append("Lean source must be limited to selected directories")
            if set(component.get("paths", [])) != LEAN_PATHS:
                errors.append("Lean source may only provide Netdata and ZeroTier LuCI directories")
        for package in component.get("provides", []):
            if package in providers:
                errors.append(f"duplicate component provider {package}: {providers[package]} and {name}")
            providers[package] = name

    for path in ROOT.rglob("*"):
        if path.name == "check-component-policy.py":
            continue
        if path.is_file() and ".git" not in path.parts and "__pycache__" not in path.parts:
            text = path.read_text(errors="ignore")
            for token in DENY:
                if token in text:
                    errors.append(f"forbidden token {token} in {path.relative_to(ROOT)}")

    if errors:
        print("component policy failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("component policy ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
