#!/usr/bin/env python3
"""Build a reproducible MiniMax-H3 Motion Context workflow chain for a Japanese cat-cafe vlog."""

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
            filename_prefix="h3_cat_cafe_vlog/clip",
            clip_index=segment,
        ),
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
                "17": node(
                    "MiniMaxH3MotionContextLoadLatent",
                    latent_path="h3_cat_cafe_vlog",
                    clip_index=context_source_clip,
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
                filename_prefix=f"video/h3_cat_cafe_vlog/segment_{segment:02d}",
                format="mp4",
                codec="auto",
            ),
        }
    )
    return nodes


PROMPTS = [
    (
        158,
        """A realistic handheld Japanese lifestyle vlog at a cozy Tokyo cat cafe in the late afternoon. A cheerful Japanese woman in her mid-20s is a non-specific social-media influencer, with shoulder-length warm brown hair, a cream cardigan over a pastel blue T-shirt, a small cat-shaped tote bag, and natural makeup. Keep her identity, outfit, voice, camera style and color grade consistent across every segment. She films herself at arm's length with a phone-sized vlog camera, then turns toward the cafe entrance. Warm wood, soft window light, several calm cats, realistic handheld motion, natural room tone, soft royalty-free acoustic background music. She smiles and speaks naturally in Japanese: 「今日は東京の猫カフェに来ました！たっぷり癒やされてきます」. Preserve clear Japanese speech, no subtitles, no on-screen text, no logos.""",
    ),
    (
        158,
        """Continue directly from the previous cat-cafe vlog clip with the exact same Japanese woman, warm brown hair, cream cardigan, pastel blue T-shirt, tote bag, voice, handheld camera and late-afternoon lighting. She enters the same Tokyo cat cafe, sanitizes her hands, and a friendly orange tabby cat with white paws and a small blue collar walks up to greet her. The camera follows from selfie view to a gentle over-the-shoulder view. Keep the same room layout, acoustic music, cafe ambience and natural handheld rhythm with no visible reset. She speaks naturally in Japanese: 「入ってすぐ、この子が来てくれた！めちゃくちゃ人懐っこい」. Include soft cat meows and purring, clear Japanese speech, no subtitles, no on-screen text, no logos.""",
    ),
    (
        158,
        """Continue directly from the previous clip with no reset. The same Japanese influencer, outfit, voice, orange tabby cat with white paws and blue collar, Tokyo cat cafe, warm wood interior, window light, handheld phone-vlog camera and acoustic background music remain consistent. She sits on a low sofa and slowly pets the tabby while the camera moves into a close but natural selfie-and-cat shot. The cat relaxes and purrs, its tail moving gently. Preserve continuous body motion, realistic fur, stable face and matching room tone. She whispers happily in Japanese: 「見て、このゴロゴロ音。かわいすぎて動けない」. Keep Japanese speech understandable, include purring and soft cafe ambience, no subtitles, no on-screen text, no logos.""",
    ),
    (
        158,
        """Continue seamlessly from the previous cat-cafe vlog segment with the same Japanese woman, same clothes, same voice, same orange tabby cat with white paws and blue collar, same warm Tokyo cafe and handheld camera. A staff member offers a small cat treat. The influencer holds it carefully and the tabby eats from her hand; she laughs softly while the camera makes a small playful push-in. Keep the background music, lighting, room tone, cat behavior and vlog color grade continuous, with realistic hands and natural motion. She says in Japanese: 「おやつタイムです。食べ方までかわいいんだけど！」. Include a quiet laugh, tiny cat sounds and clear Japanese speech, no subtitles, no on-screen text, no logos.""",
    ),
    (
        158,
        """Continue directly from the previous clip and finish the same Japanese influencer cat-cafe vlog without a visible reset. Keep the exact same woman, warm brown hair, cream cardigan, pastel blue T-shirt, tote bag, voice, orange tabby cat with white paws and blue collar, warm window light, cafe ambience and handheld phone camera. She plays briefly with a feather toy, then returns to selfie view near the entrance as the cat sits beside her. She waves to the camera, smiles with a relaxed satisfied expression, and the camera gently pulls back. Preserve continuous acoustic music and natural room tone. She gives a friendly Japanese outro: 「今日は本当に癒やされました。またこの子に会いに来ます！」. End with soft purring and a natural handheld stop, clear Japanese speech, no subtitles, no on-screen text, no logos.""",
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--width", type=int, default=1280)
    parser.add_argument("--height", type=int, default=704)
    parser.add_argument("--seed", type=int, default=2026080910)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "experiment": "MiniMax-H3 Japanese cat-cafe influencer vlog Motion Context chain",
        "sourceExperiment": "experiments/05-temporal-continuity/motion-context-3segment",
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
        "language": "Japanese dialogue and narration",
        "segments": [],
    }

    previous_input = None
    for segment, (length, prompt) in enumerate(PROMPTS, start=1):
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
                "expectedOutputSeconds": round((length if segment == 1 else length - 22) / 24, 6),
                "inputVideo": previous_input,
                "workflow": filename,
                "prompt": prompt,
            }
        )
        previous_input = f"h3_cat_cafe_vlog/segment_{segment:02d}.mp4"

    expected_frames = 158 + 4 * (158 - 22)
    manifest["expectedChainFrames"] = expected_frames
    manifest["expectedChainSeconds"] = round(expected_frames / 24, 6)
    (args.output_dir / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"outputDir": str(args.output_dir), "segments": len(PROMPTS), "expectedSeconds": expected_frames / 24}, ensure_ascii=False))


if __name__ == "__main__":
    main()
