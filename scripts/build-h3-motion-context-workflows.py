#!/usr/bin/env python3
"""Generate reproducible API workflows for the MiniMax-H3 motion-context test."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def link(node_id: int, output: int = 0) -> list[object]:
    return [str(node_id), output]


def node(class_type: str, **inputs: object) -> dict[str, object]:
    return {"class_type": class_type, "inputs": inputs}


def build_segment(
    *,
    segment: int,
    width: int,
    height: int,
    length: int,
    seed: int,
    prompt: str,
    previous_input: str | None,
    context_source_clip: int | None,
) -> dict[str, dict[str, object]]:
    """Build one API prompt; segments after the first consume the prior output."""

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
        # Generic FP16 CUDA SageAttention was the stable path in the preceding
        # ref2va benchmark; Spectrum and EasyCache are intentionally omitted so
        # the continuation test isolates Motion Context behaviour.
        "5": node("MiniMaxH3ImageToVideo", clip=link(2), vae=link(3), prompt=prompt,
                   width=width, height=height, length=length),
        "6": node("PathchSageAttentionKJ", model=link(1),
                   sage_attention="sageattn_qk_int8_pv_fp16_cuda", allow_compile=False),
        "7": node("BasicGuider", model=link(model), conditioning=link(5)),
        "8": node("KSamplerSelect", sampler_name="res_multistep"),
        "9": node("BasicScheduler", model=link(model), scheduler="simple",
                   steps=20, denoise=1.0),
        "10": node("RandomNoise", noise_seed=seed),
        "11": node("SamplerCustomAdvanced", noise=link(10), guider=link(7),
                    sampler=link(8), sigmas=link(9), latent_image=link(5, 1)),
        "12": node("VAEDecode", samples=link(11), vae=link(3)),
        "13": node("VAEDecodeAudio", samples=link(11, 1), vae=link(4)),
        "14": node("MiniMaxH3MotionContextSaveLatent", latent=link(11),
                    filename_prefix="h3_context/clip", clip_index=segment),
    }

    if previous_input is None:
        video_input = link(12)
        audio_input = link(13)
    else:
        if context_source_clip is None:
            raise ValueError("context_source_clip is required after segment 1")
        nodes.update(
            {
                "15": node("LoadVideo", file=previous_input),
                "16": node("GetVideoComponents", video=link(15)),
                "17": node("MiniMaxH3MotionContextLoadLatent",
                            latent_path="h3_context", clip_index=context_source_clip),
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
                filename_prefix=f"video/h3_motion_context/segment_{segment:02d}",
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
    parser.add_argument("--seed", type=int, default=2026080909)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    prompts = [
        (
            124,
            "A cinematic live-action shot in a warm Japanese cafe at night. "
            "A young woman in a floral dress walks slowly between wooden tables "
            "while the camera tracks backward at eye level. Natural cafe ambience, "
            "soft music, subtle conversations and room tone, realistic motion, "
            "consistent lighting, no dialogue, no text, no subtitles.",
        ),
        (
            124,
            "Continue directly from the previous clip with the exact same woman, "
            "cafe, lighting, camera direction and soundtrack. She keeps walking "
            "forward between the tables, passing a waiter and turning slightly "
            "toward the counter. Preserve continuous body motion, tempo and audio "
            "without a reset, realistic live-action cinematography, no dialogue, "
            "no text, no subtitles.",
        ),
        (
            141,
            "Continue directly from the previous clip with no visible reset. The "
            "same woman reaches the cafe counter, slows, and looks toward the warm "
            "window while the camera eases to a gentle stop. Preserve the exact "
            "motion direction, ambience, music waveform and lighting across the "
            "join, realistic live-action cinematography, no dialogue, no text, "
            "no subtitles.",
        ),
    ]

    manifest = {
        "experiment": "MiniMax-H3 Motion Context three-segment chain",
        "sourceRepository": "https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context",
        "sourceCommit": "15fc6a7bf7b78efb27f33d7eef3818e7ed0e118a",
        "sourcePost": "https://x.com/photogenicweeke/status/2085848283138891926?s=46",
        "gpuService": "h3-4090",
        "resolution": [args.width, args.height],
        "fps": 24,
        "steps": 20,
        "seed": args.seed,
        "contextLength": 22,
        "audioContextLength": 22,
        "encodeMode": "video",
        "anchorMode": "head",
        "audioMode": "timeline",
        "optimizerIsolation": "generic FP16 CUDA SageAttention only; EasyCache/Spectrum/Sol-Attn disabled",
        "segments": [],
    }

    previous_input = None
    for segment, (length, prompt) in enumerate(prompts, start=1):
        filename = f"segment_{segment:02d}_api.json"
        workflow = build_segment(
            segment=segment,
            width=args.width,
            height=args.height,
            length=length,
            seed=args.seed,
            prompt=prompt,
            previous_input=previous_input,
            context_source_clip=segment - 1 if segment > 1 else None,
        )
        (args.output_dir / filename).write_text(
            json.dumps(workflow, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        manifest["segments"].append(
            {
                "segment": segment,
                "generatedFrames": length,
                "generatedSeconds": round(length / 24, 6),
                "contextFrames": 0 if segment == 1 else 22,
                "expectedTrimmedFrames": length if segment == 1 else length - 22,
                "inputVideo": previous_input,
                "workflow": filename,
                "prompt": prompt,
            }
        )
        previous_input = f"h3_motion_context/segment_{segment:02d}.mp4"

    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"outputDir": str(args.output_dir), "segments": 3}, ensure_ascii=False))


if __name__ == "__main__":
    main()
