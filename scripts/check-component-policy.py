#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCK = ROOT / "config" / "components.lock.json"
DENY = ("github.com/pmkol/", "pmkol/openwrt-feeds", "pmkol/openwrt-source")
ALLOW_BROAD = False

lock = json.loads(LOCK.read_text())
errors = []
for component in lock.get("components", []):
    repo = component.get("repo", "")
    if any(token in repo for token in DENY):
        errors.append(f"forbidden dependency for {component.get('name')}: {repo}")
    for key in ("name", "repo", "ref", "paths", "destination"):
        if key not in component:
            errors.append(f"missing {key} in component: {component}")
    if repo != "local" and not repo.startswith("https://github.com/"):
        errors.append(f"external component must use GitHub HTTPS URL: {component.get('name')} => {repo}")

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
    for e in errors:
        print(f"- {e}", file=sys.stderr)
    sys.exit(1)
print("component policy ok")
