#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
VERSION=${1:-}
DEVICE=${2:-}

if [[ -z "$VERSION" || -z "$DEVICE" ]]; then
  echo "usage: scripts/build.sh <lite|server> <x86_64|nanopi-r4s|nanopi-r5s>" >&2
  exit 2
fi
if [[ "$VERSION" != "lite" && "$VERSION" != "server" ]]; then
  echo "invalid version: $VERSION" >&2
  exit 2
fi

PYTHON=${PYTHON:-python3}
WORKDIR=${WORKDIR:-$ROOT/work}
OPENWRT_DIR=${OPENWRT_DIR:-$WORKDIR/openwrt}
DL_DIR=${DL_DIR:-$ROOT/dl}
OPENWRT_REPO=${OPENWRT_REPO:-https://github.com/openwrt/openwrt.git}
OPENWRT_REF=${OPENWRT_REF:-v25.12.2}
FEEDS_REF=${FEEDS_REF:-openwrt-25.12}
LAN=${LAN:-10.0.0.1}
JOBS=${JOBS:-$(($(nproc 2>/dev/null || sysctl -n hw.ncpu) + 1))}
NO_APPS=${NO_APPS:-n}
BUILD_FAST=${BUILD_FAST:-n}

mkdir -p "$WORKDIR" "$DL_DIR"

profile_json=$($PYTHON - "$ROOT/config/devices.json" "$DEVICE" <<'PY'
import json, sys
path, device = sys.argv[1:3]
data = json.load(open(path))
if device not in data:
    raise SystemExit(f"unknown device: {device}")
print(json.dumps(data[device]))
PY
)
TARGET=$(printf '%s' "$profile_json" | $PYTHON -c 'import json,sys; print(json.load(sys.stdin)["target"])')
PROFILE=$(printf '%s' "$profile_json" | $PYTHON -c 'import json,sys; print(json.load(sys.stdin)["profile"])')

if [[ ! -d "$OPENWRT_DIR/.git" ]]; then
  git clone --depth 1 --branch "$OPENWRT_REF" "$OPENWRT_REPO" "$OPENWRT_DIR"
else
  git -C "$OPENWRT_DIR" fetch --depth 1 origin "$OPENWRT_REF"
  git -C "$OPENWRT_DIR" checkout FETCH_HEAD
  git -C "$OPENWRT_DIR" clean -xfd
  git -C "$OPENWRT_DIR" reset --hard
fi

cd "$OPENWRT_DIR"
cat > feeds.conf <<EOF
src-git packages https://github.com/openwrt/packages.git;$FEEDS_REF
src-git luci https://github.com/openwrt/luci.git;$FEEDS_REF
src-git routing https://github.com/openwrt/routing.git;$FEEDS_REF
src-git telephony https://github.com/openwrt/telephony.git;$FEEDS_REF
EOF

./scripts/feeds update -a
./scripts/feeds install -a
"$ROOT/scripts/install-components.py" "$OPENWRT_DIR"

mkdir -p files/etc/uci-defaults files/etc/sysctl.d
cp -a "$ROOT/files/." files/ 2>/dev/null || true
cat > files/etc/uci-defaults/99-openwrt-builder-defaults <<EOF
#!/bin/sh
uci -q set system.@system[0].timezone='CST-8'
uci -q set system.@system[0].zonename='Asia/Shanghai'
uci -q commit system
exit 0
EOF
chmod +x files/etc/uci-defaults/99-openwrt-builder-defaults

# Preserve current default LAN without carrying old base-files patches.
sed -i.bak "s/192.168.1.1/$LAN/g" package/base-files/files/bin/config_generate
rm -f package/base-files/files/bin/config_generate.bak

cat > .config <<EOF
CONFIG_TARGET_${TARGET%/*}=y
CONFIG_TARGET_${TARGET%/*}_${TARGET#*/}=y
CONFIG_TARGET_${TARGET%/*}_${TARGET#*/}_DEVICE_${PROFILE//-/_}=y
EOF
cat "$ROOT/config/packages.common" >> .config
if [[ "$NO_APPS" == "y" ]]; then
  sed -i.bak '/CONFIG_PACKAGE_luci-app-/d;/CONFIG_PACKAGE_luci-theme-argon/d;/CONFIG_PACKAGE_luci-app-argon-config/d' .config
  rm -f .config.bak
fi
cat "$ROOT/config/$VERSION.config" >> .config

make defconfig
if [[ "$BUILD_FAST" == "y" ]]; then
  make -j"$JOBS" download || make download V=s
fi
make -j"$JOBS" || make -j1 V=s
