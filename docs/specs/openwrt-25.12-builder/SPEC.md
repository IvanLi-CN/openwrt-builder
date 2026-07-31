# OpenWrt 25.12 Builder

## Goal

Build the repository's custom firmware flavor on the OpenWrt 25.12 release line for x86_64, preserving the enabled `openwrt-lite` custom capabilities while using maintained, compatible sources.

## Scope

- Publish x86_64 only, with `lite` and `server` profiles.
- Resolve the highest stable `v25.12.x` tag at build time; use the official `openwrt-25.12` feeds.
- Keep `custom` as an internal package flavor rather than a user-facing release choice.
- Preserve a required free-text `build_options` interface with safe `KEY=value` parsing.
- Provide an explicit hardware and feature compatibility set for network drivers, storage, USB, zram, BBR, and firewall4 flow offloading.
- Use official packages first, selected Lean LuCI directories only for Netdata and ZeroTier, then individual package upstreams and local compatibility packages.

## Non-goals

- ARM targets or R4S/R5S publication.
- Ordinary versus custom user profile selection.
- Commit-SHA pinning for OpenWrt patch releases or third-party components.
- Broad third-party feed imports.
- BBR3, Brutal, SFE, LRNG, mold, LTO, or other private build/kernel patches from the historical project.

## Contracts

- `lite` is the default profile; `server` is a strict package superset.
- `NO_APPS=y` keeps base LuCI, Argon, drivers, filesystems, and system tools while removing optional applications and their application-only runtimes.
- `build_options` accepts shell-quoted `KEY=value` tokens as data. It may supply arbitrary business variables but cannot replace source refs, paths, jobs, Git environment, GitHub execution context, or credential values.
- Component refs are named branches or tags. The build records the resolved commits for traceability without treating them as future pins.
- Manual releases default to prerelease. Stable releases are GitHub Latest. Empty tags use the resolved OpenWrt tag, flavor, x86_64, and an Asia/Shanghai timestamp.

## Acceptance Criteria

- Device configuration exposes only `x86_64` with 64 MiB kernel and 1024 MiB rootfs partitions.
- Static checks validate both profiles, source policy, source reachability, server superset behavior, forbidden historical patches, and `NO_APPS` composition.
- After `make defconfig`, capability checks validate the actual selected package set.
- PRs compile and QEMU boot `server/x86_64`; manual builds QEMU boot the selected profile before publication.
- Each release contains checksum-verified firmware files, `sha256sums.txt`, and `buildinfo.tar.gz` with resolved source/version/option provenance.
- The default LAN is `192.168.31.1`; manual builds may optionally supply a validated LAN input or set `LAN` through `build_options`.

## Visual Evidence

None. This work changes build inputs and repository automation, not a rendered UI.
