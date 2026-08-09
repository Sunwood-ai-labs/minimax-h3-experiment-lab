# MiniMax-H3 research notes

Japanese detailed log: [research-notes.md](./research-notes.md)

Checked: 2026-08-07 JST
Scope: X posts for RTX 3060 / RTX 4090, upstream documentation, and Docker Compose local verification.

## Conclusions

The first RTX 3060 MP4 was completely black. It came from the legacy Turbo/full-int8 + Kijai int8 video-VAE path and is retained as a separate failed record. It is not treated as a successful 3060 result.

The adopted 3060 reference is the [TlanoAI post](https://x.com/TlanoAI/status/2084940455809286397): RTX 3060 12 GB, ComfyUI 0.30.0, PyTorch 2.11.0+cu130, CUDA 13.0, SageAttention 2.2.0, pruned int8 base, NVFP4 text encoder, official FP16 video VAE, official FP32 audio VAE, Dynamic VRAM + CPU offload, EasyCache, SageAttention, 864×480, 124 frames, 24 fps, and 25 steps. The local Docker result completed normally at 424.660 seconds cold and 267.980 seconds warm inference.

The adopted 4090 source is the [yume_arasaki post](https://x.com/yume_arasaki/status/2084766655331360999) and its linked [recipe](https://github.com/yume-arasaki/RTX-4090-3090-Minimax-H3-15s). The post says approximately 842×480, 24 fps, 20 steps, and about 7 minutes for 5 seconds; the linked recipe specifies 832×480, pruned int8, NVFP4 text encoder, official FP16/FP32 VAEs, 20 steps, `res_multistep`, `simple`, aggressive CPU offload, and related flags. The local record uses the recipe dimensions, not the post dimensions.

After a WSL restart, RTX 3060 completed approximately 720p-class 1280×704 T2V and I2V without OOM. These are recorded as local results under the baseline experiment, not as an assertion about the original X post.

## X research boundary

| Candidate | Decision |
|---|---|
| [TlanoAI 3060](https://x.com/TlanoAI/status/2084940455809286397) | Adopted: enough runtime and model details for a partial-condition reproduction. |
| [yume_arasaki 4090](https://x.com/yume_arasaki/status/2084766655331360999) + [linked recipe](https://github.com/yume-arasaki/RTX-4090-3090-Minimax-H3-15s) | Adopted as a linked-recipe reproduction; 842×480 post dimensions and 832×480 recipe dimensions remain separate. |
| [lizikk_zhu](https://x.com/lizikk_zhu/status/2084859489115648336) | Context only; steps, sampler, scheduler, VAE, and offload details are incomplete. |
| [thekhoma](https://x.com/thekhoma/status/2084504336173076800) | Context only; major model and offload conditions are incomplete. |
| [onigirikila](https://x.com/onigirikila/status/2084858171462754672) | Context only; exact base, LoRA, VAE, and sampler are not known. |

The post's prompt, seed, sampler, scheduler, LoRA, and some VAE/offload values are not silently invented. When a local comparison requires them, the experiment record labels them as local fixed values.

## Docker conditions used for the adopted baseline

- Host: Windows 11 Pro + WSL2 + Docker Desktop
- Container: ComfyUI 0.30.0, Python 3.12.3, PyTorch 2.11.0+cu130, CUDA runtime 13.0, cuDNN 9
- RTX 3060: Dynamic VRAM, CPU offload, SageAttention, EasyCache; 864×480 reference run and 1280×704 post-restart follow-up
- RTX 4090: `memory_usage_factor=1.0`, pinned memory disabled, fp16 intermediates; 832×480 linked-recipe run and 1280×704 follow-up
- GPU UUIDs, driver, host memory, workflow hashes, model hashes, media probes, and timing evidence are preserved in the runtime benchmark reports.

See the bilingual [English/default GPU baseline record](./experiments/01-baseline/gpu-baseline/README.md), [Japanese record](./experiments/01-baseline/gpu-baseline/README.ja.md), and the [English lab guide](./LAB.en.md) for the reproducibility contract.
