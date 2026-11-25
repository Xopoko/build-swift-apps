import json
import plistlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile


SCRIPT = (
    Path(__file__).resolve().parents[2]
    / "skills/appstore-release-director/scripts/appstore_preflight.py"
)


class AppStorePreflightTest(unittest.TestCase):
    def test_ipa_must_match_archived_build(self):
        identity = {
            "CFBundleIdentifier": "com.example.app",
            "CFBundleShortVersionString": "1.0",
            "CFBundleVersion": "42",
        }
        with tempfile.TemporaryDirectory() as temporary:
            plist = Path(temporary) / "Info.plist"
            plist.write_bytes(plistlib.dumps(identity))
            ipa = Path(temporary) / "App.ipa"

            for build, should_pass in [(None, False), ("41", False), ("42", True)]:
                with self.subTest(exported_build=build):
                    if build is None:
                        ipa.write_text("not a ZIP file", encoding="utf-8")
                    else:
                        with ZipFile(ipa, "w") as archive:
                            exported = {**identity, "CFBundleVersion": build}
                            archive.writestr("Payload/App.app/Info.plist", plistlib.dumps(exported))
                    result = subprocess.run(
                        [sys.executable, str(SCRIPT), "--app-plist", str(plist), "--ipa", str(ipa)],
                        capture_output=True,
                        text=True,
                    )
                    self.assertEqual(result.returncode, 0 if should_pass else 1, result.stderr)
                    self.assertEqual(json.loads(result.stdout)["ok"], should_pass)


if __name__ == "__main__":
    unittest.main()
