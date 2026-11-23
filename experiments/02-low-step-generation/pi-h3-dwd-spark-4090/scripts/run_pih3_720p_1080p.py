#!/usr/bin/env python3
"""Run 720p (1280x720) and 1080p (1920x1080) pi-H3 benchmarks on RTX 4090."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib import request

BASE_URL = "http://localhost:8195"
CONTAINER_NAME = "minimax-h3-pih3-4090"
GPU_UUID = "GPU-f877fbc1-9f24-bd97-3359-dd358eaa2caa"
OUTPUT_ROOT = Path(r"D:\Prj\minimax-h3-compose\runtime\pih3-4090\output")

RUN_MATRIX = [
    # 4-step adapter is currently warm from prior run
    ("720p_4step_warmup", "pih3_dwd_spark_sm89_720p_4step_api.json", 41, "video/pi-h3-4090/720p_4step_warmup", True),
    ("720p_4step_warm", "pih3_dwd_spark_sm89_720p_4step_api.json", 42, "video/pi-h3-4090/720p_4step_warm", True),
    ("1080p_upscaled_4step_warmup", "pih3_dwd_spark_sm89_1080p_upscaled_4step_api.json", 41, "video/pi-h3-4090/1080p_upscaled_4step_warmup", True),
    ("1080p_upscaled_4step_warm", "pih3_dwd_spark_sm89_1080p_upscaled_4step_api.json", 42, "video/pi-h3-4090/1080p_upscaled_4step_warm", True),
    # Switch to 2-step adapter
    ("720p_2step_warmup", "pih3_dwd_spark_sm89_720p_2step_api.json", 41, "video/pi-h3-4090/720p_2step_warmup", True),
    ("720p_2step_warm", "pih3_dwd_spark_sm89_720p_2step_api.json", 42, "video/pi-h3-4090/720p_2step_warm", True),
    ("1080p_upscaled_2step_warmup", "pih3_dwd_spark_sm89_1080p_upscaled_2step_api.json", 41, "video/pi-h3-4090/1080p_upscaled_2step_warmup", True),
    ("1080p_upscaled_2step_warm", "pih3_dwd_spark_sm89_1080p_upscaled_2step_api.json", 42, "video/pi-h3-4090/1080p_upscaled_2step_warm", True),
    # Native 1080p (1920x1088 -> 1920x1080) attempts (allow graceful failure if 24GB VRAM OOMs)
    ("1080p_native_2step", "pih3_dwd_spark_sm89_1080p_native_2step_api.json", 42, "video/pi-h3-4090/1080p_native_2step", False),
    ("1080p_native_4step", "pih3_dwd_spark_sm89_1080p_native_4step_api.json", 42, "video/pi-h3-4090/1080p_native_4step", False),
]


def http_json(url: str, payload: dict | None = None) -> dict:
    if payload is None:
        with request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(url, data=data, headers={"Content-Type": "application/json; charset=utf-8"})
    with request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().upper()


class GpuSampler:
    def __init__(self, gpu_id: str, interval: float = 0.5) -> None:
        self.gpu_id = gpu_id
        self.interval = interval
        self.samples: list[dict] = []
        self._stop = threading.Event()
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def start(self) -> None:
        self._thread.start()

    def stop(self) -> dict:
        self._stop.set()
        self._thread.join(timeout=5)
        if not self.samples:
            return {}
        return {
            "sample_count": len(self.samples),
            "peak_vram_mib": max(s["memory_used_mib"] for s in self.samples),
            "min_vram_mib": min(s["memory_used_mib"] for s in self.samples),
            "vram_total_mib": self.samples[0]["memory_total_mib"],
            "peak_gpu_util_pct": max(s["util_gpu_pct"] for s in self.samples),
            "avg_gpu_util_pct": round(sum(s["util_gpu_pct"] for s in self.samples) / len(self.samples), 1),
            "peak_power_w": round(max(s["power_draw_w"] for s in self.samples), 2),
            "avg_power_w": round(sum(s["power_draw_w"] for s in self.samples) / len(self.samples), 2),
            "peak_temp_c": max(s["temp_c"] for s in self.samples),
        }

    def _loop(self) -> None:
        cmd = [
            "nvidia-smi",
            f"--id={self.gpu_id}",
            "--query-gpu=memory.used,memory.total,utilization.gpu,utilization.memory,power.draw,temperature.gpu",
            "--format=csv,noheader,nounits",
        ]
        while not self._stop.is_set():
            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=3, check=True)
                parts = [p.strip() for p in res.stdout.strip().splitlines()[0].split(",")]
                if len(parts) >= 6:
                    self.samples.append({
                        "t": round(time.time(), 3),
                        "memory_used_mib": float(parts[0]),
                        "memory_total_mib": float(parts[1]),
                        "util_gpu_pct": float(parts[2]),
                        "util_mem_pct": float(parts[3]),
                        "power_draw_w": float(parts[4]),
                        "temp_c": float(parts[5]),
                    })
            except Exception:
                pass
            self._stop.wait(self.interval)


def get_container_logs_since(since_iso: str) -> str:
    res = subprocess.run(
        ["docker", "logs", "--since", since_iso, CONTAINER_NAME],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=15,
    )
    return (res.stdout or "") + "\n" + (res.stderr or "")


def parse_history_messages(item: dict) -> dict:
    messages = item.get("status", {}).get("messages", [])
    ts_start = None
    ts_end = None
    cached_nodes: list[str] = []
    exec_error = None
    for msg_type, msg_data in messages:
        if msg_type == "execution_start":
            ts_start = msg_data.get("timestamp")
        elif msg_type in ("execution_success", "execution_error"):
            ts_end = msg_data.get("timestamp")
            if msg_type == "execution_error":
                exec_error = msg_data
        elif msg_type == "execution_cached":
            cached_nodes = list(msg_data.get("nodes", []))
    comfy_s = None
    if ts_start is not None and ts_end is not None:
        comfy_s = round((ts_end - ts_start) / 1000.0, 3)
    return {
        "comfy_execution_s": comfy_s,
        "cached_nodes": cached_nodes,
        "execution_error": exec_error,
    }


def main() -> int:
    exp_dir = Path(__file__).resolve().parent.parent
    wf_dir = exp_dir / "workflows"
    runs_dir = exp_dir / "runs"
    runs_dir.mkdir(parents=True, exist_ok=True)
    out_json = runs_dir / "benchmark_720p_1080p_results.json"

    stats = http_json(f"{BASE_URL}/system_stats")
    print("Connected to ComfyUI:", stats.get("system", {}).get("comfyui_version"), flush=True)

    results: dict = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "runs": [],
    }

    native_2step_failed = False
    for run_id, wf_file, seed, prefix, fatal in RUN_MATRIX:
        if run_id == "1080p_native_4step" and native_2step_failed:
            print(f"[{run_id}] skipped because 1080p_native_2step failed.", flush=True)
            continue

        graph = json.loads((wf_dir / wf_file).read_text(encoding="utf-8"))
        graph["12"]["inputs"]["noise_seed"] = seed
        graph["17"]["inputs"]["filename_prefix"] = prefix

        since_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        sampler = GpuSampler(GPU_UUID, interval=0.5)
        sampler.start()
        t0 = time.perf_counter()

        resp = http_json(f"{BASE_URL}/prompt", {"prompt": graph, "client_id": str(uuid.uuid4())})
        prompt_id = resp["prompt_id"]
        print(f"[{run_id}] queued prompt_id={prompt_id} seed={seed} ...", flush=True)

        history_item = None
        deadline = time.time() + 1800
        while time.time() < deadline:
            time.sleep(0.5)
            try:
                hist = http_json(f"{BASE_URL}/history/{prompt_id}")
            except Exception:
                continue
            if prompt_id in hist:
                history_item = hist[prompt_id]
                status_str = history_item.get("status", {}).get("status_str")
                if status_str in ("success", "error"):
                    break
        wall_s = round(time.perf_counter() - t0, 3)
        gpu_stats = sampler.stop()
        logs = get_container_logs_since(since_iso)

        if history_item is None:
            raise RuntimeError(f"Timeout waiting for {run_id} ({prompt_id})")

        status_str = history_item.get("status", {}).get("status_str")
        parsed = parse_history_messages(history_item)
        prompt_exec_match = re.findall(r"Prompt executed in ([0-9.]+) seconds", logs)
        comfy_logged_s = float(prompt_exec_match[-1]) if prompt_exec_match else None

        output_videos = []
        outputs = history_item.get("outputs", {}).get("17", {})
        for key in ("images", "videos", "gifs"):
            for entry in outputs.get(key, []):
                sub = entry.get("subfolder", "")
                fn = entry.get("filename", "")
                if not fn:
                    continue
                local_path = OUTPUT_ROOT / sub / fn if sub else OUTPUT_ROOT / fn
                info = {
                    "filename": fn,
                    "subfolder": sub,
                    "relative_path": str(Path(sub) / fn if sub else fn).replace("\\", "/"),
                    "local_path": str(local_path),
                    "exists": local_path.is_file(),
                }
                if local_path.is_file():
                    info["bytes"] = local_path.stat().st_size
                    info["sha256"] = sha256_file(local_path)
                output_videos.append(info)

        run_record = {
            "run_id": run_id,
            "workflow_file": wf_file,
            "workflow_sha256": sha256_file(wf_dir / wf_file),
            "prompt_id": prompt_id,
            "seed": seed,
            "gen_width": graph["6"]["inputs"]["width"],
            "gen_height": graph["6"]["inputs"]["height"],
            "out_width": graph["18"]["inputs"]["width"],
            "out_height": graph["18"]["inputs"]["height"],
            "chunk_path": graph["8"]["inputs"]["chunk_path"],
            "steps": graph["8"]["inputs"]["steps"],
            "max_raw_t": graph["9"]["inputs"]["max_raw_t"],
            "adapter": graph["2"]["inputs"]["adapter_name"],
            "status": status_str,
            "runner_wall_s": wall_s,
            "comfy_execution_s": parsed["comfy_execution_s"],
            "comfy_logged_s": comfy_logged_s,
            "cached_nodes": parsed["cached_nodes"],
            "gpu": gpu_stats,
            "outputs": output_videos,
            "execution_error": parsed["execution_error"],
        }
        results["runs"].append(run_record)
        (runs_dir / f"{run_id}.log").write_text(logs, encoding="utf-8")
        out_json.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

        print(
            f"[{run_id}] status={status_str} comfy_s={parsed['comfy_execution_s']} "
            f"wall_s={wall_s} peak_vram={gpu_stats.get('peak_vram_mib')}MiB cached={len(parsed['cached_nodes'])}",
            flush=True,
        )
        if status_str != "success":
            err_msg = (parsed["execution_error"] or {}).get("exception_message", "unknown error")
            print(f"[{run_id}] ERROR: {err_msg}", flush=True)
            if run_id == "1080p_native_2step":
                native_2step_failed = True
                subprocess.run(["docker", "restart", CONTAINER_NAME], capture_output=True, timeout=60)
            if fatal:
                return 1

    results["finished_at"] = datetime.now(timezone.utc).isoformat()
    out_json.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("720p/1080p BENCHMARK COMPLETE:", out_json, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
