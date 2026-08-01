"""Resolve the highest stable OpenWrt tag in a supported release series."""

from __future__ import annotations

import re
from collections.abc import Iterable


def latest_stable_tag(refs: Iterable[str], series: str) -> str:
    pattern = re.compile(rf"^refs/tags/v{re.escape(series)}\.(\d+)$")
    candidates: list[tuple[int, str]] = []
    for ref in refs:
        match = pattern.fullmatch(ref.strip())
        if match:
            candidates.append((int(match.group(1)), f"v{series}.{match.group(1)}"))
    if not candidates:
        raise ValueError(f"no stable v{series}.x tag found")
    return max(candidates)[1]
