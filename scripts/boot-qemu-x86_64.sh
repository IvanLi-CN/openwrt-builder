#!/usr/bin/env bash
set -euo pipefail

IMAGE=${1:-}
WORKDIR=${WORKDIR:-$(mktemp -d)}
TIMEOUT=${TIMEOUT:-90}

if [[ -z "$IMAGE" ]]; then
  echo "usage: scripts/boot-qemu-x86_64.sh <openwrt-x86_64-combined.img[.gz]>" >&2
  exit 2
fi
if [[ ! -f "$IMAGE" ]]; then
  echo "image not found: $IMAGE" >&2
  exit 2
fi
if ! command -v qemu-system-x86_64 >/dev/null 2>&1; then
  echo "qemu-system-x86_64 is required" >&2
  exit 2
fi

mkdir -p "$WORKDIR"
DISK="$WORKDIR/openwrt.img"
SERIAL_LOG="$WORKDIR/serial.log"
QEMU_LOG="$WORKDIR/qemu.log"

case "$IMAGE" in
  *.gz) gzip -dc "$IMAGE" > "$DISK" ;;
  *) cp "$IMAGE" "$DISK" ;;
esac

qemu-system-x86_64 \
  -machine pc,accel=tcg \
  -cpu max \
  -smp 1 \
  -m 256M \
  -nographic \
  -no-reboot \
  -drive "file=$DISK,format=raw,if=virtio" \
  -netdev user,id=wan \
  -device virtio-net-pci,netdev=wan \
  -serial "file:$SERIAL_LOG" \
  >"$QEMU_LOG" 2>&1 &
QEMU_PID=$!

# shellcheck disable=SC2317,SC2329 # Invoked by the EXIT trap below.
cleanup() {
  if kill -0 "$QEMU_PID" >/dev/null 2>&1; then
    kill "$QEMU_PID" >/dev/null 2>&1 || true
    wait "$QEMU_PID" >/dev/null 2>&1 || true
  fi
}
trap cleanup EXIT

deadline=$((SECONDS + TIMEOUT))
while (( SECONDS < deadline )); do
  if [[ -s "$SERIAL_LOG" ]]; then
    if grep -Eiq "kernel panic|not syncing|attempted to kill init|segmentation fault" "$SERIAL_LOG"; then
      echo "boot failed; serial log contains a fatal error" >&2
      tail -n 120 "$SERIAL_LOG" >&2
      exit 1
    fi
    if grep -Eq "Please press Enter to activate this console|procd: - init complete -|BusyBox" "$SERIAL_LOG"; then
      echo "boot ok: OpenWrt reached userspace"
      tail -n 80 "$SERIAL_LOG"
      exit 0
    fi
  fi
  if ! kill -0 "$QEMU_PID" >/dev/null 2>&1; then
    echo "qemu exited before OpenWrt reached userspace" >&2
    tail -n 120 "$SERIAL_LOG" >&2 || true
    tail -n 120 "$QEMU_LOG" >&2 || true
    exit 1
  fi
  sleep 2
done

echo "boot timed out after ${TIMEOUT}s" >&2
tail -n 120 "$SERIAL_LOG" >&2 || true
exit 1
