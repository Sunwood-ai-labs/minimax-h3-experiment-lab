#!/usr/bin/env python3
"""Run ffprobe/ffmpeg QA and build visual comparison sheets for the sequel experiment."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

EXP_DIR = Path(r"D:\Prj\minimax-h3-compose\experiments\02-low-step-generation\pi-h3-pixelaigc-workflow-4090")
RUNS_DIR = EXP_DIR / "runs"
PREVIEWS_DIR = EXP_DIR / "previews"
ARTIFACT_DIR = Path(r"C:\Users\makim\.gemini\antigravity\brain\39a5eb2d-3b5e-464f-ad95-ad89ae10cda9")
INPUT_DIR = Path(r"D:\Prj\minimax-h3-compose\runtime\pih3-4090\input")

PREVIEWS_DIR.mkdir(parents=True, exist_ok=True)


def run_cmd(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", check=False)


def probe_video(path: Path) -> dict:
    p = run_cmd([
        "ffprobe", "-v", "error", "-print_format", "json",
        "-show_format", "-show_streams", str(path),
    ])
    info = json.loads(p.stdout) if p.stdout.strip() else {}
    v_stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "video"), {})
    a_stream = next((s for s in info.get("streams", []) if s.get("codec_type") == "audio"), {})

    # Audio stats
    a_res = run_cmd([
        "ffmpeg", "-hide_banner", "-i", str(path),
        "-af", "astats=metadata=0:reset=0", "-f", "null", "-",
    ])
    a_err = a_res.stderr
    rms = re.findall(r"RMS level dB:\s*([-\d.]+)", a_err)
    peak = re.findall(r"Peak level dB:\s*([-\d.]+)", a_err)

    # Blackdetect
    b_res = run_cmd([
        "ffmpeg", "-hide_banner", "-i", str(path),
        "-vf", "blackdetect=d=0.1:pix_th=0.10", "-an", "-f", "null", "-",
    ])
    blacks = re.findall(r"black_start:([0-9.]+)\s+black_end:([0-9.]+)\s+black_duration:([0-9.]+)", b_res.stderr)

    return {
        "file": str(path),
        "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
        "duration_s": round(float(info.get("format", {}).get("duration", 0.0)), 3),
        "video": {
            "codec": v_stream.get("codec_name"),
            "width": v_stream.get("width"),
            "height": v_stream.get("height"),
            "nb_frames": int(v_stream.get("nb_frames", 0)) if str(v_stream.get("nb_frames", "")).isdigit() else None,
            "r_frame_rate": v_stream.get("r_frame_rate"),
        },
        "audio": {
            "codec": a_stream.get("codec_name"),
            "sample_rate": a_stream.get("sample_rate"),
            "channels": a_stream.get("channels"),
            "rms_db_overall": float(rms[-1]) if rms else None,
            "peak_db_overall": float(peak[-1]) if peak else None,
        },
        "blackdetect_count": len(blacks),
    }


def extract_frame(video_path: Path, t_sec: float, out_png: Path) -> Image.Image:
    run_cmd([
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-ss", f"{t_sec:.3f}", "-i", str(video_path),
        "-frames:v", "1", str(out_png),
    ])
    return Image.open(out_png).convert("RGB")


def make_grid(rows: list[tuple[str, list[tuple[str, Image.Image]]]], tile_w: int, tile_h: int, out_path: Path) -> None:
    cols = max(len(r[1]) for r in rows)
    header_h = 34
    label_w = 240
    pad = 8
    total_w = label_w + cols * (tile_w + pad) + pad
    total_h = pad + len(rows) * (tile_h + header_h + pad)
    canvas = Image.new("RGB", (total_w, total_h), (18, 22, 30))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("arial.ttf", 18)
        font_sm = ImageFont.truetype("arial.ttf", 15)
    except Exception:
        font = ImageFont.load_default()
        font_sm = font

    for r_idx, (row_label, frames) in enumerate(rows):
        y0 = pad + r_idx * (tile_h + header_h + pad)
        draw.text((12, y0 + header_h + tile_h // 2 - 20), row_label, fill=(235, 240, 250), font=font)
        for c_idx, (col_label, img) in enumerate(frames):
            x0 = label_w + pad + c_idx * (tile_w + pad)
            draw.text((x0 + 4, y0 + 6), col_label, fill=(180, 200, 230), font=font_sm)
            resized = img.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
            canvas.paste(resized, (x0, y0 + header_h))

    canvas.save(out_path, quality=92)


def main() -> int:
    part_a = json.loads((RUNS_DIR / "part_a_results.json").read_text(encoding="utf-8"))
    part_b = json.loads((RUNS_DIR / "part_b_results.json").read_text(encoding="utf-8"))

    all_runs = part_a["runs"] + part_b["runs"]
    qa_map: dict[str, dict] = {}
    vid_map: dict[str, Path] = {}

    for rec in all_runs:
        run_id = rec["run_id"]
        outs = rec.get("outputs") or []
        if not outs:
            continue
        p = Path(outs[0]["host_path"])
        if p.exists():
            vid_map[run_id] = p
            qa_map[run_id] = probe_video(p)
            print(f"[QA] {run_id}: {qa_map[run_id]['video']} dur={qa_map[run_id]['duration_s']}s "
                  f"rms={qa_map[run_id]['audio']['rms_db_overall']}dB black={qa_map[run_id]['blackdetect_count']}")

    (RUNS_DIR / "media_qa.json").write_text(json.dumps(qa_map, indent=2, ensure_ascii=False), encoding="utf-8")

    tmp_dir = PREVIEWS_DIR / "_frames"
    tmp_dir.mkdir(exist_ok=True)

    # 1. Long-duration & Sol vs Spark comparison sheet
    long_rows = []
    long_specs = [
        ("768p 10s 4-step\nSol-Attn\n(196.0s)", "768p_10s_4step_sol", [0.5, 3.0, 6.0, 9.5]),
        ("768p 10s 4-step\nSpark-Attn SM89\n(124.7s)", "768p_10s_4step_spark", [0.5, 3.0, 6.0, 9.5]),
        ("480p 30s 2-step\nSol-Attn\n(336.8s)", "480p_30s_2step_sol", [1.0, 10.0, 20.0, 29.0]),
        ("480p 30s 2-step\nSpark-Attn SM89\n(346.0s)", "480p_30s_2step_spark", [1.0, 10.0, 20.0, 29.0]),
    ]
    for label, rid, times in long_specs:
        if rid not in vid_map:
            continue
        frames = []
        for t in times:
            im = extract_frame(vid_map[rid], t, tmp_dir / f"{rid}_{t:.1f}.png")
            frames.append((f"t = {t:.1f}s", im))
        long_rows.append((label, frames))

    out_long = PREVIEWS_DIR / "compare_sol_vs_spark_long.jpg"
    make_grid(long_rows, 384, 216, out_long)
    shutil.copy2(out_long, ARTIFACT_DIR / out_long.name)
    print("Saved:", out_long)

    # 2. FL2VA transition comparison sheet
    fl2va_rows = []
    first_im = Image.open(INPUT_DIR / "fl2va_first_night_rain.png").convert("RGB")
    last_im = Image.open(INPUT_DIR / "fl2va_last_morning_sun.png").convert("RGB")
    fl2va_specs = [
        ("FL2VA 768p 5s\n2-step Sol-Attn\n(143.2s cold)", "fl2va_768p_5s_2step_sol"),
        ("FL2VA 768p 5s\n4-step Sol-Attn\n(72.5s warm)", "fl2va_768p_5s_4step_sol"),
        ("FL2VA 768p 5s\n4-step Spark-Attn\n(54.6s warm)", "fl2va_768p_5s_4step_spark"),
    ]
    times_fl = [0.05, 1.3, 2.6, 3.9, 5.05]
    for label, rid in fl2va_specs:
        if rid not in vid_map:
            continue
        frames = []
        for t in times_fl:
            im = extract_frame(vid_map[rid], t, tmp_dir / f"{rid}_{t:.2f}.png")
            frames.append((f"t = {t:.2f}s", im))
        fl2va_rows.append((label, frames))

    # Prepend reference row showing input first/last frames at left/right
    blank = Image.new("RGB", (384, 216), (28, 32, 42))
    ref_row = (
        "Input Reference\n(First & Last)",
        [("Input First Frame", first_im), ("", blank), ("(Interpolated by H3)", blank), ("", blank), ("Input Last Frame", last_im)],
    )
    fl2va_rows.insert(0, ref_row)

    out_fl2va = PREVIEWS_DIR / "compare_fl2va_transition.jpg"
    make_grid(fl2va_rows, 320, 180, out_fl2va)
    shutil.copy2(out_fl2va, ARTIFACT_DIR / out_fl2va.name)
    print("Saved:", out_fl2va)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
