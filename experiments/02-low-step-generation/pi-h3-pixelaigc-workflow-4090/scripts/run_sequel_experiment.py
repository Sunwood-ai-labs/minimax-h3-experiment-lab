#!/usr/bin/env python3
"""Sequel experiment on RTX 4090 using pixelaigc/ComfyUI-MiniMax-H3-pi-H3-Workflow."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
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

SERVER_ROOM_PROMPT = (
    'integrated_multimodal_description: [Shot 1] Live-action, epic cinematic, a slow push-in '
    'through a dim, dusty server room overgrown with thick cobwebs, a single ancient computer '
    'monitor glowing at the center of the frame showing a progress bar stuck at "99%", a '
    'skeleton in an office chair slumped in front of it with one bony finger still on the mouse, '
    'dust drifting through a shaft of cold light. A deep, gravelly movie-trailer narrator (S1) '
    'says off-screen: <d>[English] In a world where your render outlived you...</d>\n\n'
    'overall_soundscape: A low electrical hum, the slow creak of the office chair, and a '
    'single cooling fan rattling and winding down.\n\n'
    'non_diegetic_music: Ominous low brass and taiko drums build slowly.'
)

FL2VA_PROMPT = (
    'integrated_multimodal_description: Live-action, cinematic 35mm film time-lapse transition '
    'in a narrow traditional Tokyo backstreet alley. '
    '[Shot 1] 00:00-00:02: Nighttime light rain falls onto wet cobblestones reflecting red paper '
    'lanterns and cyan neon signs, the wooden sliding door at the far end is closed. '
    '[Shot 2] 00:02-00:05: As the camera glides gently forward, the rain clears and warm golden '
    'morning sunlight gradually floods the alley; the lanterns fade, the cobblestones glisten, '
    'and the wooden sliding door slides smoothly open revealing warm golden light and gentle steam '
    'drifting out. A calm Japanese narrator (S1) says softly: '
    '<d>[Japanese] 長い雨が止み、路地の奥に静かな朝が訪れる。</d>\n\n'
    'overall_soundscape: Gentle night rainfall and distant city hum gradually fade into soft '
    'morning birdsong, the wooden sliding door rolling open, and the faint hiss of a kettle.\n\n'
    'non_diegetic_music: Minimalist warm solo piano swelling softly as the morning sun appears.'
)


def build_workflow(
    *,
    prompt: str,
    width: int,
    height: int,
    length: int,
    steps: int,
    attn: str,
    seed: int,
    filename_prefix: str,
    first_frame: str | None = None,
    last_frame: str | None = None,
) -> dict:
    assert steps in (2, 4)
    assert attn in ("sol", "spark")

    adapter_name = (
        "pi_h3_2step_dwd_adapter_int8_convrot.safetensors"
        if steps == 2
        else "pi_h3_4step_dwd_adapter_int8_convrot.safetensors"
    )
    max_raw_t = 0.93 if steps == 2 else 0.96

    g: dict[str, dict] = {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
                "weight_dtype": "default",
            },
        },
        "2": {
            "class_type": "Load LakonLab Adapter",
            "inputs": {
                "model": ["1", 0],
                "adapter_name": adapter_name,
                "adapter_strength": 1.0,
            },
        },
        "3": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
                "type": "minimax",
                "device": "default",
            },
        },
        "4": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "minimax_h3_video_vae_int8_convrot.safetensors"},
        },
        "5": {
            "class_type": "VAELoader",
            "inputs": {"vae_name": "minimax_h3_audio_vae_fp32.safetensors"},
        },
        "6": {
            "class_type": "MiniMaxH3ImageToVideo",
            "inputs": {
                "clip": ["3", 0],
                "vae": ["4", 0],
                "prompt": prompt,
                "width": width,
                "height": height,
                "length": length,
            },
        },
        "7": {
            "class_type": "MiniMaxH3SigmaShift",
            "inputs": {
                "model": ["2", 0],
                "shift_video": 11.99 if attn == "sol" else 12.0,
                "shift_audio": 3.0,
            },
        },
    }

    if first_frame is not None:
        g["21"] = {"class_type": "LoadImage", "inputs": {"image": first_frame}}
        g["23"] = {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["21", 0],
                "upscale_method": "lanczos",
                "width": width,
                "height": height,
                "crop": "center",
            },
        }
        g["6"]["inputs"]["first_frame"] = ["23", 0]

    if last_frame is not None:
        g["22"] = {"class_type": "LoadImage", "inputs": {"image": last_frame}}
        g["24"] = {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["22", 0],
                "upscale_method": "lanczos",
                "width": width,
                "height": height,
                "crop": "center",
            },
        }
        g["6"]["inputs"]["last_frame"] = ["24", 0]

    if attn == "sol":
        g["8"] = {
            "class_type": "BlockSparseAttention",
            "inputs": {
                "model": ["7", 0],
                "selection": "sol-attn",
                "selection.tau": 1.0,
                "start_percent": 0.0,
                "end_percent": 1.0,
                "dense_blocks": "0, 1",
                "min_tokens": 12288,
                "extra_tokens": 256,
                "sink_conditioning": "exact_kv_and_rows",
                "verbose": False,
            },
        }
    else:
        g["8"] = {
            "class_type": "MiniMaxH3SparkAttentionSM89",
            "inputs": {
                "model": ["7", 0],
                "mode": "speed",
                "steps": steps,
                "warmup_mode": "warmup_ratio",
                "warmup_ratio": 0.0,
                "warmup_steps": 4,
                "topk_mode": "topk_ratio",
                "topk_ratio": 0.2,
                "topk_blocks": 228,
                "dense_layers": 0,
                "min_tokens": 12288,
                "strict": True,
                "dense_backend": "inherit",
                "tail_granularity": "query",
                "reblock_layout": "q_reuse_k",
                "sparse_scope": "target-video",
                "producer_chunk": 16384,
                "chunk_path": "none",
            },
        }

    g.update(
        {
            "9": {
                "class_type": "pi-Flow Scheduler",
                "inputs": {
                    "model": ["8", 0],
                    "steps": steps,
                    "min_raw_t": 0.0,
                    "max_raw_t": max_raw_t,
                    "final_step_size_scale": 0.6,
                },
            },
            "10": {
                "class_type": "BasicGuider",
                "inputs": {
                    "model": ["8", 0],
                    "conditioning": ["6", 0],
                },
            },
            "11": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": "euler"}},
            "12": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
            "13": {
                "class_type": "SamplerCustomAdvanced",
                "inputs": {
                    "noise": ["12", 0],
                    "guider": ["10", 0],
                    "sampler": ["11", 0],
                    "sigmas": ["9", 0],
                    "latent_image": ["6", 1],
                },
            },
            "14": {"class_type": "DWD Decode", "inputs": {"samples": ["13", 0]}},
            "15": {
                "class_type": "VAEDecodeAudio",
                "inputs": {"samples": ["13", 0], "vae": ["5", 0]},
            },
            "16": {
                "class_type": "CreateVideo",
                "inputs": {
                    "images": ["14", 0],
                    "audio": ["15", 0],
                    "fps": 24.0,
                    "bit_depth": "auto",
                    "color_space": "sRGB",
                    "chroma_subsampling": "auto",
                    "codec": "none",
                },
            },
            "17": {
                "class_type": "SaveVideo",
                "inputs": {
                    "video": ["16", 0],
                    "filename_prefix": filename_prefix,
                    "format": "mp4",
                    "format.codec": "auto",
                },
            },
        }
    )
    return g


def http_json(url: str, payload: dict | None = None) -> dict:
    if payload is None:
        with request.urlopen(url, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        url, data=data, headers={"Content-Type": "application/json; charset=utf-8"}
    )
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
            "avg_gpu_util_pct": round(
                sum(s["util_gpu_pct"] for s in self.samples) / len(self.samples), 1
            ),
            "peak_power_w": round(max(s["power_draw_w"] for s in self.samples), 2),
            "avg_power_w": round(
                sum(s["power_draw_w"] for s in self.samples) / len(self.samples), 2
            ),
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
                res = subprocess.run(
                    cmd, capture_output=True, text=True, timeout=3, check=True
                )
                parts = [p.strip() for p in res.stdout.strip().splitlines()[0].split(",")]
                if len(parts) >= 6:
                    self.samples.append(
                        {
                            "t": round(time.time(), 3),
                            "memory_used_mib": float(parts[0]),
                            "memory_total_mib": float(parts[1]),
                            "util_gpu_pct": float(parts[2]),
                            "util_mem_pct": float(parts[3]),
                            "power_draw_w": float(parts[4]),
                            "temp_c": float(parts[5]),
                        }
                    )
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
        "ts_start_ms": ts_start,
        "ts_end_ms": ts_end,
        "cached_nodes": cached_nodes,
        "execution_error": exec_error,
    }


def extract_output_files(history_item: dict) -> list[dict]:
    files = []
    for node_id, node_out in (history_item.get("outputs") or {}).items():
        for key in ("images", "videos", "gifs", "audio"):
            for entry in node_out.get(key) or []:
                subfolder = entry.get("subfolder", "")
                filename = entry.get("filename", "")
                rel = Path(subfolder) / filename if subfolder else Path(filename)
                full = OUTPUT_ROOT / rel
                info = {
                    "node_id": node_id,
                    "media_key": key,
                    "filename": filename,
                    "subfolder": subfolder,
                    "host_path": str(full),
                }
                if full.exists():
                    info["size_bytes"] = full.stat().st_size
                    info["sha256"] = sha256_file(full)
                files.append(info)
    return files


def run_matrix(specs: list[dict], exp_dir: Path, out_json: Path) -> None:
    wf_dir = exp_dir / "workflows"
    runs_dir = exp_dir / "runs"
    wf_dir.mkdir(parents=True, exist_ok=True)
    runs_dir.mkdir(parents=True, exist_ok=True)

    stats = http_json(f"{BASE_URL}/system_stats")
    results: dict = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "system_stats": stats,
        "runs": [],
    }

    for spec in specs:
        run_id = spec["run_id"]
        graph = build_workflow(
            prompt=spec["prompt"],
            width=spec["width"],
            height=spec["height"],
            length=spec["length"],
            steps=spec["steps"],
            attn=spec["attn"],
            seed=spec["seed"],
            filename_prefix=spec["prefix"],
            first_frame=spec.get("first_frame"),
            last_frame=spec.get("last_frame"),
        )
        (wf_dir / f"{run_id}_api.json").write_text(
            json.dumps(graph, indent=2, ensure_ascii=False), encoding="utf-8"
        )

        since_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        sampler = GpuSampler(GPU_UUID, interval=0.5)
        sampler.start()
        t0 = time.perf_counter()

        try:
            resp = http_json(
                f"{BASE_URL}/prompt",
                {"prompt": graph, "client_id": str(uuid.uuid4())},
            )
            prompt_id = resp["prompt_id"]
            print(
                f"[{run_id}] queued prompt_id={prompt_id} ({spec['width']}x{spec['height']}, "
                f"{spec['length']}f, {spec['steps']}step, {spec['attn']}) ...",
                flush=True,
            )

            history_item = None
            deadline = time.time() + 1800
            while time.time() < deadline:
                time.sleep(0.5)
                hist = http_json(f"{BASE_URL}/history/{prompt_id}")
                if prompt_id in hist:
                    history_item = hist[prompt_id]
                    status_str = history_item.get("status", {}).get("status_str")
                    if status_str in ("success", "error"):
                        break
        except Exception as exc:
            wall_s = round(time.perf_counter() - t0, 3)
            gpu_stats = sampler.stop()
            logs = get_container_logs_since(since_iso)
            (runs_dir / f"{run_id}.log").write_text(logs, encoding="utf-8")
            rec = {
                "run_id": run_id,
                "spec": {k: v for k, v in spec.items() if k != "prompt"},
                "status": "exception",
                "error": str(exc),
                "wall_s": wall_s,
                "gpu": gpu_stats,
            }
            results["runs"].append(rec)
            out_json.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"[{run_id}] EXCEPTION: {exc}", flush=True)
            continue

        wall_s = round(time.perf_counter() - t0, 3)
        gpu_stats = sampler.stop()
        logs = get_container_logs_since(since_iso)
        (runs_dir / f"{run_id}.log").write_text(logs, encoding="utf-8")

        if history_item is None:
            rec = {
                "run_id": run_id,
                "spec": {k: v for k, v in spec.items() if k != "prompt"},
                "status": "timeout",
                "wall_s": wall_s,
                "gpu": gpu_stats,
            }
        else:
            status_str = history_item.get("status", {}).get("status_str")
            parsed = parse_history_messages(history_item)
            prompt_exec_match = re.findall(r"Prompt executed in ([0-9.]+) seconds", logs)
            comfy_logged_s = float(prompt_exec_match[-1]) if prompt_exec_match else None
            out_files = extract_output_files(history_item)
            rec = {
                "run_id": run_id,
                "spec": {k: v for k, v in spec.items() if k != "prompt"},
                "prompt_id": prompt_id,
                "status": status_str,
                "wall_s": wall_s,
                "comfy_execution_s": parsed["comfy_execution_s"],
                "comfy_logged_s": comfy_logged_s,
                "cached_nodes_count": len(parsed["cached_nodes"]),
                "execution_error": parsed["execution_error"],
                "gpu": gpu_stats,
                "outputs": out_files,
            }
            print(
                f"[{run_id}] status={status_str} comfy_s={parsed['comfy_execution_s']} "
                f"wall_s={wall_s} peak_vram={gpu_stats.get('peak_vram_mib')}MiB "
                f"cached={len(parsed['cached_nodes'])}",
                flush=True,
            )

        results["runs"].append(rec)
        results["updated_at"] = datetime.now(timezone.utc).isoformat()
        out_json.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")


PART_A_SPECS = [
    # 5.17s (124f) 768p 2-step Sol-Attn: warmup (Triton JIT) + warm vs previous Spark-Attn (32.32s)
    {
        "run_id": "768p_5s_2step_sol_warmup",
        "prompt": SERVER_ROOM_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 124,
        "steps": 2,
        "attn": "sol",
        "seed": 41,
        "prefix": "video/pi-h3-sequel/768p_5s_2step_sol_warmup",
    },
    {
        "run_id": "768p_5s_2step_sol_warm",
        "prompt": SERVER_ROOM_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 124,
        "steps": 2,
        "attn": "sol",
        "seed": 42,
        "prefix": "video/pi-h3-sequel/768p_5s_2step_sol_warm",
    },
    # 8.0s (192f) 768p 2-step: Sol-Attn vs Spark-Attn SM89 (vs author 3060: 262s)
    {
        "run_id": "768p_8s_2step_sol",
        "prompt": SERVER_ROOM_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 192,
        "steps": 2,
        "attn": "sol",
        "seed": 42,
        "prefix": "video/pi-h3-sequel/768p_8s_2step_sol",
    },
    {
        "run_id": "768p_8s_2step_spark",
        "prompt": SERVER_ROOM_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 192,
        "steps": 2,
        "attn": "spark",
        "seed": 42,
        "prefix": "video/pi-h3-sequel/768p_8s_2step_spark",
    },
    # 10.125s (243f) 768p 2-step: Sol-Attn vs Spark-Attn SM89 (workflow default 10s)
    {
        "run_id": "768p_10s_2step_sol",
        "prompt": SERVER_ROOM_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 243,
        "steps": 2,
        "attn": "sol",
        "seed": 42,
        "prefix": "video/pi-h3-sequel/768p_10s_2step_sol",
    },
    {
        "run_id": "768p_10s_2step_spark",
        "prompt": SERVER_ROOM_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 243,
        "steps": 2,
        "attn": "spark",
        "seed": 42,
        "prefix": "video/pi-h3-sequel/768p_10s_2step_spark",
    },
    # 10.125s (243f) 768p 4-step: Sol-Attn vs Spark-Attn SM89
    {
        "run_id": "768p_10s_4step_sol",
        "prompt": SERVER_ROOM_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 243,
        "steps": 4,
        "attn": "sol",
        "seed": 42,
        "prefix": "video/pi-h3-sequel/768p_10s_4step_sol",
    },
    {
        "run_id": "768p_10s_4step_spark",
        "prompt": SERVER_ROOM_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 243,
        "steps": 4,
        "attn": "spark",
        "seed": 42,
        "prefix": "video/pi-h3-sequel/768p_10s_4step_spark",
    },
    # 30.0s (719f) 480p 2-step: Sol-Attn vs Spark-Attn SM89 (long-duration stress test)
    {
        "run_id": "480p_30s_2step_sol",
        "prompt": SERVER_ROOM_PROMPT,
        "width": 864,
        "height": 480,
        "length": 719,
        "steps": 2,
        "attn": "sol",
        "seed": 42,
        "prefix": "video/pi-h3-sequel/480p_30s_2step_sol",
    },
    {
        "run_id": "480p_30s_2step_spark",
        "prompt": SERVER_ROOM_PROMPT,
        "width": 864,
        "height": 480,
        "length": 719,
        "steps": 2,
        "attn": "spark",
        "seed": 42,
        "prefix": "video/pi-h3-sequel/480p_30s_2step_spark",
    },
]

PART_B_SPECS = [
    {
        "run_id": "fl2va_768p_5s_2step_sol",
        "prompt": FL2VA_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 124,
        "steps": 2,
        "attn": "sol",
        "seed": 42,
        "prefix": "video/pi-h3-sequel/fl2va_768p_5s_2step_sol",
        "first_frame": "fl2va_first_night_rain.png",
        "last_frame": "fl2va_last_morning_sun.png",
    },
    {
        "run_id": "fl2va_768p_5s_4step_sol",
        "prompt": FL2VA_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 124,
        "steps": 4,
        "attn": "sol",
        "seed": 42,
        "prefix": "video/pi-h3-sequel/fl2va_768p_5s_4step_sol",
        "first_frame": "fl2va_first_night_rain.png",
        "last_frame": "fl2va_last_morning_sun.png",
    },
    {
        "run_id": "fl2va_768p_5s_4step_spark",
        "prompt": FL2VA_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 124,
        "steps": 4,
        "attn": "spark",
        "seed": 42,
        "prefix": "video/pi-h3-sequel/fl2va_768p_5s_4step_spark",
        "first_frame": "fl2va_first_night_rain.png",
        "last_frame": "fl2va_last_morning_sun.png",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["part_a", "part_b"], required=True)
    args = parser.parse_args()
    exp_dir = Path(__file__).resolve().parent.parent
    if args.phase == "part_a":
        run_matrix(PART_A_SPECS, exp_dir, exp_dir / "runs" / "part_a_results.json")
    else:
        run_matrix(PART_B_SPECS, exp_dir, exp_dir / "runs" / "part_b_results.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
