"""Parse and redact user-provided build options without executing them."""

from __future__ import annotations

import re
import shlex
from collections.abc import Mapping


NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
SENSITIVE_RE = re.compile(r"TOKEN|PASSWORD|SECRET|KEY|CREDENTIAL", re.IGNORECASE)
RESERVED_NAMES = frozenset(
    {
        "BUILD_METADATA_FILE",
        "BUILD_OPTIONS",
        "COMPONENT_CACHE",
        "CONFIG_CUSTOM",
        "DL_DIR",
        "FEEDS_REF",
        "GH_TOKEN",
        "HOME",
        "JOBS",
        "OPENWRT_DIR",
        "OPENWRT_REPO",
        "OPENWRT_REF",
        "OPENWRT_SERIES",
        "PATH",
        "PYTHON",
        "RESOLVED_OPENWRT_REF",
        "WORKDIR",
    }
)
RESERVED_PREFIXES = ("ACTIONS_", "GITHUB_", "RUNNER_")


class BuildOptionError(ValueError):
    """A build option is malformed or attempts to alter protected execution state."""


def is_reserved(name: str) -> bool:
    return name in RESERVED_NAMES or name.startswith(RESERVED_PREFIXES)


def parse_build_options(raw: str | None) -> dict[str, str]:
    """Return a deterministic key/value mapping from shell-quoted assignments."""
    if not raw:
        return {}
    try:
        tokens = shlex.split(raw, posix=True)
    except ValueError as exc:
        raise BuildOptionError(f"invalid build_options quoting: {exc}") from exc

    options: dict[str, str] = {}
    for token in tokens:
        if "=" not in token:
            raise BuildOptionError(f"build option must use KEY=value: {token!r}")
        name, value = token.split("=", 1)
        if not NAME_RE.fullmatch(name):
            raise BuildOptionError(f"invalid build option name: {name!r}")
        if is_reserved(name):
            raise BuildOptionError(f"build option is reserved: {name}")
        if any(ord(char) < 32 or ord(char) == 127 for char in value):
            raise BuildOptionError(f"build option contains a control character: {name}")
        if name in options:
            raise BuildOptionError(f"build option is repeated: {name}")
        options[name] = value
    return options


def redact_options(options: Mapping[str, str]) -> dict[str, str]:
    """Preserve option names while redacting values that may contain credentials."""
    return {
        name: "***REDACTED***" if SENSITIVE_RE.search(name) else value
        for name, value in options.items()
    }
