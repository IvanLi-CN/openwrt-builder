import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECK = ROOT / "scripts" / "check-package-set.py"


class PackageSetTest(unittest.TestCase):
    def test_all_supported_profile_combinations_are_consistent(self):
        for version in ("lite", "server"):
            for no_apps in (False, True):
                with self.subTest(version=version, no_apps=no_apps):
                    command = [sys.executable, str(CHECK), "--version", version, "--device", "x86_64"]
                    if no_apps:
                        command.append("--no-apps")
                    subprocess.run(command, check=True, text=True, capture_output=True)
