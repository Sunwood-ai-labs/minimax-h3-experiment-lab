# Sources — Kijai LightX2V scene generalization

## Kijai / MiniMax-H3 Comfy

- URL: https://huggingface.co/Kijai/MiniMax-H3_comfy
- Revision checked: `37ae5cbe1d6f2243484812fc511f9fa427b12a30`
- Used facts: `4 steps`, `0.75 LoRA strength`, and the `er_sde` / `sa_solver` examples.
- LoRA used: `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`

## X reference

- URL: https://x.com/sd_tutorial/status/2085760369612783646
- Used facts from the public post/media metadata: Kijai's repacked LightX2V H3 turbo LoRA for Comfy support; original media target `1344×768`; public media length `6.583 seconds`; inspected delivery variant `158 frames / 24 fps`.
- The post does not expose the GPU, prompt, seed, sampler, scheduler, exact VAE selection, or offload flags. Those values are therefore recorded as local experiment conditions, not as facts about the post.

## Upstream LightX2V

- URL: https://huggingface.co/lightx2v/Minimax-h3-Turbo/tree/main
- Revision checked: `b65e359c0d128b3c5e08e0f5bf2791b794378588`
- Used for lineage/context only; the actual workflow uses Kijai's Comfy-compatible LoRA listed above.

## ImageGen start frames

The four start frames were generated in this Codex session with the built-in `image_gen.imagegen` capability. The exact prompts, copied workspace paths, source output filenames, byte sizes, and SHA-256 values are in [`imagegen-prompts.md`](./imagegen-prompts.md). The generated PNGs are treated as fixed experimental inputs after copying them to `runtime/4090/input/`.

## Interpretation boundary

This is a scene-generalization experiment, not a claim that the X post used these four images or these prompts. The controlled comparison is: same 4090 Docker/ComfyUI/model/LoRA/resolution/length/steps/sampler settings, with only scene content, start image, prompt, and seed changed.
