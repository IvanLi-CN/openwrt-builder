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
