#!/usr/bin/env python3
"""Build tracked contact-sheet.jpg, contact-sheet.json, and experiment.json for pi-h3-pixelaigc-workflow-4090."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from qa_and_previews import EXP_DIR, PREVIEWS_DIR, RUNS_DIR, extract_frame, make_grid


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().upper()


def main() -> int:
    part_a = json.loads((RUNS_DIR / "part_a_results.json").read_text(encoding="utf-8"))
    part_b = json.loads((RUNS_DIR / "part_b_results.json").read_text(encoding="utf-8"))
    part_c = json.loads((RUNS_DIR / "part_c_results.json").read_text(encoding="utf-8"))
    qa_ab = json.loads((RUNS_DIR / "media_qa.json").read_text(encoding="utf-8"))
    qa_c = json.loads((RUNS_DIR / "media_qa_part_c.json").read_text(encoding="utf-8"))
    qa_all = {**qa_ab, **qa_c}

    all_runs = part_a["runs"] + part_b["runs"] + part_c["runs"]
    run_by_id = {r["run_id"]: r for r in all_runs}

    tmp_dir = PREVIEWS_DIR / "_tmp_cs"
    tmp_dir.mkdir(exist_ok=True)

    cs_specs = [
        ("768p 10s 4-step\nSpark SM89 (124.7s)", "768p_10s_4step_spark", [0.5, 3.5, 6.5, 9.5]),
        ("480p 30s 2-step\nSol-Attn (336.8s)", "480p_30s_2step_sol", [1.0, 10.0, 20.0, 29.0]),
        ("1080p Native 5s\n2-step Sol (100.2s)", "1080p_native_5s_2step_sol", [0.5, 2.0, 3.5, 5.0]),
        ("FL2VA 768p 10s\n4-step Spark (133.2s)", "fl2va_768p_10s_4step_spark", [0.1, 3.5, 7.0, 10.0]),
        ("FL2VA 480p 30s\n2-step Sol (347.2s)", "fl2va_480p_30s_2step_sol", [0.1, 10.0, 20.0, 29.8]),
    ]

    rows = []
    manifest_sources = []
    repo_root = Path(r"D:\Prj\minimax-h3-compose")

    for idx, (label, rid, times) in enumerate(cs_specs, start=1):
        rec = run_by_id[rid]
        out_entry = rec["outputs"][0]
        p = Path(out_entry["host_path"])
        frames = [
            (f"t = {t:.1f}s", extract_frame(p, t, tmp_dir / f"{rid}_{t:.1f}.png"))
            for t in times
        ]
        rows.append((label, frames))
        q = qa_all[rid]
        rel_path = p.relative_to(repo_root).as_posix()
        manifest_sources.append(
            {
                "row": idx,
                "run_id": rid,
                "path": rel_path,
                "bytes": out_entry.get("size_bytes", p.stat().st_size),
                "sha256": out_entry.get("sha256", sha256_file(p)),
                "width": q["video"]["width"],
                "height": q["video"]["height"],
                "durationSeconds": q["duration_s"],
                "fps": q["video"]["r_frame_rate"],
                "frames": q["video"]["nb_frames"],
                "sampleTimesSeconds": times,
            }
        )

    cs_jpg = PREVIEWS_DIR / "contact-sheet.jpg"
    make_grid(rows, 320, 180, cs_jpg)

    cs_manifest = {
        "schema": "minimax-h3-video-contact-sheet/v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sources": manifest_sources,
        "sampling": {
            "frameCountPerSource": 4,
            "columns": 4,
            "rowsPerSource": 1,
            "tileWidth": 320,
            "tileHeight": 180,
            "order": "Each row corresponds to one representative run; frames advance left-to-right.",
        },
        "output": {
            "path": "experiments/02-low-step-generation/pi-h3-pixelaigc-workflow-4090/previews/contact-sheet.jpg",
            "bytes": cs_jpg.stat().st_size,
            "sha256": sha256_file(cs_jpg),
            "format": "jpg",
        },
    }
    (PREVIEWS_DIR / "contact-sheet.json").write_text(
        json.dumps(cs_manifest, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    # Clean up temporary extracted frames
    for d in (PREVIEWS_DIR / "_frames", PREVIEWS_DIR / "_frames_part_c", tmp_dir):
        if d.exists():
            shutil.rmtree(d)

    # Build experiment.json
    wf_dir = EXP_DIR / "workflows"
    formatted_runs = []
    for r in all_runs:
        rid = r["run_id"]
        spec = r["spec"]
        wf_rel = f"workflows/{rid}_api.json"
        wf_path = EXP_DIR / wf_rel
        outs = []
        for o in r.get("outputs") or []:
            hp = Path(o["host_path"])
            outs.append(
                {
                    "filename": o["filename"],
                    "subfolder": o["subfolder"],
                    "relative_path": f"{o['subfolder']}/{o['filename']}" if o.get("subfolder") else o["filename"],
                    "local_path": str(hp),
                    "exists": hp.exists(),
                    "bytes": o.get("size_bytes"),
                    "sha256": o.get("sha256"),
                }
            )
        formatted_runs.append(
            {
                "run_id": rid,
                "workflow": wf_rel,
                "workflow_sha256": sha256_file(wf_path) if wf_path.exists() else None,
                "prompt_id": r.get("prompt_id"),
                "width": spec["width"],
                "height": spec["height"],
                "length": spec["length"],
                "steps": spec["steps"],
                "attention": spec["attn"],
                "seed": spec["seed"],
                "first_frame": spec.get("first_frame"),
                "last_frame": spec.get("last_frame"),
                "status": r["status"],
                "runner_wall_s": r.get("wall_s"),
                "comfy_execution_s": r.get("comfy_execution_s"),
                "cached_nodes_count": r.get("cached_nodes_count"),
                "gpu": r.get("gpu"),
                "outputs": outs,
                "execution_error": r.get("execution_error", {}).get("exception_type")
                if isinstance(r.get("execution_error"), dict)
                else r.get("execution_error"),
            }
        )

    exp_record = {
        "id": "2026-11-23-pi-h3-pixelaigc-workflow-4090",
        "date": "2026-11-23",
        "category": "02-low-step-generation",
        "status": "verified",
        "baselineExperiment": "../pi-h3-dwd-spark-4090/experiment.json",
        "hypothesis": (
            "The pixelaigc/ComfyUI-MiniMax-H3-pi-H3-Workflow (pi-H3-DWD-3060-2.json) runs with zero "
            "missing nodes or additional weights on the existing RTX 4090 pi-H3 Docker stack, enables "
            "long-duration generation up to 30s at 480p and native 1080p at 5s via Sol-Attn + DWD, "
            "and supports 5s/10s/30s FL2VA first-and-last-frame transitions with synchronized stereo audio."
        ),
        "purpose": (
            "Evaluate pixelaigc/ComfyUI-MiniMax-H3-pi-H3-Workflow on RTX 4090 across Sol-Attn vs "
            "Spark-Attn SM89, long durations (5s/8s/10s/30s), native 1080p vs 768p 30s VRAM limits, "
            "and FL2VA first/last-frame transitions (5s/10s/30s)."
        ),
        "scope": "ComfyUI v0.46.0 + ComfyUI-piFlow + ComfyUI-SolAttn_triton + Spark-H3 v0.2.0 SM89 inside Docker on RTX 4090 (24GB VRAM).",
        "sources": [
            {
                "title": "pixelaigc/ComfyUI-MiniMax-H3-pi-H3-Workflow",
                "url": "https://github.com/pixelaigc/ComfyUI-MiniMax-H3-pi-H3-Workflow",
            },
            {
                "title": "Lakonik/pi-H3",
                "url": "https://huggingface.co/Lakonik/pi-H3",
            },
            {
                "title": "ComfyUI-piFlow",
                "url": "https://github.com/Lakonik/ComfyUI-piFlow",
            },
            {
                "title": "ComfyUI-SolAttn_triton",
                "url": "https://github.com/kijai/ComfyUI-SolAttn_triton",
            },
        ],
        "conditions": {
            "gpu": "NVIDIA GeForce RTX 4090 (24564 MiB VRAM, SM 8.9)",
            "dockerImage": "local/minimax-h3-comfyui:v0.46.0-pih3",
            "comfyui": "v0.46.0",
            "baseModel": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
            "textEncoder": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
            "videoVae": "minimax_h3_video_vae_int8_convrot.safetensors",
            "audioVae": "minimax_h3_audio_vae_fp32.safetensors",
            "adapters": [
                "pi_h3_2step_dwd_adapter_int8_convrot.safetensors",
                "pi_h3_4step_dwd_adapter_int8_convrot.safetensors",
            ],
            "attentionBackends": [
                "BlockSparseAttention (sol-attn, tau=1.0, dense_blocks='0, 1', extra_tokens=256, sink_conditioning=exact_kv_and_rows)",
                "MiniMaxH3SparkAttentionSM89 (mode=speed, topk_ratio=0.2, dense_layers=0, reblock_layout=q_reuse_k)",
            ],
            "sampler": "euler",
            "scheduler": "pi-Flow Scheduler (2-step max_raw_t=0.93, 4-step max_raw_t=0.96, final_step_size_scale=0.6)",
            "fps": 24,
        },
        "runs": formatted_runs,
        "mediaQa": qa_all,
        "previews": {
            "contactSheet": "previews/contact-sheet.jpg",
            "manifest": "previews/contact-sheet.json",
            "longComparison": "previews/compare_sol_vs_spark_long.jpg",
            "fl2va5sComparison": "previews/compare_fl2va_transition.jpg",
            "native1080pComparison": "previews/compare_1080p_native_sol.jpg",
            "fl2vaLongComparison": "previews/compare_fl2va_long_10s_30s.jpg",
        },
        "publicEvidence": {
            "tile": "previews/contact-sheet.jpg",
            "manifest": "previews/contact-sheet.json",
            "videoStatus": "local-only",
            "note": "Generated MP4s remain local under runtime/pih3-4090/output/video/pi-h3-sequel* and are excluded from Git; tracked tiles, manifests, and SHA-256 hashes verify all outputs.",
        },
        "publication": {
            "platform": "x",
            "status": "not_posted",
            "videoTweets": [],
        },
        "conclusion": (
            "17 of 18 runs succeeded on RTX 4090 with zero dense fallbacks and zero black frames (all with AAC 32kHz stereo audio, RMS -13.78 to -15.76 dB). "
            "Sol-Attn unlocked native 1080p (1920x1088->1080) 5s 2-step generation in 100.23s (22.5 GB Peak VRAM) and 30s (719f) 480p T2V/FL2VA in ~337-347s. "
            "768p 30s hit 24GB VRAM OOM, establishing 480p as the practical 30s ceiling on 24GB. "
            "For 4-step generation (10s T2V, 5s/10s FL2VA), Spark-Attn SM89 outperformed Sol-Attn by 25-36% (e.g., 54.65s vs 72.52s on 5s FL2VA; 124.70s vs 196.04s on 10s T2V; 133.22s on 10s FL2VA)."
        ),
        "limitations": [
            "768p 30s (719f) exceeded RTX 4090 24GB VRAM during sampling (torch.OutOfMemoryError).",
            "Generated MP4 videos are stored locally under runtime/pih3-4090/output/video/pi-h3-sequel* and are not committed to Git.",
        ],
    }

    (EXP_DIR / "experiment.json").write_text(
        json.dumps(exp_record, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("Generated contact-sheet.jpg, contact-sheet.json, and experiment.json successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
