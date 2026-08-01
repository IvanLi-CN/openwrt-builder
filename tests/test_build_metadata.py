import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_metadata import write_metadata


class BuildMetadataTest(unittest.TestCase):
    def test_metadata_redacts_options_and_release_tag_uses_resolved_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            metadata_path = Path(tmp) / "metadata.json"
            write_metadata(
                metadata_path,
                openwrt_repo="https://github.com/openwrt/openwrt.git",
                resolved_tag="v25.12.5",
                openwrt_commit="abc123",
                feeds_ref="openwrt-25.12",
                components=[],
                build_options={"BUILD_FAST": "y", "API_TOKEN": "hidden"},
            )
            metadata = json.loads(metadata_path.read_text())
            self.assertEqual(metadata["build_options"]["API_TOKEN"], "***REDACTED***")
            output = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "render-release-notes.py"),
                    "--metadata", str(metadata_path),
                    "--format", "tag",
                    "--flavor", "lite",
                    "--device", "x86_64",
                    "--timestamp", "20260726-1200",
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            self.assertEqual(output.stdout.strip(), "v25.12.5-lite-x86_64-20260726-1200")
