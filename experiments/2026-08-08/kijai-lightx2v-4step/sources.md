# Sources — Kijai LightX2V 4-step LoRA

## Hugging Face: Kijai/MiniMax-H3_comfy

- URL: https://huggingface.co/Kijai/MiniMax-H3_comfy
- Revision checked: `37ae5cbe1d6f2243484812fc511f9fa427b12a30`
- README fact: `4 steps, 0.75 LoRA strength`
- README examples: `er_sde` and `sa_solver`
- README caveat: intended alpha is not confirmed; lower strength may help noisy outputs
- Full LoRA: `loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`, 1,956,171,984 bytes, LFS OID `fc9b6500f0331fe925b004738baaa31bd34104741c8bf9334816f9ac3005c8c1`
- Resized LoRA: `loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy_resized_avg_rank_21_bf16.safetensors`, 314,878,200 bytes, LFS OID `3a069f26fbc33f377a60dc72dd9e15f2aa42aa1d1b44915fded835716672dd36`

## X: SD_Tutorial

- URL: https://x.com/sd_tutorial/status/2085760369612783646
- Author: `@SD_Tutorial`
- Published: `2026-08-07T16:09:58Z`
- Text: `Kija's repacked Lightx2v's H3 turbo lora for Comfy support:👇`
- Links in the post: Kijai Comfy repository and LightX2V source repository
- Attached video public metadata: 1344×768, 6,583 ms; this does not expose the generation sampler
- Public MP4 variant inspected with ffprobe: 630×360, 158 video frames, 24 fps, 6.656 seconds. The 630×360 dimensions are a delivery variant; the X metadata reports the original 1344×768.

## Upstream LightX2V

- URL: https://huggingface.co/lightx2v/Minimax-h3-Turbo/tree/main
- Revision checked: `b65e359c0d128b3c5e08e0f5bf2791b794378588`
- File: `minimax_h3_fl2v_turbo_4step_v0.1.safetensors`, 1,383,677,888 bytes, LFS OID `5ff4a12c8b4599fec716e1b15a45e504e0d1129111896bdcde5ac4a15e395b29`
- README points to https://github.com/ModelTC/Minimax-H3-Turbo for reproduction

## Interpretation boundary

The 4-step and 0.75 strength values are directly stated by Kijai. Resolution and duration are read from X's public media metadata. GPU, prompt, seed, sampler, scheduler, frame count, VAE, and offload settings remain unreported by the post and must be treated as local experiment choices.
