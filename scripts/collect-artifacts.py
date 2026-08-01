#!/usr/bin/env python3
import glob
import json
import shutil
import sys
import tarfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main():
    if len(sys.argv) != 4:
        print("usage: collect-artifacts.py <openwrt-dir> <device> <out-dir>", file=sys.stderr)
        return 2
    openwrt, device, out = Path(sys.argv[1]), sys.argv[2], Path(sys.argv[3])
    devices = json.loads((ROOT / "config" / "devices.json").read_text())
    cfg = devices[device]
    out.mkdir(parents=True, exist_ok=True)
    copied = []
    for pattern in cfg["artifact_globs"]:
        for src in glob.glob(str(openwrt / pattern)):
            dst = out / Path(src).name
            shutil.copy2(src, dst)
            copied.append(dst)
    target_dir = openwrt / "bin" / "targets" / cfg["target"]
    info = out / "buildinfo"
    info.mkdir(exist_ok=True)
    for name in ["config.buildinfo", "feeds.buildinfo", "version.buildinfo"]:
        src = target_dir / name
        if src.exists(): shutil.copy2(src, info / name)
    for src in target_dir.glob("*.manifest"):
        shutil.copy2(src, info / "manifest.txt")
        break
    for src, name in [
        (openwrt / ".config", "final.config"),
        (openwrt / "openwrt-builder-metadata.json", "openwrt-builder-metadata.json"),
        (openwrt / "openwrt-builder-components.json", "openwrt-builder-components.json"),
    ]:
        if src.exists(): shutil.copy2(src, info / name)
    if not copied:
        print("no firmware artifacts found", file=sys.stderr)
        return 1

    buildinfo_archive = out / "buildinfo.tar.gz"
    with tarfile.open(buildinfo_archive, "w:gz") as archive:
        archive.add(info, arcname=info.name)

    release_assets = sorted([*copied, buildinfo_archive], key=lambda path: path.name)
    import hashlib
    with (out / "sha256sums.txt").open("w") as f:
        for path in release_assets:
            f.write(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n")
    print(f"collected {len(copied)} firmware artifacts into {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
