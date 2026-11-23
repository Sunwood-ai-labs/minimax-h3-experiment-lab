import json
from pathlib import Path

PROMPT = (
    'integrated_multimodal_description: [Shot 1] Live-action, epic cinematic, '
    'a slow push-in through a dim, dusty server room overgrown with thick cobwebs, '
    'a single ancient computer monitor glowing at the center of the frame showing '
    'a progress bar stuck at "99%", a skeleton in an office chair slumped in front '
    'of it with one bony finger still on the mouse, dust drifting through a shaft '
    'of cold light. A deep, gravelly movie-trailer narrator (S1) says off-screen: '
    '<d>[English] In a world where your render outlived you...</d>\n\n'
    'overall_soundscape: A low electrical hum, the slow creak of the office chair, '
    'and a single cooling fan rattling and winding down.\n\n'
    'non_diegetic_music: Ominous low brass and taiko drums build slowly.'
)

CONFIGS = [
    ("pih3_dwd_spark_sm89_720p_2step_api.json", 1280, 736, 1280, 720, 2, 0.93, "pi_h3_2step_dwd_adapter_int8_convrot.safetensors", "none", 16384, "720p_2step"),
    ("pih3_dwd_spark_sm89_720p_4step_api.json", 1280, 736, 1280, 720, 4, 0.96, "pi_h3_4step_dwd_adapter_int8_convrot.safetensors", "none", 16384, "720p_4step"),
    ("pih3_dwd_spark_sm89_1080p_upscaled_2step_api.json", 1344, 768, 1920, 1080, 2, 0.93, "pi_h3_2step_dwd_adapter_int8_convrot.safetensors", "none", 16384, "1080p_upscaled_2step"),
    ("pih3_dwd_spark_sm89_1080p_upscaled_4step_api.json", 1344, 768, 1920, 1080, 4, 0.96, "pi_h3_4step_dwd_adapter_int8_convrot.safetensors", "none", 16384, "1080p_upscaled_4step"),
    ("pih3_dwd_spark_sm89_1080p_native_2step_api.json", 1920, 1088, 1920, 1080, 2, 0.93, "pi_h3_2step_dwd_adapter_int8_convrot.safetensors", "drop_k", 8192, "1080p_native_2step"),
    ("pih3_dwd_spark_sm89_1080p_native_4step_api.json", 1920, 1088, 1920, 1080, 4, 0.96, "pi_h3_4step_dwd_adapter_int8_convrot.safetensors", "drop_k", 8192, "1080p_native_4step"),
]


def build_workflow(
    gen_w: int,
    gen_h: int,
    out_w: int,
    out_h: int,
    steps: int,
    max_raw_t: float,
    adapter: str,
    chunk_path: str,
    producer_chunk: int,
    tag: str,
) -> dict:
    return {
        "1": {
            "class_type": "UNETLoader",
            "inputs": {
                "unet_name": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
                "weight_dtype": "default",
            },
        },
        "2": {
            "class_type": "Load LakonLab Adapter",
            "inputs": {
                "model": ["1", 0],
                "adapter_name": adapter,
                "adapter_strength": 1.0,
            },
        },
        "3": {
            "class_type": "CLIPLoader",
            "inputs": {
                "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors",
                "type": "minimax",
                "device": "default",
            },
        },
        "4": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "minimax_h3_video_vae_int8_convrot.safetensors",
            },
        },
        "5": {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": "minimax_h3_audio_vae_fp32.safetensors",
            },
        },
        "6": {
            "class_type": "MiniMaxH3ImageToVideo",
            "inputs": {
                "clip": ["3", 0],
                "vae": ["4", 0],
                "prompt": PROMPT,
                "width": gen_w,
                "height": gen_h,
                "length": 124,
            },
        },
        "7": {
            "class_type": "MiniMaxH3SigmaShift",
            "inputs": {
                "model": ["2", 0],
                "shift_video": 12.0,
                "shift_audio": 3.0,
            },
        },
        "8": {
            "class_type": "MiniMaxH3SparkAttentionSM89",
            "inputs": {
                "model": ["7", 0],
                "mode": "speed",
                "steps": steps,
                "warmup_mode": "warmup_ratio",
                "warmup_ratio": 0.0,
                "warmup_steps": 4,
                "topk_mode": "topk_ratio",
                "topk_ratio": 0.2,
                "topk_blocks": 228,
                "dense_layers": 0,
                "min_tokens": 12288,
                "strict": True,
                "dense_backend": "inherit",
                "tail_granularity": "query",
                "reblock_layout": "q_reuse_k",
                "sparse_scope": "target-video",
                "producer_chunk": producer_chunk,
                "chunk_path": chunk_path,
            },
        },
        "9": {
            "class_type": "pi-Flow Scheduler",
            "inputs": {
                "model": ["8", 0],
                "steps": steps,
                "min_raw_t": 0.0,
                "max_raw_t": max_raw_t,
                "final_step_size_scale": 0.6,
            },
        },
        "10": {
            "class_type": "BasicGuider",
            "inputs": {
                "model": ["8", 0],
                "conditioning": ["6", 0],
            },
        },
        "11": {
            "class_type": "KSamplerSelect",
            "inputs": {
                "sampler_name": "euler",
            },
        },
        "12": {
            "class_type": "RandomNoise",
            "inputs": {
                "noise_seed": 42,
            },
        },
        "13": {
            "class_type": "SamplerCustomAdvanced",
            "inputs": {
                "noise": ["12", 0],
                "guider": ["10", 0],
                "sampler": ["11", 0],
                "sigmas": ["9", 0],
                "latent_image": ["6", 1],
            },
        },
        "14": {
            "class_type": "DWD Decode",
            "inputs": {
                "samples": ["13", 0],
            },
        },
        "18": {
            "class_type": "ImageScale",
            "inputs": {
                "image": ["14", 0],
                "upscale_method": "lanczos",
                "width": out_w,
                "height": out_h,
                "crop": "center",
            },
        },
        "15": {
            "class_type": "VAEDecodeAudio",
            "inputs": {
                "samples": ["13", 0],
                "vae": ["5", 0],
            },
        },
        "16": {
            "class_type": "CreateVideo",
            "inputs": {
                "images": ["18", 0],
                "audio": ["15", 0],
                "fps": 24.0,
                "bit_depth": "auto",
                "color_space": "sRGB",
                "chroma_subsampling": "auto",
                "codec": "none",
            },
        },
        "17": {
            "class_type": "SaveVideo",
            "inputs": {
                "video": ["16", 0],
                "filename_prefix": f"video/pi-h3-4090/{tag}",
                "format": "mp4",
                "format.codec": "auto",
            },
        },
    }


def main() -> None:
    wf_dir = Path(__file__).resolve().parent.parent / "workflows"
    wf_dir.mkdir(parents=True, exist_ok=True)
    for cfg in CONFIGS:
        fname, gen_w, gen_h, out_w, out_h, steps, max_raw_t, adapter, chunk_path, p_chunk, tag = cfg
        out = wf_dir / fname
        out.write_text(
            json.dumps(
                build_workflow(gen_w, gen_h, out_w, out_h, steps, max_raw_t, adapter, chunk_path, p_chunk, tag),
                indent=2,
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"WROTE: {out}")


if __name__ == "__main__":
    main()
