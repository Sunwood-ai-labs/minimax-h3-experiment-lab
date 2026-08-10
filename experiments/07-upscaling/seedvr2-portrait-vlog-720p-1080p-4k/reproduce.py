#!/usr/bin/env python3
"""Reproduce the 7-second MiniMax-H3 + SeedVR2 video comparison.

Requirements on the host: Python 3.10+, ffmpeg, and a running ComfyUI API.
The workflow JSON files and the input image are kept next to this script.
"""

from __future__ import annotations

import argparse
import copy
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from uuid import uuid4


EXPERIMENT_DIR = Path(__file__).resolve().parent
REPO_ROOT = EXPERIMENT_DIR.parents[3]
RUNTIME_INPUT = REPO_ROOT / "runtime" / "4090" / "input"
RUNTIME_OUTPUT = REPO_ROOT / "runtime" / "4090" / "output"
WORKFLOW_DIR = EXPERIMENT_DIR / "workflows"
RUN_DIR = EXPERIMENT_DIR / "runs"

TOTAL_SECONDS = 7.291667
SEGMENT_SECONDS = 0.75
SEGMENT_COUNT = 10
START_IMAGE = EXPERIMENT_DIR / "inputs" / "seedvr2_portrait_vlog_h3_start_704x1280.png"
H3_WORKFLOW = WORKFLOW_DIR / "h3_portrait_vlog_i2v_7s_704x1280_api.json"
BASELINE_NAME = "seedvr2_portrait_vlog_h3_i2v_7s_720p_baseline.mp4"
BASELINE_PATH = RUNTIME_OUTPUT / "video" / BASELINE_NAME


def fail(message: str) -> "NoReturn":
    raise RuntimeError(message)


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8-sig") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        fail(f"Expected an object workflow: {path}")
    return value


def save_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(value, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def api_json(api_url: str, endpoint: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    url = api_url.rstrip("/") + endpoint
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, method="POST" if data is not None else "GET")
    if data is not None:
        request.add_header("Content-Type", "application/json")
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))


def patch_workflow(
    graph: dict[str, Any],
    *,
    input_name: str | None = None,
    baseline_name: str | None = None,
    start: float | None = None,
    duration: float | None = None,
    output_prefix: str | None = None,
) -> dict[str, Any]:
    graph = copy.deepcopy(graph)
    for node in graph.values():
        if not isinstance(node, dict):
            continue
        class_type = node.get("class_type")
        inputs = node.setdefault("inputs", {})
        if class_type == "LoadImage" and input_name is not None:
            inputs["image"] = input_name
        elif class_type == "LoadVideo" and baseline_name is not None:
            inputs["file"] = baseline_name
        elif class_type == "Video Slice":
            if start is not None:
                inputs["start_time"] = start
            if duration is not None:
                inputs["duration"] = duration
        elif class_type == "SaveVideo" and output_prefix is not None:
            inputs["filename_prefix"] = output_prefix
    return graph


def output_candidates(prefix: str) -> list[Path]:
    output_dir = RUNTIME_OUTPUT / Path(prefix).parent
    stem = Path(prefix).name
    if not output_dir.exists():
        return []
    return sorted(output_dir.glob(stem + "*.mp4"), key=lambda p: p.stat().st_mtime, reverse=True)


def wait_for_output(prefix: str, started: float, timeout: int) -> Path:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for candidate in output_candidates(prefix):
            if candidate.stat().st_mtime >= started - 2:
                return candidate
        time.sleep(1)
    fail(f"ComfyUI output was not found for prefix: {prefix}")


def run_comfy_workflow(
    api_url: str,
    graph: dict[str, Any],
    output_prefix: str,
    *,
    timeout: int,
    label: str,
) -> tuple[Path, float, str]:
    started = time.monotonic()
    try:
        response = api_json(api_url, "/prompt", {"prompt": graph, "client_id": str(uuid4())})
    except (HTTPError, URLError) as exc:
        fail(f"Could not submit {label} to {api_url}: {exc}")
    prompt_id = response.get("prompt_id")
    if not prompt_id:
        fail(f"ComfyUI did not return a prompt_id for {label}: {response}")
    print(f"[{label}] prompt_id={prompt_id}", flush=True)

    deadline = time.monotonic() + timeout
    final_status: dict[str, Any] | None = None
    while time.monotonic() < deadline:
        time.sleep(3)
        try:
            history = api_json(api_url, f"/history/{prompt_id}")
        except (HTTPError, URLError):
            continue
        item = history.get(prompt_id)
        if not item:
            continue
        status = item.get("status", {})
        status_name = status.get("status_str", "unknown")
        print(f"[{label}] status={status_name}", flush=True)
        if status_name in {"success", "error"}:
            final_status = item
            break
    if final_status is None:
        fail(f"Timed out waiting for {label} ({timeout}s)")
    status_name = final_status.get("status", {}).get("status_str")
    if status_name != "success":
        messages = final_status.get("status", {}).get("messages", [])
        fail(f"ComfyUI failed {label}: {messages}")
    output = wait_for_output(output_prefix, started, timeout)
    return output, round(time.monotonic() - started, 3), str(prompt_id)


def run_command(args: list[str], label: str) -> None:
    print(f"[{label}] {' '.join(args)}", flush=True)
    completed = subprocess.run(args, check=False)
    if completed.returncode != 0:
        fail(f"{label} failed with exit code {completed.returncode}")


def require_command(name: str) -> None:
    if shutil.which(name) is None:
        fail(f"Required command not found on PATH: {name}")


def prepare_baseline(source: Path) -> Path:
    BASELINE_PATH.parent.mkdir(parents=True, exist_ok=True)
    run_command(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-map",
            "0:v:0",
            "-map",
            "0:a?",
            "-vf",
            "scale=720:1280:flags=lanczos",
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "copy",
            "-movflags",
            "+faststart",
            str(BASELINE_PATH),
        ],
        "baseline",
    )
    shutil.copy2(BASELINE_PATH, RUNTIME_INPUT / BASELINE_NAME)
    return BASELINE_PATH


def merge_segments(target: str, segments: list[Path]) -> Path:
    output = RUNTIME_OUTPUT / "video" / f"seedvr2_portrait_vlog_7s_{target}.mp4"
    filter_inputs = "".join(f"[{i}:v:0][{i}:a:0]" for i in range(len(segments)))
    filter_complex = filter_inputs + f"concat=n={len(segments)}:v=1:a=1[v][a]"
    command = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error"]
    for segment in segments:
        command.extend(["-i", str(segment)])
    command.extend(
        [
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-map",
            "[a]",
            "-c:v",
            "libx264",
            "-crf",
            "18",
            "-preset",
            "medium",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-movflags",
            "+faststart",
            str(output),
        ]
    )
    run_command(command, f"merge-{target}")
    return output


def make_tile(outputs: dict[str, Path]) -> Path:
    output = RUNTIME_OUTPUT / "video" / "seedvr2_portrait_vlog_video_comparison_seedvr2_7s.mp4"
    filter_complex = (
        "[0:v]setpts=PTS-STARTPTS,scale=360:640:flags=lanczos[v0];"
        "[1:v]setpts=PTS-STARTPTS,scale=360:640:flags=lanczos[v1];"
        "[2:v]setpts=PTS-STARTPTS,scale=360:640:flags=lanczos[v2];"
        "[v0][v1][v2]hstack=inputs=3:shortest=1[tiles];"
        "[tiles]pad=1080:720:0:80:color=0x080b12[v]"
    )
    run_command(
        [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(outputs["720p"]),
            "-i",
            str(outputs["1080p"]),
            "-i",
            str(outputs["4k"]),
            "-filter_complex",
            filter_complex,
            "-map",
            "[v]",
            "-an",
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            "-pix_fmt",
            "yuv420p",
            "-movflags",
            "+faststart",
            str(output),
        ],
        "tile",
    )
    return output


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--api-url", default="http://127.0.0.1:8188")
    parser.add_argument("--target", choices=("1080p", "4k", "both"), default="both")
    parser.add_argument("--start-image", type=Path, default=START_IMAGE)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--skip-h3", action="store_true")
    parser.add_argument("--skip-baseline", action="store_true")
    parser.add_argument("--tile", action="store_true", help="Create a synchronized no-audio comparison tile")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    require_command("ffmpeg")
    RUNTIME_INPUT.mkdir(parents=True, exist_ok=True)
    (RUNTIME_OUTPUT / "video").mkdir(parents=True, exist_ok=True)
    start_image = args.start_image.resolve()
    if not start_image.is_file():
        fail(f"Start image not found: {start_image}")
    shutil.copy2(start_image, RUNTIME_INPUT / start_image.name)

    results: dict[str, Any] = {"api_url": args.api_url, "target": args.target, "started": time.strftime("%Y-%m-%dT%H:%M:%S%z")}
    if not args.skip_h3:
        graph = patch_workflow(load_json(H3_WORKFLOW), input_name=start_image.name, output_prefix="video/seedvr2_portrait_vlog_h3_i2v_7s_704x1280")
        h3_output, wall, prompt_id = run_comfy_workflow(
            args.api_url, graph, "video/seedvr2_portrait_vlog_h3_i2v_7s_704x1280", timeout=args.timeout, label="h3-i2v"
        )
        results["h3"] = {"output": str(h3_output), "wall_seconds": wall, "prompt_id": prompt_id}
    else:
        candidates = output_candidates("video/seedvr2_portrait_vlog_h3_i2v_7s_704x1280")
        if not candidates:
            fail("--skip-h3 was used but the H3 output is missing")
        h3_output = candidates[0]

    if not args.skip_baseline:
        prepare_baseline(h3_output)
    elif not BASELINE_PATH.is_file():
        fail("--skip-baseline was used but the baseline video is missing")
    else:
        shutil.copy2(BASELINE_PATH, RUNTIME_INPUT / BASELINE_NAME)

    targets = ("1080p", "4k") if args.target == "both" else (args.target,)
    merged: dict[str, Path] = {}
    for target in targets:
        workflow_path = WORKFLOW_DIR / f"seedvr2_portrait_vlog_7s_{target}_segment_api.json"
        if not workflow_path.is_file():
            fail(f"Workflow not found: {workflow_path}")
        seed = 2026081014 if target == "1080p" else 2026081015
        segments: list[Path] = []
        segment_results = []
        for index in range(SEGMENT_COUNT):
            start = round(index * SEGMENT_SECONDS, 6)
            duration = round(TOTAL_SECONDS - start, 6) if index == SEGMENT_COUNT - 1 else SEGMENT_SECONDS
            prefix = f"video/seedvr2_portrait_vlog_7s_seedvr2_{target}_seg{index:02d}"
            graph = patch_workflow(
                load_json(workflow_path),
                baseline_name=BASELINE_NAME,
                start=start,
                duration=duration,
                output_prefix=prefix,
            )
            # Keep the seed visible in the public runner even if a workflow is edited later.
            for node in graph.values():
                if isinstance(node, dict) and node.get("class_type") == "KSampler":
                    node.setdefault("inputs", {})["seed"] = seed
            output, wall, prompt_id = run_comfy_workflow(args.api_url, graph, prefix, timeout=args.timeout, label=f"{target}-seg{index:02d}")
            segments.append(output)
            segment_results.append({"segment": index, "start": start, "duration": duration, "output": str(output), "wall_seconds": wall, "prompt_id": prompt_id})
        merged_output = merge_segments(target, segments)
        merged[target] = merged_output
        results[target] = {"segments": segment_results, "merged": str(merged_output)}

    if args.tile:
        if set(merged) != {"1080p", "4k"}:
            fail("--tile requires --target both")
        results["tile"] = str(make_tile({"720p": BASELINE_PATH, **merged}))

    report = RUN_DIR / "public-reproduction-last-run.json"
    save_json(report, results)
    print(f"Reproduction report: {report}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
