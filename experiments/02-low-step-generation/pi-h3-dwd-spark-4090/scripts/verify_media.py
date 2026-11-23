#!/usr/bin/env python3
"""Verify generated pi-H3 MP4 files (video + audio streams, blackdetect, signalstats, astats) and build 768p comparison image."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

OUT_DIR = Path(r"D:\Prj\minimax-h3-compose\runtime\pih3-4090\output\video\pi-h3-4090")
EXP_DIR = Path(r"D:\Prj\minimax-h3-compose\experiments\02-low-step-generation\pi-h3-dwd-spark-4090")
ARTIFACT_DIR = Path(r"C:\Users\makim\.gemini\antigravity\brain\147bd0aa-f4bc-4be4-b4a0-4800d6d2d9f1")

VIDEOS = [
    "480p_2step_warm_00001_.mp4",
    "480p_4step_warm_00001_.mp4",
    "768p_2step_warm_00001_.mp4",
    "768p_4step_warm_00001_.mp4",
]


def main() -> int:
    report = {}
    for name in VIDEOS:
        p = OUT_DIR / name
        if not p.is_file():
            raise FileNotFoundError(f"Missing video: {p}")

        probe = json.loads(
            subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(p)],
                text=True,
            )
        )
        bd = subprocess.run(
            ["ffmpeg", "-v", "info", "-i", str(p), "-vf", "blackdetect=d=0.1:pix_th=0.10", "-an", "-f", "null", "-"],
            capture_output=True,
            text=True,
        ).stderr
        black_lines = [l for l in bd.splitlines() if "blackdetect" in l]

        ss = subprocess.run(
            [
                "ffmpeg",
                "-v",
                "info",
                "-i",
                str(p),
                "-vf",
                "select='eq(n,0)+eq(n,60)+eq(n,120)',signalstats,metadata=print",
                "-an",
                "-f",
                "null",
                "-",
            ],
            capture_output=True,
            text=True,
        ).stderr
        stats_lines = [
            l.strip()
            for l in ss.splitlines()
            if any(k in l for k in ("frame:", "YMIN=", "YAVG=", "YMAX=", "SATAVG="))
        ]

        au = subprocess.run(
            ["ffmpeg", "-v", "info", "-i", str(p), "-af", "astats=metadata=0:reset=0", "-vn", "-f", "null", "-"],
            capture_output=True,
            text=True,
        ).stderr
        audio_lines = [
            l.strip()
            for l in au.splitlines()
            if any(k in l for k in ("Channel:", "RMS level dB", "Peak level dB", "Flat factor"))
        ]

        report[name] = {
            "bytes": p.stat().st_size,
            "streams": probe.get("streams", []),
            "format": probe.get("format", {}),
            "blackdetect": black_lines,
            "signalstats": stats_lines,
            "astats": audio_lines,
        }
        print(f"=== {name} ({p.stat().st_size} bytes) ===", flush=True)
        for s in probe.get("streams", []):
            print(
                f"  stream[{s.get('index')}]: type={s.get('codec_type')} codec={s.get('codec_name')} "
                f"w={s.get('width')} h={s.get('height')} fps={s.get('r_frame_rate')} "
                f"frames={s.get('nb_frames')} sr={s.get('sample_rate')} ch={s.get('channels')} dur={s.get('duration')}",
                flush=True,
            )
        print("  blackdetect:", black_lines, flush=True)
        print("  signalstats:", stats_lines[:12], flush=True)
        print("  astats:", audio_lines[-8:], flush=True)

    (EXP_DIR / "runs" / "media_qa.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )

    # Create side-by-side 768p 2-step vs 4-step comparison at t=2.5s (frame 60) and t=4.5s (frame 108)
    v2 = OUT_DIR / "768p_2step_warm_00001_.mp4"
    v4 = OUT_DIR / "768p_4step_warm_00001_.mp4"
    comp_path = EXP_DIR / "previews" / "compare_768p_2step_vs_4step.jpg"
    comp_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg",
            "-y",
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
                "[0:v]drawtext=text='768p 2-step (32.3s) t=2.5s':x=20:y=20:fontsize=32:fontcolor=white:box=1:boxcolor=black@0.65[a];"
                "[1:v]drawtext=text='768p 4-step (49.4s) t=2.5s':x=20:y=20:fontsize=32:fontcolor=white:box=1:boxcolor=black@0.65[b];"
                "[2:v]drawtext=text='768p 2-step (32.3s) t=4.5s':x=20:y=20:fontsize=32:fontcolor=white:box=1:boxcolor=black@0.65[c];"
                "[3:v]drawtext=text='768p 4-step (49.4s) t=4.5s':x=20:y=20:fontsize=32:fontcolor=white:box=1:boxcolor=black@0.65[d];"
                "[a][b]hstack=inputs=2[top];[c][d]hstack=inputs=2[bot];[top][bot]vstack=inputs=2[out]"
            ),
            "-map",
            "[out]",
            "-frames:v",
            "1",
            "-q:v",
            "2",
            str(comp_path),
        ],
        check=True,
    )
    print("WROTE:", comp_path, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
