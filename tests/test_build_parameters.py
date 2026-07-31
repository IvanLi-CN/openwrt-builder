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

    def test_invalid_build_options_are_rejected_before_build(self):
        result = subprocess.run(
            [str(BUILD_SCRIPT), "lite", "x86_64"],
            env={**os.environ, "BUILD_OPTIONS": "NO_APPS"},
            text=True,
            capture_output=True,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("invalid build_options: build option must use KEY=value", result.stderr)

    def test_workflow_exposes_and_uses_lan(self):
        workflow = WORKFLOW.read_text()

        self.assertIn("      lan:\n", workflow)
        self.assertIn("        required: false\n", workflow)
        self.assertIn("        default: 192.168.31.1\n", workflow)
        self.assertIn('          LAN: ${{ inputs.lan }}', workflow)
        self.assertNotIn('export LAN="${{ inputs.lan }}"', workflow)

    def test_workflow_serializes_auto_tag_creation_and_has_collision_suffix(self):
        workflow = WORKFLOW.read_text()

        self.assertIn("concurrency:\n", workflow)
        self.assertIn("cancel-in-progress: ${{ github.event_name == 'pull_request' }}", workflow)
        self.assertIn("AUTO_RELEASE_TAG=true", workflow)
        self.assertIn('RELEASE_TAG="${RELEASE_TAG}-r${GITHUB_RUN_NUMBER}"', workflow)

    def test_release_permissions_are_isolated_from_pr_builds(self):
        workflow = WORKFLOW.read_text()
        build_job, release_job = workflow.split("  release:\n", 1)

        self.assertIn("permissions:\n  contents: read", workflow)
        self.assertNotIn("contents: write", build_job)
        self.assertIn("permissions:\n      contents: write", release_job)
        self.assertNotIn("Publish release", build_job)


if __name__ == "__main__":
    unittest.main()
