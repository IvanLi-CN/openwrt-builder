import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-package-set.py"


class PackageSetTest(unittest.TestCase):
    def test_x86_compat_wrapper_does_not_use_source_package_defaults(self):
        wrapper = (ROOT / "packages" / "kmod-x86-compat" / "Makefile").read_text()

        self.assertIn("PKG_NAME:=kmod-x86-compat", wrapper)
        self.assertIn("define Build/Compile\nendef", wrapper)

    def test_all_supported_profile_combinations_are_consistent(self):
        for version in ("lite", "server"):
            for no_apps in (False, True):
                with self.subTest(version=version, no_apps=no_apps):
                    command = [sys.executable, str(CHECK), "--version", version, "--device", "x86_64"]
                    if no_apps:
                        command.append("--no-apps")
                    subprocess.run(command, check=True, text=True, capture_output=True)

    def test_resolved_config_rejects_forbidden_settings(self):
        config = "\n".join(
            [
                "CONFIG_PACKAGE_luci=y",
                "CONFIG_PACKAGE_luci-theme-argon=y",
                "CONFIG_ALL_KMODS=y",
            ]
        )
        with tempfile.TemporaryDirectory() as directory:
            resolved_config = Path(directory) / ".config"
            resolved_config.write_text(config + "\n")
            result = subprocess.run(
                [
                    sys.executable,
                    str(CHECK),
                    "--version",
                    "lite",
                    "--device",
                    "x86_64",
                    "--no-apps",
                    "--resolved-config",
                    str(resolved_config),
                ],
                text=True,
                capture_output=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("forbidden configuration is enabled: CONFIG_ALL_KMODS=y", result.stderr)
