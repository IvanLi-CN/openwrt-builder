import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_options import BuildOptionError, parse_build_options, redact_options


class BuildOptionsTest(unittest.TestCase):
    def test_parses_shell_quoted_assignments_without_execution(self):
        options = parse_build_options("BUILD_FAST=y LABEL='x86 release' LITERAL='$(not executed)'")
        self.assertEqual(options["BUILD_FAST"], "y")
        self.assertEqual(options["LABEL"], "x86 release")
        self.assertEqual(options["LITERAL"], "$(not executed)")

    def test_rejects_shell_fragments_and_protected_variables(self):
        for value in (
            "NO_APPS",
            "OPENWRT_REF=v25.12.5",
            "GITHUB_TOKEN=value",
            "GIT_CONFIG_COUNT=1",
            "GIT_CONFIG_KEY_0=url.https://untrusted.invalid.insteadOf",
            "BASH_ENV=/tmp/injected.sh",
            "MAKEFLAGS=--eval=$(shell touch /tmp/injected)",
            "LD_PRELOAD=/tmp/injected.so",
            "A=1 A=2",
        ):
            with self.subTest(value=value):
                with self.assertRaises(BuildOptionError):
                    parse_build_options(value)

    def test_redacts_sensitive_values(self):
        self.assertEqual(
            redact_options({"API_AUTH": "secret", "API_TOKEN": "secret", "LAN": "10.0.0.1"}),
            {
                "API_AUTH": "***REDACTED***",
                "API_TOKEN": "***REDACTED***",
                "LAN": "10.0.0.1",
            },
        )
