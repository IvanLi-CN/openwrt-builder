# openwrt-builder

OpenWrt image builder for the 25.12 line, with the current firmware UI and feature set preserved as the default target.

## What this repo does

- Pins OpenWrt to `v25.12.2` and official `openwrt-25.12` feeds.
- Reuses only the specific upstream component repositories needed for the enabled apps.
- Keeps the current UI stack: Argon, LuCI, and the enabled app set carried over from `openwrt-lite`.
- Builds `lite` and `server` images for `x86_64`, `nanopi-r4s`, and `nanopi-r5s`.

## Quick start

```bash
scripts/check-component-policy.py
scripts/check-package-set.py --version lite --device x86_64
scripts/build.sh lite x86_64
```

## Build cache

`DL_DIR` selects the persistent directory for OpenWrt source downloads and
defaults to `./dl`. Set `CCACHE_DIR` to opt into a persistent compiler cache;
leaving it unset preserves the normal compiler path.

Manual GitHub Actions builds cache `dl/` and `.ccache/` only for `x86_64`.
Cache restore and save failures fall back to a regular build, so cache
availability does not affect the firmware result. The repository keeps the
GitHub Actions default cache limit and retention policy; inspect the workflow
log's cache-size line after a build before changing that policy.

## Deployment

- [Deploy on Proxmox VE 9 as a VM](docs/deploy-pve-9-vm.md)

## Pre-release downloads

Firmware builds are published as GitHub pre-releases. Download the image that
matches the target boot mode, along with `sha256sums.txt` and
`buildinfo.tar.gz`.

`sha256sums.txt` covers every firmware image and the build-information archive.
Verify the downloaded payloads before flashing:

```bash
sha256sum -c sha256sums.txt
```

`buildinfo.tar.gz` contains the generated configuration, feed revisions,
version information, and package manifest for the build.

## Layout

- `config/` pinned source and package selections
- `packages/` local compatibility packages
- `files/` runtime overlay copied into the image
- `scripts/` validation, build, and artifact collection
