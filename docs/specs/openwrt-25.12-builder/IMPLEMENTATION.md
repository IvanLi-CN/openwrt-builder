# Implementation Notes

- Base tree: `scripts/build.sh` pulls `openwrt/openwrt` at `v25.12.2`.
- Feeds: official `openwrt-25.12` feeds only.
- Third-party features are pinned in `config/components.lock.json`.
- Package-set validation cross-checks locked component names against the selected package configuration.
- Local shims:
  - `packages/luci-app-ramfree`
  - `packages/luci-app-zerotier`
- Runtime overlay files are tracked under `files/`.
- CI entrypoint: `.github/workflows/build-openwrt.yml`.
- `scripts/build.sh` defaults `LAN` to `192.168.31.1`, validates IPv4 input, and applies it to the generated OpenWrt LAN configuration.
- The manual build workflow passes its optional `lan` input through the build step environment before invoking `scripts/build.sh`.
- Release publication creates a draft first, uploads only regular artifact files, then marks the release as a prerelease after all uploads succeed.
- Collected build metadata is distributed as `buildinfo.tar.gz`; its checksum is included with the firmware payload checksums.
