import json
import runpy
import subprocess
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch


BENCHMARK = Path(__file__).resolve().parents[2] / "shared/build-optimization/scripts/benchmark_builds.py"


class BuildBenchmarkTest(unittest.TestCase):
    def test_cached_build_failure_preserves_caller_derived_data_and_artifact(self):
        main = runpy.run_path(str(BENCHMARK))["main"]

        with TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            caller_data = root / "Caller DerivedData"
            caller_data.mkdir()
            sentinel = caller_data / "keep"
            sentinel.touch()
            output = root / "artifacts"
            args = [
                str(BENCHMARK), "--project", "Sample.xcodeproj", "--scheme", "Sample",
                "--derived-data-path", str(caller_data), "--output-dir", str(output),
                "--repeats", "1", "--skip-warmup",
            ]

            def run_xcode(command):
                if "-version" in command:
                    return subprocess.CompletedProcess(command, 0, "Xcode fixture", "")
                if "-showBuildSettings" in command:
                    return subprocess.CompletedProcess(command, 0, "COMPILATION_CACHE_ENABLE_CACHING = YES", "")
                derived_data = Path(command[command.index("-derivedDataPath") + 1])
                if derived_data != caller_data:
                    setting = next(arg for arg in command if arg.startswith("COMPILATION_CACHE_CAS_PATH="))
                    cache = Path(setting.split("=", 1)[1])
                    if "-showBuildTimingSummary" in command:
                        self.assertFalse(derived_data.exists())
                        self.assertTrue(cache.is_dir())
                        return subprocess.CompletedProcess(command, 65, "", "cached build failed")
                    derived_data.mkdir()
                    cache.mkdir()
                return subprocess.CompletedProcess(command, 0, "", "")

            with patch.object(sys, "argv", args), patch.dict(main.__globals__, run_command=run_xcode):
                with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                    self.assertEqual(main(), 65)

            self.assertTrue(sentinel.is_file())
            artifact = json.loads(next(output.glob("*.json")).read_text())
            self.assertEqual(artifact["exit_code"], 65)
            self.assertEqual(artifact["summary"]["incremental"]["count"], 1)
            self.assertIsNone(artifact["summary"]["cached_clean"]["median_seconds"])
            failed_run, = artifact["runs"]["cached_clean"]
            self.assertEqual(failed_run["exit_code"], 65)
            self.assertEqual(Path(failed_run["raw_log_path"]).read_text(), "cached build failed")


if __name__ == "__main__":
    unittest.main()
