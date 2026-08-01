# openwrt-builder

OpenWrt 25.12 x86_64 firmware builder. It publishes one repository-defined custom flavor in two sizes: `lite` and `server`.

## What this repo does

- Resolves the newest stable `v25.12.x` tag at build time and uses official `openwrt-25.12` feeds.
- Builds only `x86_64`; `server` is a strict superset of `lite`.
- Keeps the custom LuCI stack: Argon, MosDNS, Netdata, Nikki, OpenClash, Tailscale, ZeroTier, Wake-on-LAN, and the other enabled `openwrt-lite` custom features.
- Uses official packages first, selected Lean 25.12 LuCI directories for Netdata and ZeroTier, then package-specific upstream repositories. Third-party sources follow branch/tag refs and never commit SHA pins.
- Uses explicit x86 driver, USB, filesystem, zram, BBR, and firewall4 flow-offload selections instead of `ALL_KMODS`, `ALL_NONSHARED`, or private kernel patches. The small local compatibility recipes expose only OpenWrt's in-tree Wangxun NGBE/TXGBE and Intel HDA modules where the 25.12 package set does not expose them for x86_64.

## Build locally

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check-component-policy.py
python3 scripts/check-package-set.py --version lite --device x86_64 --verify-upstreams
BUILD_OPTIONS='BUILD_FAST=y' scripts/build.sh lite x86_64
```

## Build cache

`DL_DIR` selects the persistent directory for OpenWrt source downloads and
defaults to `./dl`. Set `CCACHE_DIR` to opt into a persistent compiler cache;
leaving it unset preserves the normal compiler path.

GitHub Actions builds cache `dl/` and `.ccache/` only for `x86_64`.
Cache restore and save failures fall back to a regular build, so cache
availability does not change the selected package configuration or image target.
ccache is limited to 2 GiB before saving. GitHub Actions defaults to 10 GiB of
cache storage per repository and evicts entries that are not accessed for more
than 7 days; no additional cache storage is configured here.

## Deployment

- [Deploy on Proxmox VE 9 as a VM](docs/deploy-pve-9-vm.md)

`BUILD_OPTIONS` accepts a shell-quoted list of `KEY=value` assignments. It is parsed as data and is never sourced or evaluated. Existing build variables such as `LAN`, `BUILD_FAST`, and `NO_APPS` remain available; build source, work directory, job count, Git environment, GitHub context, and credential variables are protected. The default LAN is `192.168.31.1`; the manual workflow exposes the same value as an optional input.

`NO_APPS=y` retains LuCI, Argon, drivers, filesystems, and system tools while removing optional LuCI applications and their application-only runtimes. `CONFIG_CUSTOM` is intentionally not an option: the custom package flavor is fixed by this repository.

## Profiles

- `lite`: common custom router profile.
- `server`: lite plus server diagnostics, L2TP support, Docker, and Dockerman.

The release workflow validates both profile configurations. Pull requests additionally compile and QEMU boot the maximal `server/x86_64` image with read-only repository permissions. Manual builds compile and boot the selected profile before a separate write-authorized release job can create a release.

## Releases

Workflow dispatch requires `build_options` and defaults it to `BUILD_FAST=y`. It accepts shell-quoted `KEY=value` data without evaluation; source, path, GitHub/Git, shell-startup, Make-control, dynamic-loader, and interpreter-runtime variables are reserved. Publishing defaults to `prerelease`; select `stable` to make the result GitHub Latest. An empty release tag becomes:

```text
v<resolved-openwrt-version>-<lite|server>-x86_64-YYYYMMDD-HHMM
```

The timestamp uses `Asia/Shanghai`. Manual runs of the same profile are serialized; if a prior release already owns the generated minute-level tag, the later automatic tag adds `-r<GITHUB_RUN_NUMBER>`. Releases are created as drafts, populated only with checksum-verified artifacts, then made visible. Every download includes `sha256sums.txt` and `buildinfo.tar.gz`; buildinfo contains the resolved OpenWrt tag and commit, component revisions, final configuration, package manifest, and build options with credential-like names redacted.

## Layout

- `config/` source policy, package profiles, devices, and capability assertions
- `packages/` local compatibility packages
- `files/` runtime overlay copied into the image
- `scripts/` version resolution, validation, build, artifact collection, and release metadata
