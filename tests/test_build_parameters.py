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
        self.assertIn("needs: [validate, build]", release_job)
        self.assertNotIn("Publish release", build_job)

    def test_build_maps_download_and_optional_compiler_cache(self):
        build_script = BUILD_SCRIPT.read_text()

        self.assertIn('DL_DIR=${DL_DIR:-$ROOT/dl}', build_script)
        self.assertIn('CCACHE_DIR=${CCACHE_DIR:-}', build_script)
        self.assertIn('CONFIG_DEVEL=y', build_script)
        self.assertIn('CONFIG_DOWNLOAD_FOLDER="$DL_DIR"', build_script)
        self.assertIn('if [[ -n "$CCACHE_DIR" ]]; then', build_script)
        self.assertIn('CONFIG_CCACHE=y', build_script)
        self.assertIn('CONFIG_CCACHE_DIR="$CCACHE_DIR"', build_script)

    def test_workflow_caches_only_x86_build_inputs_non_blockingly(self):
        workflow = WORKFLOW.read_text()

        self.assertIn('- name: Restore x86 build cache', workflow)
        self.assertIn('uses: actions/cache/restore@v4', workflow)
        self.assertIn('uses: actions/cache/save@v4', workflow)
        self.assertIn("if: ${{ env.BUILD_DEVICE == 'x86_64' }}", workflow)
        self.assertIn('continue-on-error: true', workflow)
        self.assertIn('openwrt-x86-cache-v2-${{ runner.os }}-x86_64-${{ env.BUILD_VERSION }}-', workflow)
        self.assertIn("hashFiles('config/components.lock.json', 'config/**', 'files/**', 'scripts/build.sh')", workflow)
        self.assertIn('${{ github.run_id }}-${{ github.run_attempt }}', workflow)
        self.assertIn('CCACHE_DIR=$GITHUB_WORKSPACE/.ccache', workflow)
        self.assertIn('CACHE_MATCHED_KEY: ${{ steps.x86-build-cache.outputs.cache-matched-key }}', workflow)
        self.assertIn('x86 build cache: exact hit', workflow)
        self.assertIn('x86 build cache: restored fallback', workflow)
        self.assertIn('x86 build cache: miss or unavailable', workflow)
        self.assertIn('"$ccache" --max-size=2G || true', workflow)
        self.assertIn('du -sh "$DL_DIR" "$CCACHE_DIR" 2>/dev/null || true', workflow)

        cache_section = workflow.split('- name: Restore x86 build cache', 1)[1].split(
            '- name: Install build dependencies', 1
        )[0]
        self.assertIn('dl', cache_section)
        self.assertIn('.ccache', cache_section)
        self.assertNotIn('nanopi-r4s', cache_section)
        self.assertNotIn('nanopi-r5s', cache_section)

        save_section = workflow.split('- name: Save x86 build cache', 1)[1].split(
            '- uses: actions/upload-artifact@v4', 1
        )[0]
        self.assertNotIn('cache-hit !=', save_section)


if __name__ == "__main__":
    unittest.main()
