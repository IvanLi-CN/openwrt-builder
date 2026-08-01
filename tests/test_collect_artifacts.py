import hashlib
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COLLECT_ARTIFACTS = ROOT / "scripts" / "collect-artifacts.py"


class CollectArtifactsTest(unittest.TestCase):
    def test_collects_firmware_buildinfo_and_checksums(self):
        firmware_files = [
            "openwrt-x86-64-generic-ext4-combined.img.gz",
            "openwrt-x86-64-generic-squashfs-combined.img.gz",
            "openwrt-x86-64-generic-ext4-combined-efi.img.gz",
            "openwrt-x86-64-generic-squashfs-combined-efi.img.gz",
            "openwrt-x86-64-generic-generic-rootfs.tar.gz",
        ]

        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            openwrt = tmp_path / "openwrt"
            target = openwrt / "bin" / "targets" / "x86" / "64"
            target.mkdir(parents=True)
            for index, name in enumerate(firmware_files):
                (target / name).write_bytes(f"firmware-{index}".encode())
            for name in ("config.buildinfo", "feeds.buildinfo", "version.buildinfo"):
                (target / name).write_text(name)
            (target / "packages.manifest").write_text("package metadata")
            (openwrt / ".config").write_text("CONFIG_TARGET_x86=y\n")
            (openwrt / "openwrt-builder-metadata.json").write_text("{}\n")
            (openwrt / "openwrt-builder-components.json").write_text("{}\n")

            output = tmp_path / "artifacts"
            subprocess.run(
                [sys.executable, str(COLLECT_ARTIFACTS), str(openwrt), "x86_64", str(output)],
                check=True,
                text=True,
                capture_output=True,
            )

            self.assertEqual(sorted(path.name for path in output.iterdir() if path.is_file()), sorted([
                *firmware_files,
                "buildinfo.tar.gz",
                "sha256sums.txt",
            ]))

            with tarfile.open(output / "buildinfo.tar.gz", "r:gz") as archive:
                self.assertEqual(sorted(archive.getnames()), sorted([
                    "buildinfo",
                    "buildinfo/config.buildinfo",
                    "buildinfo/feeds.buildinfo",
                    "buildinfo/manifest.txt",
                    "buildinfo/final.config",
                    "buildinfo/openwrt-builder-components.json",
                    "buildinfo/openwrt-builder-metadata.json",
                    "buildinfo/version.buildinfo",
                ]))

            expected_payloads = sorted([*firmware_files, "buildinfo.tar.gz"])
            checksums = dict(
                line.split("  ", 1)
                for line in (output / "sha256sums.txt").read_text().splitlines()
            )
            self.assertEqual(sorted(checksums.values()), expected_payloads)
            for name in expected_payloads:
                self.assertEqual(
                    checksums[hashlib.sha256((output / name).read_bytes()).hexdigest()],
                    name,
                )


if __name__ == "__main__":
    unittest.main()
