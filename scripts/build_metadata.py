"""Build metadata helpers shared by artifact and release scripts."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from build_options import redact_options


def write_metadata(
    output: Path,
    *,
    openwrt_repo: str,
    resolved_tag: str,
    openwrt_commit: str,
    feeds_ref: str,
    components: list[dict[str, object]],
    build_options: Mapping[str, str],
) -> None:
    payload = {
        "build_options": redact_options(build_options),
        "components": components,
        "openwrt": {
            "commit": openwrt_commit,
            "feeds_ref": feeds_ref,
            "repo": openwrt_repo,
            "resolved_tag": resolved_tag,
        },
    }
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def load_metadata(path: Path) -> dict[str, object]:
    return json.loads(path.read_text())
