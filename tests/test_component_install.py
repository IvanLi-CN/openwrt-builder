import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("install_components", ROOT / "scripts" / "install-components.py")
INSTALL_COMPONENTS = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALL_COMPONENTS)


class ComponentInstallTest(unittest.TestCase):
    def test_rejects_two_components_targeting_the_same_directory(self):
        components = [
            {"name": "first", "repo": "local", "paths": ["packages/first"], "destination": "package/custom/first"},
            {"name": "second", "repo": "local", "paths": ["packages/second"], "destination": "package/custom/first"},
        ]
        with self.assertRaisesRegex(ValueError, "destination collision"):
            INSTALL_COMPONENTS.validate_destinations(components)

    def test_current_component_destinations_are_unique(self):
        import json

        components = json.loads((ROOT / "config" / "components.lock.json").read_text())["components"]
        INSTALL_COMPONENTS.validate_destinations(components)
