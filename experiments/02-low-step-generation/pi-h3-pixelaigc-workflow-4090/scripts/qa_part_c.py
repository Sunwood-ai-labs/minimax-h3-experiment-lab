#!/usr/bin/env python3
"""QA and visual comparison sheet for Part C (1080p native + long FL2VA)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from PIL import Image

from qa_and_previews import (
    ARTIFACT_DIR,
    INPUT_DIR,
    PREVIEWS_DIR,
    RUNS_DIR,
    extract_frame,
    make_grid,
    probe_video,
)


def main() -> int:
    part_c = json.loads((RUNS_DIR / "part_c_results.json").read_text(encoding="utf-8"))
    qa_map: dict[str, dict] = {}
    vid_map: dict[str, Path] = {}

    for rec in part_c["runs"]:
        rid = rec["run_id"]
        outs = rec.get("outputs") or []
        if rec["status"] != "success" or not outs:
            continue
        p = Path(outs[0]["host_path"])
        if p.exists():
            vid_map[rid] = p
            qa_map[rid] = probe_video(p)
            print(
                f"[QA] {rid}: {qa_map[rid]['video']} dur={qa_map[rid]['duration_s']}s "
                f"rms={qa_map[rid]['audio']['rms_db_overall']}dB black={qa_map[rid]['blackdetect_count']} "
                f"size={qa_map[rid]['size_mb']}MB"
            )

    (RUNS_DIR / "media_qa_part_c.json").write_text(
        json.dumps(qa_map, indent=2, ensure_ascii=False), encoding="utf-8"
    )

    tmp_dir = PREVIEWS_DIR / "_frames_part_c"
    tmp_dir.mkdir(exist_ok=True)

    # 1. 1080p native 5s Sol-Attn strip
    if "1080p_native_5s_2step_sol" in vid_map:
        p = vid_map["1080p_native_5s_2step_sol"]
        frames = [
            (f"t = {t:.1f}s", extract_frame(p, t, tmp_dir / f"1080p_native_{t:.1f}.png"))
            for t in (0.5, 2.0, 3.5, 5.0)
        ]
        out_1080 = PREVIEWS_DIR / "compare_1080p_native_sol.jpg"
        make_grid([("1080p Native\n(1920x1088->1080)\n5s 2-step Sol\n(100.2s)", frames)], 400, 225, out_1080)
        shutil.copy2(out_1080, ARTIFACT_DIR / out_1080.name)
        print("Saved:", out_1080)

    # 2. Long FL2VA (10s & 30s) transition comparison
    first_im = Image.open(INPUT_DIR / "fl2va_first_night_rain.png").convert("RGB")
    last_im = Image.open(INPUT_DIR / "fl2va_last_morning_sun.png").convert("RGB")
    blank = Image.new("RGB", (320, 180), (28, 32, 42))

    rows = [
        (
            "Input Reference\n(First & Last)",
            [("First Frame", first_im), ("", blank), ("(Long Transition)", blank), ("", blank), ("Last Frame", last_im)],
        )
    ]

    fl_specs = [
        ("FL2VA 768p 10s\n2-step Sol-Attn\n(106.3s)", "fl2va_768p_10s_2step_sol", [0.05, 2.5, 5.0, 7.5, 10.0]),
        ("FL2VA 768p 10s\n4-step Spark SM89\n(133.2s)", "fl2va_768p_10s_4step_spark", [0.05, 2.5, 5.0, 7.5, 10.0]),
        ("FL2VA 480p 30s\n2-step Sol-Attn\n(347.2s)", "fl2va_480p_30s_2step_sol", [0.1, 7.5, 15.0, 22.5, 29.8]),
    ]
    for label, rid, times in fl_specs:
        if rid not in vid_map:
            continue
        frames = [
            (f"t = {t:.1f}s", extract_frame(vid_map[rid], t, tmp_dir / f"{rid}_{t:.2f}.png"))
            for t in times
        ]
        rows.append((label, frames))

    out_fl = PREVIEWS_DIR / "compare_fl2va_long_10s_30s.jpg"
    make_grid(rows, 320, 180, out_fl)
    shutil.copy2(out_fl, ARTIFACT_DIR / out_fl.name)
    print("Saved:", out_fl)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
