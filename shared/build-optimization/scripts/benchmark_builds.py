#!/usr/bin/env python3

import argparse
import json
import os
import platform
import re
import shlex
import shutil
import statistics
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark Xcode clean and incremental builds.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--workspace", help="Path to the .xcworkspace file")
    group.add_argument("--project", help="Path to the .xcodeproj file")
    parser.add_argument("--scheme", required=True, help="Scheme to build")
    parser.add_argument("--configuration", default="Debug", help="Build configuration")
    parser.add_argument("--destination", help="xcodebuild destination string")
    parser.add_argument("--derived-data-path", help="DerivedData path override")
    parser.add_argument("--output-dir", default=".build-benchmark", help="Output directory for artifacts")
    parser.add_argument("--repeats", type=int, default=3, help="Measured runs per build type")
    parser.add_argument("--skip-warmup", action="store_true", help="Skip the validation build")
    parser.add_argument(
        "--touch-file",
        help="Path to a source file to touch before each incremental build. "
        "When provided, measures a real edit-rebuild loop instead of a zero-change build.",
    )
    parser.add_argument(
        "--no-cached-clean",
        action="store_true",
        help="Skip cached clean builds even when COMPILATION_CACHE_ENABLE_CACHING is detected.",
    )
    parser.add_argument(
        "--extra-arg",
        action="append",
        default=[],
        help="Additional xcodebuild argument to append. Can be passed multiple times.",
    )
    args = parser.parse_args()
    if args.repeats < 1:
        parser.error("--repeats must be at least 1")
    if args.touch_file and not Path(args.touch_file).is_file():
        parser.error(f"--touch-file must name an existing file: {args.touch_file}")
    return args


def command_base(args: argparse.Namespace, derived_data_path: Optional[str]) -> List[str]:
    command = ["xcodebuild"]
    if args.workspace:
        command.extend(["-workspace", args.workspace])
    if args.project:
        command.extend(["-project", args.project])
    command.extend(["-scheme", args.scheme, "-configuration", args.configuration])
    if args.destination:
        command.extend(["-destination", args.destination])
    if derived_data_path:
        command.extend(["-derivedDataPath", derived_data_path])
    command.extend(args.extra_arg)
    return command


_TIMING_ROW = re.compile(
    r"(?P<name>.+?)\s*(?:\((?P<tasks>\d+) tasks?\))?\s*"
    r"\|\s*(?P<seconds>\d+(?:\.\d+)?) seconds?"
)


def parse_timing_summary(output: str) -> List[Dict]:
    categories: Dict[str, Dict] = {}
    in_summary = False
    for raw_line in output.splitlines():
        line = raw_line.strip()
        if line == "Build Timing Summary":
            in_summary = True
        elif line.startswith("** BUILD"):
            in_summary = False
        elif not in_summary:
            continue
        match = _TIMING_ROW.fullmatch(line)
        if match:
            name = match["name"].strip()
            category = categories.setdefault(name, {"name": name, "seconds": 0.0})
            category["seconds"] = round(category["seconds"] + float(match["seconds"]), 3)
            if match["tasks"]:
                category["task_count"] = category.get("task_count", 0) + int(match["tasks"])
    return sorted(categories.values(), key=lambda category: category["seconds"], reverse=True)


def run_command(command: List[str]) -> subprocess.CompletedProcess:
    return subprocess.run(command, capture_output=True, text=True)


def stats_for(runs: List[Dict[str, object]]) -> Dict[str, Optional[float]]:
    durations = [run["duration_seconds"] for run in runs if run.get("success")]
    return {
        "count": len(durations),
        "min_seconds": round(min(durations), 3) if durations else None,
        "max_seconds": round(max(durations), 3) if durations else None,
        "median_seconds": round(statistics.median(durations), 3) if durations else None,
        "average_seconds": round(statistics.fmean(durations), 3) if durations else None,
    }


def xcode_version() -> str:
    result = run_command(["xcodebuild", "-version"])
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def measure_build(
    base_command: List[str],
    artifact_stem: str,
    output_dir: Path,
    build_type: str,
    run_index: int,
) -> Dict[str, object]:
    build_command = [*base_command, "build", "-showBuildTimingSummary"]
    started = time.perf_counter()
    result = run_command(build_command)
    elapsed = round(time.perf_counter() - started, 3)
    log_path = output_dir / f"{artifact_stem}-{build_type}-{run_index}.log"
    log_path.write_text(result.stdout + result.stderr)
    return {
        "id": f"{build_type}-{run_index}",
        "build_type": build_type,
        "duration_seconds": elapsed,
        "success": result.returncode == 0,
        "exit_code": result.returncode,
        "command": shlex.join(build_command),
        "raw_log_path": str(log_path),
        "timing_summary_categories": parse_timing_summary(result.stdout + result.stderr),
    }


def main() -> int:
    args = parse_args()
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    artifact_stem = f"{timestamp}-{args.scheme.replace(' ', '-').lower()}"
    base_command = command_base(args, args.derived_data_path)

    if not args.skip_warmup:
        warmup = run_command([*base_command, "build"])
        if warmup.returncode != 0:
            sys.stderr.write(warmup.stdout + warmup.stderr)
            return warmup.returncode

    runs: Dict[str, list] = {"clean": [], "incremental": []}
    exit_code = 0

    for index in range(1, args.repeats + 1):
        clean_result = run_command([*base_command, "clean"])
        clean_log_path = output_dir / f"{artifact_stem}-clean-prep-{index}.log"
        clean_log_path.write_text(clean_result.stdout + clean_result.stderr)
        if clean_result.returncode != 0:
            sys.stderr.write(f"Clean failed. See {clean_log_path}\n")
            exit_code = clean_result.returncode
            break
        run = measure_build(base_command, artifact_stem, output_dir, "clean", index)
        runs["clean"].append(run)
        if not run["success"]:
            exit_code = run["exit_code"]
            break

    incremental_label = "incremental" if args.touch_file else "zero-change"
    if not exit_code:
        for index in range(1, args.repeats + 1):
            if args.touch_file:
                Path(args.touch_file).touch()
            run = measure_build(base_command, artifact_stem, output_dir, incremental_label, index)
            runs["incremental"].append(run)
            if not run["success"]:
                exit_code = run["exit_code"]
                break

    if not exit_code and not args.no_cached_clean:
        settings = run_command([*base_command, "-showBuildSettings"])
        if settings.returncode != 0:
            sys.stderr.write("Could not determine whether compilation caching is enabled.\n")
            sys.stderr.write(settings.stdout + settings.stderr)
            exit_code = settings.returncode
        elif re.search(r"^\s*COMPILATION_CACHE_ENABLE_CACHING\s*=\s*YES\s*$", settings.stdout, re.MULTILINE):
            runs["cached_clean"] = []
            with tempfile.TemporaryDirectory(prefix="xcode-bench-") as temp_dir:
                derived_data = Path(temp_dir) / "DerivedData"
                cache_path = Path(temp_dir) / "CompilationCache.noindex"
                cached_command = [
                    *command_base(args, str(derived_data)),
                    f"COMPILATION_CACHE_CAS_PATH={cache_path}",
                ]
                warmup = run_command([*cached_command, "build"])
                if warmup.returncode != 0:
                    sys.stderr.write("Cached-clean warm-up failed.\n")
                    sys.stderr.write(warmup.stdout + warmup.stderr)
                    exit_code = warmup.returncode
                else:
                    for index in range(1, args.repeats + 1):
                        if derived_data.exists():
                            shutil.rmtree(derived_data)
                        run = measure_build(cached_command, artifact_stem, output_dir, "cached-clean", index)
                        runs["cached_clean"].append(run)
                        if not run["success"]:
                            exit_code = run["exit_code"]
                            break

    summary = {phase: stats_for(phase_runs) for phase, phase_runs in runs.items()}
    artifact = {
        "schema_version": "1.2.0" if "cached_clean" in runs else "1.1.0",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "exit_code": exit_code,
        "build": {
            "entrypoint": "workspace" if args.workspace else "project",
            "path": args.workspace or args.project,
            "scheme": args.scheme,
            "configuration": args.configuration,
            "destination": args.destination or "",
            "derived_data_path": args.derived_data_path or "",
            "command": shlex.join(base_command),
        },
        "environment": {
            "host": platform.node(),
            "macos_version": platform.platform(),
            "xcode_version": xcode_version(),
            "cwd": os.getcwd(),
        },
        "runs": runs,
        "summary": summary,
        "notes": [f"touch-file: {args.touch_file}"] if args.touch_file else [],
    }

    artifact_path = output_dir / f"{artifact_stem}.json"
    artifact_path.write_text(json.dumps(artifact, indent=2) + "\n")

    print(f"Saved benchmark artifact: {artifact_path}")
    if exit_code:
        for phase_runs in runs.values():
            for run in phase_runs:
                if not run["success"]:
                    sys.stderr.write(f"{run['id']} failed. See {run['raw_log_path']}\n")
        return exit_code

    labels = {"clean": "Clean", "incremental": incremental_label.capitalize(), "cached_clean": "Cached clean"}
    for phase, stats in summary.items():
        print(f"{labels[phase]} median: {stats['median_seconds']}s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
