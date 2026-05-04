# Implementation Notes

- Base tree: `scripts/build.sh` pulls `openwrt/openwrt` at `v25.12.2`.
- Feeds: official `openwrt-25.12` feeds only.
- Third-party features are pinned in `config/components.lock.json`.
- Local shims:
  - `packages/luci-app-ramfree`
  - `packages/luci-app-zerotier`
- Runtime overlay files are tracked under `files/`.
- CI entrypoint: `.github/workflows/build-openwrt.yml`.

