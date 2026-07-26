#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
VERSION=${1:-}
DEVICE=${2:-}
PYTHON=${PYTHON:-python3}
BUILD_OPTIONS=${BUILD_OPTIONS:-}

if [[ "$VERSION" != "lite" && "$VERSION" != "server" ]]; then
  echo "usage: scripts/build.sh <lite|server> <x86_64>" >&2
  exit 2
fi
if [[ "$DEVICE" != "x86_64" ]]; then
  echo "unsupported device: $DEVICE (only x86_64 is published)" >&2
  exit 2
fi

# build_options is data, never shell source. The parser emits NUL-delimited pairs.
while IFS= read -r -d '' name && IFS= read -r -d '' value; do
  export "$name=$value"
done < <("$PYTHON" "$ROOT/scripts/parse-build-options.py" --format nul -- "$BUILD_OPTIONS")

WORKDIR=${WORKDIR:-$ROOT/work}
OPENWRT_DIR=${OPENWRT_DIR:-$WORKDIR/openwrt}
DL_DIR=${DL_DIR:-$ROOT/dl}
COMPONENT_CACHE=${COMPONENT_CACHE:-$WORKDIR/components}
LAN=${LAN:-10.0.0.1}
JOBS=${JOBS:-$(($(nproc 2>/dev/null || sysctl -n hw.ncpu) + 1))}
NO_APPS=${NO_APPS:-n}
BUILD_FAST=${BUILD_FAST:-n}

if [[ "$NO_APPS" != "y" && "$NO_APPS" != "n" ]]; then
  echo "NO_APPS must be y or n" >&2
  exit 2
fi
if [[ "$BUILD_FAST" != "y" && "$BUILD_FAST" != "n" ]]; then
  echo "BUILD_FAST must be y or n" >&2
  exit 2
fi

source_json=$($PYTHON - "$ROOT/config/components.lock.json" <<'PY'
import json
import sys

data = json.load(open(sys.argv[1]))["openwrt"]
print(json.dumps(data))
PY
)
OPENWRT_REPO=$(printf '%s' "$source_json" | $PYTHON -c 'import json,sys; print(json.load(sys.stdin)["repo"])')
OPENWRT_SERIES=$(printf '%s' "$source_json" | $PYTHON -c 'import json,sys; print(json.load(sys.stdin)["series"])')
FEEDS_REF=$(printf '%s' "$source_json" | $PYTHON -c 'import json,sys; print(json.load(sys.stdin)["feeds_ref"])')
RESOLVED_OPENWRT_REF=$($PYTHON "$ROOT/scripts/resolve-openwrt-version.py" --repo "$OPENWRT_REPO" --series "$OPENWRT_SERIES")

mkdir -p "$WORKDIR" "$DL_DIR" "$COMPONENT_CACHE"

profile_json=$($PYTHON - "$ROOT/config/devices.json" "$DEVICE" <<'PY'
import json
import sys

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
  git clone --depth 1 --branch "$RESOLVED_OPENWRT_REF" "$OPENWRT_REPO" "$OPENWRT_DIR"
else
  git -C "$OPENWRT_DIR" fetch --depth 1 origin "refs/tags/$RESOLVED_OPENWRT_REF"
  git -C "$OPENWRT_DIR" checkout --detach FETCH_HEAD
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
COMPONENT_CACHE="$COMPONENT_CACHE" "$ROOT/scripts/install-components.py" "$OPENWRT_DIR"

mkdir -p files/etc/uci-defaults files/etc/sysctl.d
cp -a "$ROOT/files/." files/ 2>/dev/null || true
cat > files/etc/uci-defaults/99-openwrt-builder-defaults <<EOF
#!/bin/sh
uci -q set system.@system[0].timezone='CST-8'
uci -q set system.@system[0].zonename='Asia/Shanghai'
uci -q set firewall.@defaults[0].flow_offloading='1'
uci -q set firewall.@defaults[0].flow_offloading_hw='0'
uci -q commit system
uci -q commit firewall
exit 0
EOF
chmod +x files/etc/uci-defaults/99-openwrt-builder-defaults

sed -i.bak "s/192.168.1.1/$LAN/g" package/base-files/files/bin/config_generate
rm -f package/base-files/files/bin/config_generate.bak

cat > .config <<EOF
CONFIG_TARGET_${TARGET%/*}=y
CONFIG_TARGET_${TARGET%/*}_${TARGET#*/}=y
CONFIG_TARGET_${TARGET%/*}_${TARGET#*/}_DEVICE_${PROFILE//-/_}=y
EOF
cat "$ROOT/config/packages.base" >> .config
cat "$ROOT/config/$VERSION.config" >> .config
if [[ "$NO_APPS" != "y" ]]; then
  cat "$ROOT/config/packages.apps" >> .config
  if [[ "$VERSION" == "server" ]]; then
    cat "$ROOT/config/server.apps" >> .config
  fi
fi
$PYTHON - "$profile_json" >> .config <<'PY'
import json
import sys

profile = json.loads(sys.argv[1])
for line in profile.get("config", []):
    print(line)
PY

make defconfig
check_args=(--version "$VERSION" --device "$DEVICE" --resolved-config "$OPENWRT_DIR/.config")
if [[ "$NO_APPS" == "y" ]]; then
  check_args+=(--no-apps)
fi
"$PYTHON" "$ROOT/scripts/check-package-set.py" "${check_args[@]}"

"$PYTHON" "$ROOT/scripts/write-build-metadata.py" \
  --output "$OPENWRT_DIR/openwrt-builder-metadata.json" \
  --openwrt-repo "$OPENWRT_REPO" \
  --resolved-tag "$RESOLVED_OPENWRT_REF" \
  --openwrt-commit "$(git rev-parse HEAD)" \
  --feeds-ref "$FEEDS_REF" \
  --components "$OPENWRT_DIR/openwrt-builder-components.json" \
  --build-options "$BUILD_OPTIONS"

if [[ "$BUILD_FAST" == "y" ]]; then
  make -j"$JOBS" download || make download V=s
fi
make -j"$JOBS" || make -j1 V=s
