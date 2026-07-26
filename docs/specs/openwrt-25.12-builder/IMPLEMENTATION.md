# Implementation Notes

- `scripts/resolve-openwrt-version.py` resolves the highest stable tag in the configured `25.12` series before cloning the OpenWrt tree.
- `config/packages.base`, `config/packages.apps`, `config/lite.config`, `config/server.config`, and `config/server.apps` compose the fixed custom flavor and enforce `NO_APPS` without post-hoc text deletion.
- `config/capabilities.json` declares the required application, x86 hardware, storage, USB, zram, BBR, flow-offload, and server capabilities. `scripts/check-package-set.py` checks both tracked profiles and post-defconfig output.
- `config/components.lock.json` uses official feeds, selected Lean 25.12 directories for Netdata and ZeroTier, package-specific upstreams for the remaining third-party applications, and the local ramfree package.
- `scripts/parse-build-options.py` parses free-text build options without evaluation. `scripts/write-build-metadata.py` records redacted options, source refs, and resolved commits.
- `.github/workflows/build-openwrt.yml` validates lite and server configuration, compiles and QEMU boots server on PRs, and compiles/QEMU boots the selected manual profile before draft-first publication.
- Collected `buildinfo.tar.gz` includes OpenWrt build metadata, final `.config`, component revision data, generated build information, and the package manifest.
