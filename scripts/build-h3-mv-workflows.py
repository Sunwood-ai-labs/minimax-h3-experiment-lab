#!/usr/bin/env python3
"""Generate reproducible MiniMax-H3 Motion Context workflows for an MV test."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def link(node_id: int, output: int = 0) -> list[object]:
    return [str(node_id), output]


def node(class_type: str, **inputs: object) -> dict[str, object]:
    return {"class_type": class_type, "inputs": inputs}


LYRICS = [
    "夜を越えて　光を探す",
    "君となら　まだ飛べる",
    "雨の向こう　夢が見える",
    "この瞬間を　抱きしめて",
    "明日へ行こう　また会おう",
]


PROMPTS = [
    (
        "A cinematic live-action Japanese pop music video at night. A non-specific "
        "Japanese woman in her mid-20s is the singer, with shoulder-length black "
        "hair, one silver hair clip, a black satin jacket over a deep red dress, "
        "and a small silver ear cuff. She performs on a rain-wet Tokyo rooftop "
        "surrounded by amber and crimson neon, then starts walking toward a stairway "
        "as the camera makes a smooth backward dolly. Original upbeat synth-pop and "
        "alt-pop instrumental, steady tempo, female Japanese vocals singing exactly "
        "「夜を越えて　光を探す」, no spoken dialogue. Preserve the singer, outfit, "
        "melody, tempo, lighting and cinematic color grade for every segment. "
        "Realistic music-video cinematography, expressive performance, no subtitles, "
        "no on-screen text, no logos."
    ),
    (
        "Continue directly from the previous Japanese pop music video segment with "
        "the exact same singer, black hair, silver hair clip, black satin jacket, "
        "deep red dress, ear cuff, vocal tone, synth-pop melody and camera direction. "
        "She descends the neon stairway into a rain-soaked Tokyo alley, singing and "
        "moving with confident choreography while the camera tracks beside her. Keep "
        "the same amber-crimson lighting, wet reflections, beat, instrumental texture "
        "and vocal continuity with no reset. Female Japanese vocals sing exactly "
        "「君となら　まだ飛べる」, no spoken dialogue, no subtitles, no on-screen "
        "text, no logos, realistic live-action music-video style."
    ),
    (
        "Continue seamlessly from the previous segment with no visible reset. The "
        "same Japanese singer, outfit, face, hair clip, ear cuff, vocal tone and "
        "synth-pop song continue in the same rainy Tokyo night. She reaches a quiet "
        "underpass with moving red and gold light, turns toward the camera and sings "
        "while the camera makes a slow half-orbit; rain trails and reflections move "
        "naturally. Preserve the exact melody, tempo, room tone, reverb and lighting "
        "across the join. Female Japanese vocals sing exactly 「雨の向こう　夢が見える」, "
        "no spoken dialogue, no subtitles, no on-screen text, no logos."
    ),
    (
        "Continue directly from the previous Japanese pop music video segment. Keep "
        "the same singer, black hair, silver clip, black satin jacket, deep red dress, "
        "ear cuff, song arrangement and vocal performance. She exits the underpass onto "
        "a pedestrian bridge above the city, performs a restrained but energetic dance "
        "phrase as the camera arcs around her, and the neon city bokeh blooms behind "
        "her. Maintain continuous beat, melody, vocal texture, wet-night color and "
        "camera energy without a reset. Female Japanese vocals sing exactly "
        "「この瞬間を　抱きしめて」, no spoken dialogue, no subtitles, no on-screen "
        "text, no logos."
    ),
    (
        "Finish the same Japanese pop music video with no visible identity reset. Keep "
        "the exact same Japanese singer, outfit, hair, silver clip, ear cuff, vocal "
        "tone, synth-pop melody and cinematic grade. The camera follows her from the "
        "bridge back to a rooftop as the rain eases and a soft pre-dawn blue mixes with "
        "the last amber neon. She faces the camera, sings the final phrase, then lowers "
        "her hand as the camera gently pulls back to a glowing city horizon. Preserve "
        "the continuous instrumental, beat and reverb. Female Japanese vocals sing "
        "exactly 「明日へ行こう　また会おう」, no spoken dialogue, no subtitles, no "
        "on-screen text, no logos."
    ),
]


def build_segment(
    *,
    segment: int,
    width: int,
    height: int,
    length: int,
    seed: int,
    prompt: str,
    previous_input: str | None,
) -> dict[str, dict[str, object]]:
    model = 6
    nodes: dict[str, dict[str, object]] = {
        "1": node(
            "UNETLoader",
            unet_name="minimax_h3_fl2va_pruned_int8_convrot.safetensors",
            weight_dtype="default",
        ),
        "2": node(
            "CLIPLoader",
            clip_name="qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
            type="minimax",
            device="default",
        ),
        "3": node("VAELoader", vae_name="minimax_h3_video_vae_fp16.safetensors"),
        "4": node("VAELoader", vae_name="minimax_h3_audio_vae_fp32.safetensors"),
        "5": node(
            "MiniMaxH3ImageToVideo",
            clip=link(2),
            vae=link(3),
            prompt=prompt,
            width=width,
            height=height,
            length=length,
        ),
        "6": node(
            "PathchSageAttentionKJ",
            model=link(1),
            sage_attention="sageattn_qk_int8_pv_fp16_cuda",
            allow_compile=False,
        ),
        "7": node("BasicGuider", model=link(model), conditioning=link(5)),
        "8": node("KSamplerSelect", sampler_name="res_multistep"),
        "9": node(
            "BasicScheduler",
            model=link(model),
            scheduler="simple",
            steps=20,
            denoise=1.0,
        ),
        "10": node("RandomNoise", noise_seed=seed),
        "11": node(
            "SamplerCustomAdvanced",
            noise=link(10),
            guider=link(7),
            sampler=link(8),
            sigmas=link(9),
            latent_image=link(5, 1),
        ),
        "12": node("VAEDecode", samples=link(11), vae=link(3)),
        "13": node("VAEDecodeAudio", samples=link(11, 1), vae=link(4)),
        "14": node(
            "MiniMaxH3MotionContextSaveLatent",
            latent=link(11),
            filename_prefix="h3_mv/mv_clip",
            clip_index=segment,
        ),
    }

    if previous_input is None:
        video_input = link(12)
        audio_input = link(13)
    else:
        nodes.update(
            {
                "15": node("LoadVideo", file=previous_input),
                "16": node("GetVideoComponents", video=link(15)),
                "17": node(
                    "MiniMaxH3MotionContextLoadLatent",
                    latent_path="h3_mv",
                    clip_index=segment - 1,
                ),
                "18": node(
                    "MiniMaxH3MotionContext",
                    conditioning=link(5),
                    vae=link(3),
                    latent=link(5, 1),
                    context_frames=link(16),
                    context_length=22,
                    encode_mode="video",
                    anchor_mode="head",
                    crop="disabled",
                    audio_context_length=22,
                    audio_mode="timeline",
                    context_latent=link(17),
                ),
                "19": node(
                    "MiniMaxH3MotionContextTrim",
                    images=link(12),
                    trim_frames=link(18, 1),
                    audio=link(13),
                    fps=24.0,
                    match_tail=True,
                ),
            }
        )
        nodes["7"]["inputs"]["conditioning"] = link(18)
        video_input = link(19)
        audio_input = link(19, 1)

    nodes.update(
        {
            "20": node("CreateVideo", images=video_input, audio=audio_input, fps=24.0),
            "21": node(
                "SaveVideo",
                video=link(20),
                filename_prefix=f"video/h3_mv/segment_{segment:02d}",
                format="mp4",
                codec="auto",
            ),
        }
    )
    return nodes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=704)
    parser.add_argument("--seed", type=int, default=2026080911)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "experiment": "MiniMax-H3 Motion Context Japanese synth-pop MV",
        "sourceRepository": "https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context",
        "sourceCommit": "15fc6a7bf7b78efb27f33d7eef3818e7ed0e118a",
        "gpuService": "h3-4090",
        "resolution": [args.width, args.height],
        "fps": 24,
        "steps": 20,
        "sampler": "res_multistep",
        "scheduler": "simple",
        "seed": args.seed,
        "contextLength": 22,
        "audioContextLength": 22,
        "encodeMode": "video",
        "anchorMode": "head",
        "audioMode": "timeline",
        "optimizerIsolation": "generic FP16 CUDA SageAttention only; EasyCache/Spectrum/Sol-Attn disabled",
        "music": {
            "style": "original Japanese synth-pop / alt-pop",
            "lyrics": LYRICS,
            "lyricsArePlannedText": True,
            "source": "MiniMax-H3 generated audio carried through Motion Context",
        },
        "segments": [],
    }

    previous_input = None
    for segment, (prompt, lyric) in enumerate(zip(PROMPTS, LYRICS), start=1):
        workflow = build_segment(
            segment=segment,
            width=args.width,
            height=args.height,
            length=158,
            seed=args.seed,
            prompt=prompt,
            previous_input=previous_input,
        )
        filename = f"segment_{segment:02d}_api.json"
        (args.output_dir / filename).write_text(
            json.dumps(workflow, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        manifest["segments"].append(
            {
                "segment": segment,
                "rawFrames": 158,
                "contextFrames": 0 if segment == 1 else 22,
                "lyric": lyric,
                "prompt": prompt,
                "workflow": filename,
                "previousInput": previous_input,
            }
        )
        previous_input = f"h3_mv/segment_{segment:02d}.mp4"

    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


if __name__ == "__main__":
    main()
