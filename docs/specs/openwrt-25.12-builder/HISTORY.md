# History

- Chose dynamic stable `v25.12.x` selection so the repository follows the supported 25.12 patch line without embedding a stricter pin than the reference project.
- Reduced publication scope to x86_64 and made custom package selection a repository invariant, leaving users with only the meaningful lite/server choice.
- Replaced archived Tailscale and WOL sources with official 25.12 LuCI packages. Netdata and ZeroTier use only their maintained Lean LuCI directories instead of a broad feed import.
- Replaced `ALL_KMODS` and `ALL_NONSHARED` with an explicit compatibility set and official BBR/firewall4 flow-offload behavior.
- Kept draft-first release publication and extended build provenance so a release can be checked against its source revisions, final configuration, and redacted input parameters.
