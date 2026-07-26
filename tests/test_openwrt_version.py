import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from openwrt_version import latest_stable_tag


class OpenWrtVersionTest(unittest.TestCase):
    def test_selects_highest_stable_patch_and_ignores_prereleases(self):
        refs = [
            "refs/tags/v25.12.0-rc5",
            "refs/tags/v25.12.2",
            "refs/tags/v25.12.11",
            "refs/tags/v24.10.9",
            "refs/tags/v25.12.12-rc1",
        ]
        self.assertEqual(latest_stable_tag(refs, "25.12"), "v25.12.11")

    def test_requires_a_stable_tag(self):
        with self.assertRaisesRegex(ValueError, "no stable"):
            latest_stable_tag(["refs/tags/v25.12.0-rc1"], "25.12")
