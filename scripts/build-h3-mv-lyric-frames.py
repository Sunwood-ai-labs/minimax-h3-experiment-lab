#!/usr/bin/env python3
"""Build the five seek-safe HyperFrames lyric overlay sub-compositions."""

from __future__ import annotations

import argparse
import html
import json
from pathlib import Path


FRAMES = [
    ("01-f01-rooftop", 0.000, 6.583, "夜を越えて　光を探す", "ROOFTOP / FIRST LIGHT"),
    ("02-f02-alley", 6.583, 12.250, "君となら　まだ飛べる", "NEON ALLEY / KEEP MOVING"),
    ("03-f03-underpass", 12.250, 17.917, "雨の向こう　夢が見える", "UNDERPASS / RAIN MEMORY"),
    ("04-f04-bridge", 17.917, 23.583, "この瞬間を　抱きしめて", "BRIDGE / PERFORMANCE PEAK"),
    ("05-f05-dawn", 23.583, 29.256, "明日へ行こう　また会おう", "DAWN ROOFTOP / OUTRO"),
]


def chars(text: str) -> str:
    out = []
    for char in text:
        if char == "　":
            out.append('<span class="char char-space">　</span>')
        else:
            out.append(f'<span class="char">{html.escape(char)}</span>')
    return "".join(out)


def build_frame(
    *,
    comp_id: str,
    start: float,
    end: float,
    lyric: str,
    scene_label: str,
    audio_frames: list[dict[str, object]],
    audio_fps: int,
    frame_number: int,
) -> str:
    duration = round(end - start, 3)
    # The filename-derived composition id must stay unchanged for the
    # assembler, but DOM ids should start with a letter for CSS safety.
    root_id = f"hf-{comp_id}-root"
    shell_id = f"hf-{comp_id}-shell"
    kicker_id = f"hf-{comp_id}-kicker"
    line_id = f"hf-{comp_id}-line"
    sub_id = f"hf-{comp_id}-sub"
    rule_id = f"hf-{comp_id}-rule"
    chars_html = chars(lyric)

    start_index = max(0, int(round(start * audio_fps)))
    end_index = min(len(audio_frames), int(round(end * audio_fps)) + 1)
    local_audio = []
    for index in range(start_index, end_index):
        frame = audio_frames[index]
        local_audio.append(
            {
                "t": round(float(frame.get("time", index / audio_fps)) - start, 4),
                "rms": float(frame.get("rms", 0.0)),
                "bass": float((frame.get("bands") or [0.0])[0]),
                "mid": float((frame.get("bands") or [0.0] * 8)[5]),
            }
        )

    audio_json = json.dumps({"fps": audio_fps, "frames": local_audio}, ensure_ascii=False, separators=(",", ":"))
    scene_label_html = html.escape(scene_label)
    lyric_label_html = html.escape(lyric)

    return f'''<!doctype html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
  </head>
  <body>
    <template>
      <div id="{root_id}" data-composition-id="{comp_id}" data-start="0" data-duration="{duration}" data-width="1280" data-height="704">
        <style>
          #{root_id} {{
            --ink: #111111;
            --ink-alt: #1a1a18;
            --orange: #e85d26;
            --cream: #f0ece5;
            --muted: rgba(240, 236, 229, .68);
            --pulse: 0;
            position: relative;
            width: 100%;
            height: 100%;
            overflow: hidden;
            container-type: size;
            color: var(--cream);
            font-family: "Barlow", "Noto Sans JP", "Yu Gothic", sans-serif;
          }}

          @font-face {{ font-family: "Barlow"; src: local("Barlow"); }}
          @font-face {{ font-family: "Noto Sans JP"; src: local("Noto Sans JP"); }}
          @font-face {{ font-family: "Yu Gothic"; src: local("Yu Gothic"); }}
          @font-face {{ font-family: "IBM Plex Mono"; src: local("IBM Plex Mono"); }}

          #{shell_id} {{
            position: absolute;
            left: 7.5%;
            bottom: 10.5%;
            width: 76%;
            min-height: 18%;
            padding: 22px 34px 20px 38px;
            background: rgba(17, 17, 17, .78);
            border-left: 5px solid var(--orange);
            transform: scale(calc(1 + var(--pulse) * .018));
            transform-origin: left bottom;
          }}

          #{kicker_id} {{
            color: var(--orange);
            font-family: "IBM Plex Mono", monospace;
            font-size: 15px;
            font-weight: 500;
            letter-spacing: .14em;
            line-height: 1.2;
            text-transform: uppercase;
          }}

          #{line_id} {{
            display: flex;
            flex-wrap: nowrap;
            margin-top: 12px;
            color: var(--cream);
            font-size: 55px;
            font-weight: 700;
            letter-spacing: .035em;
            line-height: 1.12;
            white-space: nowrap;
          }}

          #{line_id} .char {{
            display: inline-block;
            will-change: transform, opacity;
          }}

          #{line_id} .char-space {{ width: .52em; }}

          #{sub_id} {{
            display: flex;
            justify-content: space-between;
            gap: 20px;
            margin-top: 12px;
            color: var(--muted);
            font-family: "IBM Plex Mono", monospace;
            font-size: 13px;
            letter-spacing: .09em;
            line-height: 1.3;
            text-transform: uppercase;
          }}

          #{rule_id} {{
            width: 100%;
            height: 2px;
            margin-top: 14px;
            background: var(--orange);
            transform-origin: left center;
          }}
        </style>

        <div id="{shell_id}" class="lyric-shell clip" data-start="0" data-duration="{duration}" data-track-index="2">
          <div id="{kicker_id}" class="kicker">H3 / MOTION CONTEXT · ORIGINAL MV · {frame_number:02d}</div>
          <div id="{line_id}" class="lyric-line" aria-label="{lyric_label_html}">{chars_html}</div>
          <div id="{sub_id}" class="lyric-sub"><span>{scene_label_html}</span><span>PLANNED LYRIC / 30 FPS AUDIO MAP</span></div>
          <div id="{rule_id}" class="lyric-rule"></div>
        </div>

        <script>
          const root = document.getElementById("{root_id}");
          const shell = document.getElementById("{shell_id}");
          const kicker = document.getElementById("{kicker_id}");
          const line = document.getElementById("{line_id}");
          const sub = document.getElementById("{sub_id}");
          const rule = document.getElementById("{rule_id}");
          const timeline = gsap.timeline({{ paused: true }});
          const lyricChars = Array.from(line.querySelectorAll(".char"));
          const AUDIO_DATA = {audio_json};

          timeline.fromTo(shell, {{ x: -42, opacity: 0 }}, {{ x: 0, opacity: 1, duration: .48, ease: "power3.out" }}, 0);
          timeline.fromTo(kicker, {{ y: 12, opacity: 0 }}, {{ y: 0, opacity: 1, duration: .34, ease: "power2.out" }}, .14);
          lyricChars.forEach((char, index) => {{
            timeline.fromTo(char,
              {{ y: 30, opacity: 0, rotation: index % 2 ? 2 : -2 }},
              {{ y: 0, opacity: 1, rotation: 0, duration: .38, ease: "back.out(1.35)" }},
              .26 + Math.min(index * .055, .72)
            );
          }});
          timeline.fromTo(sub, {{ y: 10, opacity: 0 }}, {{ y: 0, opacity: 1, duration: .3, ease: "power2.out" }}, .72);
          timeline.fromTo(rule, {{ scaleX: 0 }}, {{ scaleX: 1, duration: .72, ease: "power2.out" }}, .72);

          // Deterministic audio-reactive pulse from pre-extracted FFT bands.
          AUDIO_DATA.frames.forEach((frame) => {{
            timeline.to(root, {{ "--pulse": frame.rms, duration: 1 / AUDIO_DATA.fps, ease: "none" }}, Math.max(0, frame.t));
          }});

          window.__timelines = window.__timelines || {{}};
          window.__timelines["{comp_id}"] = timeline;
        </script>
      </div>
    </template>
  </body>
</html>
'''


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audio-data", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.audio_data.read_text(encoding="utf-8"))
    audio_frames = data["frames"]
    audio_fps = int(data["fps"])
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for number, (comp_id, start, end, lyric, label) in enumerate(FRAMES, start=1):
        target = args.output_dir / f"{comp_id}.html"
        target.write_text(
            build_frame(
                comp_id=comp_id,
                start=start,
                end=end,
                lyric=lyric,
                scene_label=label,
                audio_frames=audio_frames,
                audio_fps=audio_fps,
                frame_number=number,
            ),
            encoding="utf-8",
        )
        print(f"wrote {target}")


if __name__ == "__main__":
    main()
