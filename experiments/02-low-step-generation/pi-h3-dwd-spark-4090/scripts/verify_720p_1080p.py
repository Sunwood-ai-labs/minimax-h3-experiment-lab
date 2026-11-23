#!/usr/bin/env python3
"""Verify 720p and 1080p pi-H3 MP4 outputs and create visual comparison images."""

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
    ("720p_2step_warm", OUT_DIR / "720p_2step_warm_00001_.mp4"),
    ("720p_4step_warm", OUT_DIR / "720p_4step_warm_00001_.mp4"),
    ("1080p_upscaled_2step_warm", OUT_DIR / "1080p_upscaled_2step_warm_00001_.mp4"),
    ("1080p_upscaled_4step_warm", OUT_DIR / "1080p_upscaled_4step_warm_00001_.mp4"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest().upper()


def main() -> int:
    qa = {}
    probes = []
    for label, vp in WARM_VIDEOS:
        if not vp.is_file():
            raise FileNotFoundError(f"Missing video: {vp}")
        probe = json.loads(
            subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(vp)],
                stdin=subprocess.DEVNULL,
                text=True,
                timeout=15,
            )
        )
        bd = subprocess.run(
            ["ffmpeg", "-nostdin", "-v", "info", "-i", str(vp), "-vf", "blackdetect=d=0.1:pix_th=0.10", "-an", "-f", "null", "-"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=20,
        ).stderr
        black_lines = [l for l in bd.splitlines() if "blackdetect" in l]
        au = subprocess.run(
            ["ffmpeg", "-nostdin", "-v", "info", "-i", str(vp), "-af", "astats=metadata=0:reset=0", "-vn", "-f", "null", "-"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=20,
        ).stderr
        audio_lines = [l.strip() for l in au.splitlines() if any(k in l for k in ("Channel:", "RMS level dB", "Peak level dB"))]

        vs = next(s for s in probe["streams"] if s["codec_type"] == "video")
        aus = next(s for s in probe["streams"] if s["codec_type"] == "audio")
        dur = float(probe["format"]["duration"])
        probes.append({"width": int(vs["width"]), "height": int(vs["height"]), "duration": dur, "frames": int(vs["nb_frames"]), "fps": vs["avg_frame_rate"]})
        qa[label] = {
            "bytes": vp.stat().st_size,
            "sha256": sha256_file(vp),
            "video": {
                "codec": vs["codec_name"],
                "width": int(vs["width"]),
                "height": int(vs["height"]),
                "fps": vs["avg_frame_rate"],
                "frames": int(vs["nb_frames"]),
                "duration": round(dur, 6),
            },
            "audio": {
                "codec": aus["codec_name"],
                "sample_rate": int(aus["sample_rate"]),
                "channels": int(aus["channels"]),
                "duration": round(float(aus["duration"]), 6),
            },
            "blackdetect": black_lines,
            "astats": audio_lines[-6:],
        }
        print(f"=== {label}: {vs['width']}x{vs['height']} {vs['nb_frames']}f {aus['sample_rate']}Hz {aus['channels']}ch black={len(black_lines)} ===", flush=True)
        print("  astats:", audio_lines[-4:], flush=True)

    (EXP_DIR / "runs" / "media_qa_720p_1080p.json").write_text(json.dumps(qa, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    # 1. Contact sheet of 720p (2-step/4-step) & 1080p upscaled (2-step/4-step)
    previews_dir = EXP_DIR / "previews"
    contact_jpg = previews_dir / "contact-sheet-720p-1080p.jpg"
    cmd = ["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y"]
    filter_parts = []
    for idx, (_, vp) in enumerate(WARM_VIDEOS):
        cmd.extend(["-i", str(vp)])
        dur = probes[idx]["duration"]
        filter_parts.append(
            f"[{idx}:v]fps=8/{dur},scale=320:180:force_original_aspect_ratio=decrease,"
            f"pad=320:180:(ow-iw)/2:(oh-ih)/2:color=black,tile=4x2:padding=6:margin=6[sheet{idx}]"
        )
    sheets = "".join(f"[sheet{i}]" for i in range(len(WARM_VIDEOS)))
    filter_parts.append(f"{sheets}vstack=inputs={len(WARM_VIDEOS)}[contact]")
    cmd.extend(["-filter_complex", ";".join(filter_parts), "-map", "[contact]", "-frames:v", "1", "-q:v", "2", str(contact_jpg)])
    subprocess.run(cmd, stdin=subprocess.DEVNULL, check=True, timeout=30)

    # 2. High-res comparison at t=2.5s and t=4.5s: Left = 720p 4-step (1280x720), Right = 1080p upscaled 4-step (1920x1080)
    v720 = OUT_DIR / "720p_4step_warm_00001_.mp4"
    v1080 = OUT_DIR / "1080p_upscaled_4step_warm_00001_.mp4"
    comp_jpg = previews_dir / "compare_720p_vs_1080p_4step.jpg"
    subprocess.run(
        [
            "ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "error", "-y",
            "-ss", "2.5", "-i", str(v720), "-ss", "2.5", "-i", str(v1080),
            "-ss", "4.5", "-i", str(v720), "-ss", "4.5", "-i", str(v1080),
            "-filter_complex",
            "[0:v]scale=960:540[a];[1:v]scale=960:540[b];[2:v]scale=960:540[c];[3:v]scale=960:540[d];[a][b]hstack=inputs=2[top];[c][d]hstack=inputs=2[bot];[top][bot]vstack=inputs=2[out]",
            "-map", "[out]", "-frames:v", "1", "-q:v", "2", str(comp_jpg),
        ],
        stdin=subprocess.DEVNULL,
        check=True,
        timeout=30,
    )

    shutil.copy2(contact_jpg, ARTIFACT_DIR / "contact-sheet-720p-1080p.jpg")
    shutil.copy2(comp_jpg, ARTIFACT_DIR / "compare_720p_vs_1080p_4step.jpg")
    print("GENERATED:", contact_jpg, contact_jpg.stat().st_size)
    print("GENERATED:", comp_jpg, comp_jpg.stat().st_size)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
