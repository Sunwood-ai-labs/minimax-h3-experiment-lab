# Sources and evidence

Japanese source note: [sources.md](./sources.md)

## Direct references

1. [Kijai/MiniMax-H3_comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy) — Kijai's ComfyUI distribution. The LoRA used here is `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`.
2. [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) — source for `minimax_h3_ref2va_pruned_int8_convrot.safetensors`.
3. [Related X reference](https://x.com/sd_tutorial/status/2085760369612783646) — the Kijai/LightX2V-related post used across this repository. The attached screenshot alone does not prove that it is the same post.

## User-provided screenshot

The experiment was prompted by a screenshot supplied by the user. The visible claims were: ref2va model, LightX2V turbo LoRA, LoRA weight `0.8`, `er_sde` sampler, and a comparison of `6` steps with the usual `20` steps. The screenshot does not expose the original post URL, GPU, seed, prompt, scheduler, VAE, EasyCache, or complete workflow.

Therefore, the experiment fixes the visible values and explicitly defines the hidden values in the README and JSON. It must not be described as a complete reproduction of the screenshot's original environment.

## Model verification

- ref2va: `20,970,379,616 bytes`
- ref2va SHA-256: `9255F52B6677845AD238F20DFAAFA94727053694127AB7F255C048F0F9365779`
- Kijai LoRA: `1,956,171,984 bytes`
- Kijai LoRA SHA-256: `FC9B6500F0331FE925B004738BAAA31BD34104741C8BF9334816F9AC3005C8C1`

The ref2va file stalled at 0 bytes with the standard `hf download` path, so it was retrieved with a Python HTTPS downloader inside the same Docker image, reconstructed from HTTP ranges, and atomically installed after size and SHA-256 verification. The 4090 Compose service was restarted afterward; ComfyUI model discovery, `model_type FLOW` in the execution log, and four successful history entries were checked.
