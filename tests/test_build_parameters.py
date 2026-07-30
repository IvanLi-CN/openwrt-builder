import os
import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BUILD_SCRIPT = ROOT / "scripts" / "build.sh"
WORKFLOW = ROOT / ".github" / "workflows" / "build-openwrt.yml"


class BuildParametersTest(unittest.TestCase):
    def test_default_lan_matches_pve_network(self):
        self.assertIn("LAN=${LAN:-192.168.31.1}", BUILD_SCRIPT.read_text())

    def test_invalid_lan_is_rejected_before_build(self):
        result = subprocess.run(
            [str(BUILD_SCRIPT), "lite", "x86_64"],
            env={**os.environ, "LAN": "999.168.31.1"},
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid LAN IPv4 address: 999.168.31.1", result.stderr)

    def test_workflow_exposes_and_uses_lan(self):
        workflow = WORKFLOW.read_text()

        self.assertIn("      lan:\n", workflow)
        self.assertIn("        default: 192.168.31.1\n", workflow)
        self.assertIn('          export LAN="${{ inputs.lan }}"', workflow)


if __name__ == "__main__":
    unittest.main()
