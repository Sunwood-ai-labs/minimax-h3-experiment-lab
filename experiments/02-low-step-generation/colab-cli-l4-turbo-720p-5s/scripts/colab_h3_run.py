"""Submit the tracked H3 workflow to ComfyUI and save a run report."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import time
import urllib.error
import urllib.request
import uuid
from datetime import datetime, timezone
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", default="/content/colab_h3_turbo_l4_1280x704_api.json")
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=704)
    parser.add_argument("--frames", type=int, default=124)
    parser.add_argument("--seed", type=int, default=2026081001)
    parser.add_argument("--steps", type=int, default=8)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--output-prefix", default="video/colab_l4_turbo_720p_5s_1280x704")
    return parser.parse_args()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(32 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def node_by_type(graph: dict, class_type: str) -> dict:
    for node in graph.values():
        if isinstance(node, dict) and node.get("class_type") == class_type:
            return node
    raise KeyError(f"workflow node not found: {class_type}")


def post_prompt(base: str, graph: dict) -> str:
    payload = json.dumps({"prompt": graph, "client_id": str(uuid.uuid4())}).encode("utf-8")
    request = urllib.request.Request(
        f"{base}/prompt",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return str(json.load(response)["prompt_id"])


def get_history(base: str, prompt_id: str) -> dict | None:
    try:
        with urllib.request.urlopen(f"{base}/history/{prompt_id}", timeout=30) as response:
            return json.load(response).get(prompt_id)
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None


args = parse_args()
base = "http://127.0.0.1:8188"
workflow_path = Path(args.workflow)
graph = json.loads(workflow_path.read_text(encoding="utf-8"))
video_node = node_by_type(graph, "MiniMaxH3ImageToVideo")
video_node["inputs"].update({"width": args.width, "height": args.height, "length": args.frames})
node_by_type(graph, "RandomNoise")["inputs"]["noise_seed"] = args.seed
node_by_type(graph, "BasicScheduler")["inputs"]["steps"] = args.steps
node_by_type(graph, "SaveVideo")["inputs"]["filename_prefix"] = args.output_prefix

output_root = Path("/content/ComfyUI/output")
before = {path: path.stat().st_mtime_ns for path in output_root.rglob("*") if path.is_file()}
started_utc = datetime.now(timezone.utc)
started_monotonic = time.perf_counter()
prompt_id = post_prompt(base, graph)
print({"prompt_id": prompt_id, "submitted": True, "resolution": f"{args.width}x{args.height}", "frames": args.frames, "fps": 24, "steps": args.steps, "seed": args.seed}, flush=True)

deadline = time.time() + args.timeout
history = None
last_status = None
while time.time() < deadline:
    time.sleep(5)
    history = get_history(base, prompt_id)
    if not history:
        continue
    status = history.get("status", {})
    status_str = status.get("status_str")
    if status_str != last_status:
        print({"status": status_str, "completed": status.get("completed")}, flush=True)
        last_status = status_str
    if status_str in {"success", "error"}:
        break
else:
    raise TimeoutError(f"timed out waiting for {prompt_id}")

ended_utc = datetime.now(timezone.utc)
new_files = [
    path for path in output_root.rglob("*")
    if path.is_file() and (path not in before or path.stat().st_mtime_ns > before[path])
]
mp4s = sorted([path for path in new_files if path.suffix.lower() == ".mp4"], key=lambda path: path.stat().st_mtime_ns, reverse=True)
raw_output = Path("/content/colab_l4_turbo_720p_5s_raw.mp4")
if history and history.get("status", {}).get("status_str") == "success" and mp4s:
    shutil.copy2(mp4s[0], raw_output)

report = {
    "prompt_id": prompt_id,
    "status": None if history is None else history.get("status", {}).get("status_str"),
    "started_utc": started_utc.isoformat(),
    "ended_utc": ended_utc.isoformat(),
    "wall_seconds": round(time.perf_counter() - started_monotonic, 3),
    "conditions": {
        "resolution": f"{args.width}x{args.height}",
        "frames": args.frames,
        "fps": 24,
        "steps": args.steps,
        "seed": args.seed,
        "workflow": str(workflow_path),
        "turbo_lora": "minimax_h3_turbo_4step_ema_ckpt850.safetensors",
    },
    "outputs": [{"path": str(path), "bytes": path.stat().st_size, "sha256": sha256(path)} for path in new_files],
    "raw_download": {
        "path": str(raw_output),
        "bytes": raw_output.stat().st_size if raw_output.exists() else None,
        "sha256": sha256(raw_output) if raw_output.exists() else None,
    },
}
Path("/content/colab_l4_run_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2), flush=True)

if report["status"] != "success":
    raise RuntimeError(json.dumps(history, ensure_ascii=False)[:12000])
if not raw_output.exists():
    raise RuntimeError("ComfyUI succeeded but no MP4 output was found")
