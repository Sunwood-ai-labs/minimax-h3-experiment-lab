#!/usr/bin/env python3
"""Build contact sheets, comparison image, experiment.json, and READMEs for pi-H3 4090 benchmark."""

from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(r"D:\Prj\minimax-h3-compose")
EXP_DIR = REPO_ROOT / "experiments" / "02-low-step-generation" / "pi-h3-dwd-spark-4090"
OUT_DIR = REPO_ROOT / "runtime" / "pih3-4090" / "output" / "video" / "pi-h3-4090"
ARTIFACT_DIR = Path(r"C:\Users\makim\.gemini\antigravity\brain\147bd0aa-f4bc-4be4-b4a0-4800d6d2d9f1")

WARM_VIDEOS = [
    ("480p_2step_warm", OUT_DIR / "480p_2step_warm_00001_.mp4"),
    ("480p_4step_warm", OUT_DIR / "480p_4step_warm_00001_.mp4"),
    ("768p_2step_warm", OUT_DIR / "768p_2step_warm_00001_.mp4"),
    ("768p_4step_warm", OUT_DIR / "768p_4step_warm_00001_.mp4"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().upper()


def ffprobe_video(path: Path) -> dict:
    out = subprocess.check_output(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,avg_frame_rate,nb_frames",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(path),
        ],
        stdin=subprocess.DEVNULL,
        text=True,
        timeout=15,
    )
    data = json.loads(out)
    s = data["streams"][0]
    return {
        "width": int(s["width"]),
        "height": int(s["height"]),
        "durationSeconds": round(float(data["format"]["duration"]), 6),
        "fps": s["avg_frame_rate"],
        "frames": int(s["nb_frames"]),
    }


def main() -> int:
    previews_dir = EXP_DIR / "previews"
    previews_dir.mkdir(parents=True, exist_ok=True)

    bench = json.loads((EXP_DIR / "runs" / "benchmark_results.json").read_text(encoding="utf-8"))
    media_qa = json.loads((EXP_DIR / "runs" / "media_qa.json").read_text(encoding="utf-8"))

    # 1. Build 4-row (8 frames per video, 4 columns x 2 rows per block) contact-sheet.jpg
    frame_count = 8
    columns = 4
    tile_w = 320
    tile_h = 180
    probes = []
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y"]
    filter_parts = []
    for idx, (_, vp) in enumerate(WARM_VIDEOS):
        if not vp.is_file():
            raise FileNotFoundError(f"Missing video: {vp}")
        probe = ffprobe_video(vp)
        probes.append(probe)
        cmd.extend(["-i", str(vp)])
        fps_expr = f"{frame_count}/{probe['durationSeconds']}"
        filter_parts.append(
            f"[{idx}:v]fps={fps_expr},"
            f"scale={tile_w}:{tile_h}:force_original_aspect_ratio=decrease,"
            f"pad={tile_w}:{tile_h}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"tile={columns}x{frame_count // columns}:padding=6:margin=6[sheet{idx}]"
        )

    sheets = "".join(f"[sheet{i}]" for i in range(len(WARM_VIDEOS)))
    filter_parts.append(f"{sheets}vstack=inputs={len(WARM_VIDEOS)}[contact]")
    contact_jpg = previews_dir / "contact-sheet.jpg"
    cmd.extend(["-filter_complex", ";".join(filter_parts), "-map", "[contact]", "-frames:v", "1", "-q:v", "2", str(contact_jpg)])
    subprocess.run(cmd, stdin=subprocess.DEVNULL, check=True, timeout=30)

    # 2. Build contact-sheet.json
    source_records = []
    for idx, (_, vp) in enumerate(WARM_VIDEOS):
        probe = probes[idx]
        dur = probe["durationSeconds"]
        sample_times = [round((k + 0.5) * dur / frame_count, 3) for k in range(frame_count)]
        source_records.append({
            "row": idx + 1,
            "path": str(vp.relative_to(REPO_ROOT)).replace("\\", "/"),
            "bytes": vp.stat().st_size,
            "sha256": sha256_file(vp),
            **probe,
            "sampleTimesSeconds": sample_times,
        })

    manifest = {
        "schema": "minimax-h3-video-contact-sheet/v1",
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "sources": source_records,
        "sampling": {
            "frameCountPerSource": frame_count,
            "columns": columns,
            "rowsPerSource": frame_count // columns,
            "tileWidth": tile_w,
            "tileHeight": tile_h,
            "order": "Each source occupies one row block; frames advance left-to-right, then top-to-bottom.",
        },
        "output": {
            "path": str(contact_jpg.relative_to(REPO_ROOT)).replace("\\", "/"),
            "bytes": contact_jpg.stat().st_size,
            "sha256": sha256_file(contact_jpg),
            "format": "jpg",
        },
    }
    manifest_json = previews_dir / "contact-sheet.json"
    manifest_json.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 3. Build 768p 2-step vs 4-step comparison image without drawtext (Left: 2-step, Right: 4-step; rows: t=1.0s, 2.5s, 4.5s)
    v2 = OUT_DIR / "768p_2step_warm_00001_.mp4"
    v4 = OUT_DIR / "768p_4step_warm_00001_.mp4"
    comp_jpg = previews_dir / "compare_768p_2step_vs_4step.jpg"
    subprocess.run(
        [
            "ffmpeg",
            "-nostdin",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            "1.0",
            "-i",
            str(v2),
            "-ss",
            "1.0",
            "-i",
            str(v4),
            "-ss",
            "2.5",
            "-i",
            str(v2),
            "-ss",
            "2.5",
            "-i",
            str(v4),
            "-ss",
            "4.5",
            "-i",
            str(v2),
            "-ss",
            "4.5",
            "-i",
            str(v4),
            "-filter_complex",
            (
                "[0:v]scale=960:-1[a];[1:v]scale=960:-1[b];"
                "[2:v]scale=960:-1[c];[3:v]scale=960:-1[d];"
                "[4:v]scale=960:-1[e];[5:v]scale=960:-1[f];"
                "[a][b]hstack=inputs=2[r1];[c][d]hstack=inputs=2[r2];[e][f]hstack=inputs=2[r3];"
                "[r1][r2][r3]vstack=inputs=3[out]"
            ),
            "-map",
            "[out]",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(comp_jpg),
        ],
        stdin=subprocess.DEVNULL,
        check=True,
        timeout=30,
    )

    shutil.copy2(contact_jpg, ARTIFACT_DIR / "contact-sheet.jpg")
    shutil.copy2(comp_jpg, ARTIFACT_DIR / "compare_768p_2step_vs_4step.jpg")

    # 4. Write experiment.json
    exp_json = {
        "id": "2026-11-23-pi-h3-dwd-spark-4090",
        "date": "2026-11-23",
        "category": "02-low-step-generation",
        "status": "verified",
        "hypothesis": "On RTX 4090 (SM89, 24GB VRAM), pi-H3 1.0 (DWD + INT8 ConvRot + Spark-Attn SM89) can generate 5s 768p video with synchronized stereo audio in <=35s when warm (matching or beating the official RTX 3090 gpu-unlock 34.6s figure), and 4-step mode improves detail over 2-step within ~50s.",
        "purpose": "Benchmark and visually/audibly compare pi-H3 DWD + Spark-Attn SM89 on RTX 4090 across 480p and 768p at 2 steps vs 4 steps.",
        "scope": "ComfyUI v0.46.0 + ComfyUI-piFlow v1.4.2 + Spark-H3 v0.2.0 SM89 inside Docker on Windows 11 WSL2 with RTX 4090.",
        "sources": [
            {"title": "Lakonik/pi-H3", "url": "https://huggingface.co/Lakonik/pi-H3"},
            {"title": "ComfyUI-piFlow docs/piH3.md", "url": "https://github.com/Lakonik/ComfyUI-piFlow/blob/main/docs/piH3.md"},
            {"title": "Spark-H3 v0.2.0", "url": "https://github.com/zechengtang/Spark-H3/releases/tag/comfyui-v0.2.0"},
        ],
        "conditions": {
            "gpu": "NVIDIA GeForce RTX 4090 (24564 MiB VRAM, SM 8.9)",
            "dockerImage": "local/minimax-h3-comfyui:v0.46.0-pih3",
            "comfyui": "v0.46.0",
            "pytorch": "2.11.0+cu130",
            "python": "3.12.3",
            "baseModel": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
            "textEncoder": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
            "videoVae": "minimax_h3_video_vae_int8_convrot.safetensors",
            "audioVae": "minimax_h3_audio_vae_fp32.safetensors",
            "adapters": [
                "pi_h3_2step_dwd_adapter_int8_convrot.safetensors",
                "pi_h3_4step_dwd_adapter_int8_convrot.safetensors",
            ],
            "attention": "MiniMaxH3SparkAttentionSM89 (mode=speed, topk_ratio=0.2, dense_layers=0, reblock_layout=q_reuse_k)",
            "sampler": "euler",
            "scheduler": "pi-Flow Scheduler (2-step max_raw_t=0.93, 4-step max_raw_t=0.96, final_step_size_scale=0.6)",
            "frames": 124,
            "fps": 24,
            "seed_warm": 42,
        },
        "runs": bench["runs"],
        "mediaQa": media_qa,
        "previews": {
            "contactSheet": "previews/contact-sheet.jpg",
            "manifest": "previews/contact-sheet.json",
            "comparison768p": "previews/compare_768p_2step_vs_4step.jpg",
        },
        "publicEvidence": {
            "tile": "previews/contact-sheet.jpg",
            "manifest": "previews/contact-sheet.json",
            "videoStatus": "local-only",
            "note": "MP4 outputs remain local under runtime/pih3-4090/output/video/pi-h3-4090; tracked previews and hashes verify results.",
        },
        "publication": {
            "platform": "x",
            "status": "not_posted",
            "videoTweets": [],
        },
        "conclusion": "All 8 runs succeeded on RTX 4090 with zero Spark-H3 dense fallbacks. Warm end-to-end generation (models loaded + prompt encoded, including DWD Decode, Audio VAE Decode, and MP4 save) took 19.729s (480p 2-step), 28.367s (480p 4-step), 32.324s (768p 2-step), and 49.390s (768p 4-step).",
        "limitations": [
            "Very first cold start over WSL2 9p mount (/mnt -> D:\\Prj\\minimax-h3-compose\\models) plus initial Triton/torch compile took 1463.079s.",
            "Audio quality was verified quantitatively via ffprobe (AAC 32kHz stereo) and ffmpeg astats (RMS -13.9 to -15.0 dB), not listened to by human ears.",
        ],
    }
    (EXP_DIR / "experiment.json").write_text(json.dumps(exp_json, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 5. Write README.ja.md & README.md
    readme_ja = """# MiniMax-H3 Experiment: pi-H3 1.0 (DWD + Spark-Attn SM89) on RTX 4090

- ID: `2026-11-23-pi-h3-dwd-spark-4090`
- Category: `02-low-step-generation`
- Status: `verified`
- GPU: `NVIDIA GeForce RTX 4090 (24564 MiB VRAM, SM 8.9)`

Record: [experiment.json](./experiment.json) · [tracked tile](./previews/contact-sheet.jpg) · [manifest](./previews/contact-sheet.json) · [768p comparison](./previews/compare_768p_2step_vs_4step.jpg)

## 実測結果サマリー（RTX 4090 · 5.17秒 / 124 frames / 24fps + ステレオ音声）

| 条件 | Seed | ComfyUI実行時間 | クライアントWall | Peak VRAM | Avg / Peak Power | キャッシュ状態 |
|---|---:|---:|---:|---:|---:|---|
| `480p_2step_cold` (864×480, 2-step) | 100 | 1463.079 s | 1463.342 s | 23,868 MiB | 13.2 / 296.2 W | コールド (初回読込+コンパイル) |
| **`480p_2step_warm`** (864×480, 2-step) | 42 | **19.729 s** | 20.208 s | 23,096 MiB | 133.4 / 303.2 W | モデル・プロンプトキャッシュ済み (`cached=11`) |
| `768p_2step_warmup` (1344×768, 2-step) | 41 | 72.526 s | 72.792 s | 23,592 MiB | 114.3 / 404.5 W | 解像度変更+初回768pコンパイル (`cached=9`) |
| **`768p_2step_warm`** (1344×768, 2-step) | 42 | **32.324 s** | 32.603 s | 24,007 MiB | 197.7 / 403.7 W | モデル・プロンプトキャッシュ済み (`cached=11`) |
| `480p_4step_cold` (864×480, 4-step) | 100 | 76.216 s | 76.729 s | 23,731 MiB | 99.1 / 293.3 W | 4-stepアダプター切替+再エンコード (`cached=5`) |
| **`480p_4step_warm`** (864×480, 4-step) | 42 | **28.367 s** | 28.883 s | 22,979 MiB | 167.3 / 295.4 W | モデル・プロンプトキャッシュ済み (`cached=11`) |
| `768p_4step_warmup` (1344×768, 4-step) | 41 | 83.495 s | 83.848 s | 23,411 MiB | 167.3 / 409.1 W | 解像度変更+再エンコード (`cached=9`) |
| **`768p_4step_warm`** (1344×768, 4-step) | 42 | **49.390 s** | 49.692 s | 23,811 MiB | 245.6 / 407.6 W | モデル・プロンプトキャッシュ済み (`cached=11`) |

- Spark-Attn SM89 (`MiniMaxH3SparkAttentionSM89`, `mode=speed`, `topk_ratio=0.2`) は全50ブロックで動作し、`unexpected_fallbacks=[]` を確認。
- 4本すべてのウォーム出力MP4で `124 frames`, `24fps`, `AAC 32000Hz stereo`, `blackdetect=[]` を確認。
"""
    (EXP_DIR / "README.ja.md").write_text(readme_ja, encoding="utf-8")
    (EXP_DIR / "README.md").write_text(readme_ja, encoding="utf-8")

    print("GENERATED:", contact_jpg, contact_jpg.stat().st_size)
    print("GENERATED:", manifest_json, manifest_json.stat().st_size)
    print("GENERATED:", comp_jpg, comp_jpg.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
