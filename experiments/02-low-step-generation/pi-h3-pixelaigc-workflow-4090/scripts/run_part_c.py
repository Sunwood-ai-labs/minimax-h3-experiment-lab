#!/usr/bin/env python3
"""Part C sequel experiment on RTX 4090: 1080p native/30s + long-duration FL2VA (10s / 30s)."""

from __future__ import annotations

import json
import re
import subprocess
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from run_sequel_experiment import (
    BASE_URL,
    GPU_UUID,
    OUTPUT_ROOT,
    SERVER_ROOM_PROMPT,
    GpuSampler,
    build_workflow,
    extract_output_files,
    get_container_logs_since,
    http_json,
    parse_history_messages,
    sha256_file,
)

FL2VA_LONG_10S_PROMPT = (
    'integrated_multimodal_description: Live-action, cinematic 35mm film time-lapse transition '
    'in a narrow traditional Tokyo backstreet alley. '
    '[Shot 1] 00:00-00:03: Nighttime light rain falls onto wet cobblestones reflecting red paper '
    'lanterns and cyan neon signs; the wooden sliding door at the far end is closed. '
    '[Shot 2] 00:03-00:07: The rain gradually stops, cool blue dawn light begins to wash over '
    'the alley as neon signs flicker off and warm morning light slowly creeps down the wooden walls. '
    '[Shot 3] 00:07-00:10: Golden sunrise floods the alley, potted plants glisten, and the wooden '
    'sliding door slides smoothly open revealing warm interior light and rising steam. '
    'A calm Japanese narrator (S1) says softly: '
    '<d>[Japanese] 長い雨が止み、夜がほどけていく。路地の奥に、あたたかな朝が訪れる。</d>\n\n'
    'overall_soundscape: Gentle night rainfall and distant city hum gradually fade into quiet '
    'dawn stillness, then morning birdsong, the wooden sliding door rolling open, and a faint kettle.\n\n'
    'non_diegetic_music: Minimalist warm solo piano evolving slowly from melancholic minor to hopeful major.'
)

FL2VA_LONG_30S_PROMPT = (
    'integrated_multimodal_description: Live-action, cinematic 35mm film continuous time-lapse '
    'transition in a narrow traditional Tokyo backstreet alley from rainy midnight to golden sunrise. '
    '[Shot 1] 00:00-00:10: Deep rainy night, wet cobblestones shimmering with red lanterns and cyan neon, '
    'the wooden sliding door at the far end remains closed as rain drips softly from the eaves. '
    '[Shot 2] 00:10-00:20: Rain slows to a stop, mist rises from the stone alley, neon lights dim out '
    'one by one as pale indigo dawn gradually brightens into soft amber twilight. '
    '[Shot 3] 00:20-00:30: Warm golden morning sunlight streams across the alley illuminating drying stones '
    'and lush green potted plants; the wooden sliding door slides open revealing cozy golden light and steam. '
    'A calm Japanese narrator (S1) says slowly: '
    '<d>[Japanese] 雨の夜がゆっくりと明け、ネオンの光が消えていく。やがて朝日が差し込み、路地の奥の扉が静かに開く。</d>\n\n'
    'overall_soundscape: Steady rainfall and night ambience slowly subside into misty pre-dawn quiet, '
    'followed by crisp morning sparrows, distant footsteps, the wooden door sliding open, and gentle steam.\n\n'
    'non_diegetic_music: Slow, contemplative solo piano and soft strings blooming warmly at sunrise.'
)

PART_C_SPECS = [
    # 1. 1080p native (1920x1088) 5.17s 2-step Sol-Attn -> cropped/scaled to exact 1920x1080
    {
        "run_id": "1080p_native_5s_2step_sol",
        "prompt": SERVER_ROOM_PROMPT,
        "width": 1920,
        "height": 1088,
        "length": 124,
        "steps": 2,
        "attn": "sol",
        "seed": 42,
        "prefix": "video/pi-h3-sequel-partc/1080p_native_5s_2step_sol",
        "in_graph_scale": (1920, 1080),
    },
    # 2. 768p 30s (719f) 2-step Sol-Attn + ffmpeg Lanczos 1080p upscale
    {
        "run_id": "768p_to_1080p_30s_2step_sol",
        "prompt": SERVER_ROOM_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 719,
        "steps": 2,
        "attn": "sol",
        "seed": 42,
        "prefix": "video/pi-h3-sequel-partc/768p_30s_2step_sol",
        "ffmpeg_upscale_1080p": True,
    },
    # 3. FL2VA 768p 10.1s (243f) 2-step Sol-Attn
    {
        "run_id": "fl2va_768p_10s_2step_sol",
        "prompt": FL2VA_LONG_10S_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 243,
        "steps": 2,
        "attn": "sol",
        "seed": 42,
        "prefix": "video/pi-h3-sequel-partc/fl2va_768p_10s_2step_sol",
        "first_frame": "fl2va_first_night_rain.png",
        "last_frame": "fl2va_last_morning_sun.png",
    },
    # 4. FL2VA 768p 10.1s (243f) 4-step Spark-Attn SM89
    {
        "run_id": "fl2va_768p_10s_4step_spark",
        "prompt": FL2VA_LONG_10S_PROMPT,
        "width": 1344,
        "height": 768,
        "length": 243,
        "steps": 4,
        "attn": "spark",
        "seed": 42,
        "prefix": "video/pi-h3-sequel-partc/fl2va_768p_10s_4step_spark",
        "first_frame": "fl2va_first_night_rain.png",
        "last_frame": "fl2va_last_morning_sun.png",
    },
    # 5. FL2VA 480p 30s (719f) 2-step Sol-Attn
    {
        "run_id": "fl2va_480p_30s_2step_sol",
        "prompt": FL2VA_LONG_30S_PROMPT,
        "width": 864,
        "height": 480,
        "length": 719,
        "steps": 2,
        "attn": "sol",
        "seed": 42,
        "prefix": "video/pi-h3-sequel-partc/fl2va_480p_30s_2step_sol",
        "first_frame": "fl2va_first_night_rain.png",
        "last_frame": "fl2va_last_morning_sun.png",
    },
]


def main() -> int:
    exp_dir = Path(__file__).resolve().parent.parent
    wf_dir = exp_dir / "workflows"
    runs_dir = exp_dir / "runs"
    out_json = runs_dir / "part_c_results.json"

    stats = http_json(f"{BASE_URL}/system_stats")
    results: dict = {
        "started_at": datetime.now(timezone.utc).isoformat(),
        "system_stats": stats,
        "runs": [],
    }

    for spec in PART_C_SPECS:
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
        if spec.get("in_graph_scale"):
            sw, sh = spec["in_graph_scale"]
            graph["18"] = {
                "class_type": "ImageScale",
                "inputs": {
                    "image": ["14", 0],
                    "upscale_method": "lanczos",
                    "width": sw,
                    "height": sh,
                    "crop": "center",
                },
            }
            graph["16"]["inputs"]["images"] = ["18", 0]

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
            deadline = time.time() + 2400
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

            upscaled_info = None
            if status_str == "success" and spec.get("ffmpeg_upscale_1080p") and out_files:
                src_mp4 = Path(out_files[0]["host_path"])
                if src_mp4.exists():
                    dst_mp4 = src_mp4.with_name(src_mp4.stem + "_1080p_lanczos.mp4")
                    t_up = time.perf_counter()
                    up_res = subprocess.run(
                        [
                            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
                            "-i", str(src_mp4),
                            "-vf", "scale=1920:1080:flags=lanczos",
                            "-c:v", "libx264", "-crf", "16", "-preset", "medium", "-pix_fmt", "yuv420p",
                            "-c:a", "copy",
                            str(dst_mp4),
                        ],
                        capture_output=True, text=True, check=False,
                    )
                    up_s = round(time.perf_counter() - t_up, 3)
                    if up_res.returncode == 0 and dst_mp4.exists():
                        upscaled_info = {
                            "host_path": str(dst_mp4),
                            "ffmpeg_upscale_s": up_s,
                            "size_bytes": dst_mp4.stat().st_size,
                            "sha256": sha256_file(dst_mp4),
                        }
                        print(f"[{run_id}] ffmpeg 1080p upscale done in {up_s}s -> {dst_mp4.name}", flush=True)

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
                "upscaled_1080p": upscaled_info,
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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
