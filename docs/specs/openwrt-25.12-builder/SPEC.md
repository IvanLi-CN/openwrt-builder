# OpenWrt 25.12 Builder

## Goal

Build a replacement for the current firmware line on OpenWrt `25.12` without changing the visible UI or removing the enabled features that are already in use.

## Scope

- Move the base tree from OpenWrt `24.05` to `25.12.2`.
- Keep the current enabled LuCI applications and runtime behavior.
- Use official OpenWrt feeds as the base dependency source.
- Use only the specific upstream repositories required for the enabled third-party packages.
- Avoid broad third-party feed bundles.

## Acceptance Criteria

- The repo pins OpenWrt `v25.12.2` and `openwrt-25.12`.
- The enabled package set is expressed in tracked config files.
- Each non-official upstream component is pinned to a named repository and ref.
- Local compatibility packages exist for features that are not covered by official feeds.
- Build scripts can produce `lite` and `server` artifacts for `x86_64`, `nanopi-r4s`, and `nanopi-r5s`.
- Validation scripts can confirm the component policy and the package availability assumptions.
- Package-set validation fails when a component declared in `config/components.lock.json` is not selected by the tracked package configuration.
- The current UI defaults remain Argon + LuCI with the same enabled apps.
- The x86_64 image defaults its LAN address to `192.168.31.1`.
- Manual GitHub Actions builds may optionally override the image LAN address with a valid IPv4 value.
- The workflow must pass the optional LAN input through the step environment, not interpolate it into shell source.
- A manually published pre-release contains every collected firmware file, `sha256sums.txt`, and a `buildinfo.tar.gz` archive; it is not made public until all assets upload successfully.

## Visual Evidence

PR: none

This work changes build inputs and repo layout, not a rendered UI.
