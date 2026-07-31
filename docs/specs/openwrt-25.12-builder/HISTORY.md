# History

- Chose `25.12.2` because the target release and package trees are published and stable.
- Rejected broad third-party feed collections to keep the dependency surface narrow.
- Kept only the upstream component repositories needed for the currently enabled apps.
- Added local packages for features that need a small compatibility layer instead of a new feed.
- Kept the image LAN default aligned with the existing PVE network while allowing manual CI builds to override it without making that input mandatory.
- Passed the workflow LAN input through the step environment so untrusted dispatch input is not parsed as shell source.
- Chose draft-first release publication so a failed asset upload cannot leave a public firmware release without downloadable files.
- Required locked components to remain selected so fetching a LuCI source tree cannot silently produce firmware without its menu package.
