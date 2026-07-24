# Implementation Notes

- Base tree: `scripts/build.sh` pulls `openwrt/openwrt` at `v25.12.2`.
- Feeds: official `openwrt-25.12` feeds only.
- Third-party features are pinned in `config/components.lock.json`.
- Local shims:
  - `packages/luci-app-ramfree`
  - `packages/luci-app-zerotier`
- Runtime overlay files are tracked under `files/`.
- CI entrypoint: `.github/workflows/build-openwrt.yml`.
- Release publication creates a draft first, uploads only regular artifact files, then marks the release as a prerelease after all uploads succeed.
- Collected build metadata is distributed as `buildinfo.tar.gz`; its checksum is included with the firmware payload checksums.
