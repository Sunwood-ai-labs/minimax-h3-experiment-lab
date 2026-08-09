# MiniMax-H3 Kijai LightX2V 4-step LoRA

Language navigation: [Japanese record](./README.ja.md)

- ID: `2026-08-08-low-step-lightx2v-4step`
- Status: `verified`
- Purpose: Verify Kijai's ComfyUI-oriented LightX2V LoRA in the existing MiniMax-H3 Docker Compose environment

Frame tile: [contact sheet](./previews/contact-sheet.jpg) / [manifest](./previews/contact-sheet.json)

Record: [experiment.json](./experiment.json) · [Japanese README](./README.ja.md) · [source ledger](./sources.md)

![Low-step generation frame tile](./previews/contact-sheet.jpg)

> The tracked frame tile and manifest are the public visual evidence for this record. Source MP4s under `runtime/*/output` remain local-only.

## Purpose and status

The hypothesis was that Kijai's LightX2V 4-step LoRA could be connected to the official MiniMax-H3 VAE and pruned int8 base in the existing Compose environment and generate both T2V and I2V video in four steps.

The experiment is `verified`. Its X publication status is `uncertain`: the record contains one X URL used in a posting simulation, but the attachment metadata has not been re-confirmed, so the URL does not establish which, if any, of the four generated MP4s was attached.

## Public evidence boundary

The contact sheet and manifest are the public visual evidence tracked by this experiment. The four generated source MP4s remain local-only. The X URL below is retained as an uncertain publication reference and must not be described as a confirmed per-run video mapping.

## X video URL and every reference URL

### X video URL

- Overview post: [X post](https://x.com/hAru_mAki_ch/status/2085926432086307010) — `uncertain`. It was used for posting simulation; the attachment relationship to the four runs has not been confirmed.

### Reference URLs

- Source condition post: [SD_Tutorial post](https://x.com/sd_tutorial/status/2085760369612783646)
- Kijai's ComfyUI repository: [Kijai/MiniMax-H3_comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy)
- Upstream LightX2V distribution: [lightx2v/Minimax-h3-Turbo](https://huggingface.co/lightx2v/Minimax-h3-Turbo/tree/main)
- Upstream reproduction repository: [ModelTC/Minimax-H3-Turbo](https://github.com/ModelTC/Minimax-H3-Turbo)

The Kijai Hugging Face revision checked was `37ae5cbe1d6f2243484812fc511f9fa427b12a30` on 2026-08-08. The upstream LightX2V revision checked was `b65e359c0d128b3c5e08e0f5bf2791b794378588` on 2026-08-08.

## Workflow/run and video mapping

The four workflow files and run IDs are mapped below. Every X cell points to the same uncertain overview-post URL; it is not evidence that that specific MP4 was attached.

| Workflow | Run ID | Mode / sampler | X video |
|---|---|---|---|
| [`minimax_h3_kijai_lightx2v_4step_1344x768_er_sde_api.json`](../../../workflows/minimax_h3_kijai_lightx2v_4step_1344x768_er_sde_api.json) | `t2v-er_sde` / prompt `b87755af-c053-42c3-8c49-6c628013b124` | T2V / `er_sde` | [X post](https://x.com/hAru_mAki_ch/status/2085926432086307010) (`uncertain`) |
| [`minimax_h3_kijai_lightx2v_4step_1344x768_sa_solver_api.json`](../../../workflows/minimax_h3_kijai_lightx2v_4step_1344x768_sa_solver_api.json) | `t2v-sa_solver` / prompt `405a78d2-9999-42b7-ab3b-759771760416` | T2V / `sa_solver` | [X post](https://x.com/hAru_mAki_ch/status/2085926432086307010) (`uncertain`) |
| [`minimax_h3_kijai_lightx2v_4step_1344x768_i2v_er_sde_api.json`](../../../workflows/minimax_h3_kijai_lightx2v_4step_1344x768_i2v_er_sde_api.json) | `i2v-er_sde` / prompt `0734b9d9-105b-47b3-a562-ba4bb8e2f3b5` | I2V / `er_sde` | [X post](https://x.com/hAru_mAki_ch/status/2085926432086307010) (`uncertain`) |
| [`minimax_h3_kijai_lightx2v_4step_1344x768_i2v_sa_solver_api.json`](../../../workflows/minimax_h3_kijai_lightx2v_4step_1344x768_i2v_sa_solver_api.json) | `i2v-sa_solver` / prompt `c56359c6-d7ca-4a64-bc30-b8add8ce5c7d` | I2V / `sa_solver` | [X post](https://x.com/hAru_mAki_ch/status/2085926432086307010) (`uncertain`) |

## What the primary sources establish

Kijai's Hugging Face repository distributes the MiniMax-H3 LightX2V LoRA rather than the MiniMax-H3 base model. Its README states `4 steps`, `0.75` LoRA strength, and examples using `er_sde` and `sa_solver`. The intended LoRA alpha is not confirmed there; the README notes that a lower strength may help if outputs are noisy.

The [SD_Tutorial X post](https://x.com/sd_tutorial/status/2085760369612783646) describes Kijai's repacked LightX2V H3 Turbo LoRA for Comfy support and links to the Kijai repository and the upstream LightX2V repository. Its public media metadata reports 1344×768 and 6.583 seconds. The public MP4 delivery variant inspected with `ffprobe` was 630×360, 158 video frames, 24 fps, and 6.656 seconds. The post does not state the GPU, seed, prompt, sampler, or scheduler.

## Verification approach

1. Use an RTX 4090 while retaining the existing official FP16 video VAE, FP32 audio VAE, pruned int8 base, and NVFP4 text encoder.
2. Connect Kijai's full Comfy LoRA through a model-only LoRA loader and run T2V at strength `0.75` and four steps.
3. Target the 1344×768-class, 24 fps, 158-frame shape observed in the public X media. This is a measured public-media target, not a claim that the original workflow is fully known.
4. Record `res_multistep`/`simple` separately from the `er_sde` and `sa_solver` examples. The source post does not expose the sampler, so the runs are not described as an exact reproduction of the post.
5. After T2V succeeds, run I2V with the same LoRA conditions.

## Runtime and fixed conditions

- GPU: RTX 4090
- Compose service: `h3-4090`
- Base: `minimax_h3_fl2va_pruned_int8_convrot.safetensors`
- Text encoder: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- Video VAE: `minimax_h3_video_vae_fp16.safetensors`
- Audio VAE: `minimax_h3_audio_vae_fp32.safetensors`
- LoRA: `models/loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`
- LoRA strength: `0.75`
- Steps: `4`
- Resolution: `1344×768` target, aligned to 32
- Frames: `158` for the first run, matching the public MP4 measurement and fitting the H3 node's 17k+5 grid
- FPS: `24`
- T2V seed: `2026080801`
- I2V seed: `2026080802`
- T2V prompt: `A calm cinematic sunrise over a quiet Japanese mountain lake, gentle mist drifting across the water, slow camera movement, natural ambient birds and soft wind, no text, five seconds.`
- I2V prompt: `Animate the supplied sunrise lake start frame into a calm cinematic shot. Preserve the mountain silhouette and composition, add gentle camera movement, natural mist drifting over the water, subtle ripples and ambient birds and soft wind, no text.`
- Samplers: `er_sde` and `sa_solver`
- Scheduler: `simple`
- EasyCache: reuse threshold `0.3`, start percent `0.2`, end percent `0.9`, verbose `false`
- Low VRAM mode: `false`

## Measured results

All four runs succeeded on `h3-4090` with four steps, LoRA strength `0.75`, 1344×768, 158 frames, 24 fps, `simple` scheduler, and the official FP16 video VAE / FP32 audio VAE. Only sampler and T2V/I2V mode varied.

| Mode | Sampler | Prompt ID | Inference | Runner wall | Output / inspection | SHA-256 |
|---|---|---|---:|---:|---|---|
| T2V | `er_sde` | `b87755af-c053-42c3-8c49-6c628013b124` | 362.48 sec | 365.71 sec | local-only MP4; `blackdetect` 0 | `B0540FE30DC549ABA6E14B3A36270BFE7068CC76F81B2763C0949CEDD92E233E` |
| T2V | `sa_solver` | `405a78d2-9999-42b7-ab3b-759771760416` | 196.25 sec | 200.39 sec | local-only MP4; `blackdetect` 0 | `DFB59D2BF85A1AFDAEB4C8B3EFABDD2909E91EBD46991F2DB7933F8B96C2C682` |
| I2V | `er_sde` | `0734b9d9-105b-47b3-a562-ba4bb8e2f3b5` | 210.05 sec | 210.457 sec | local-only MP4; `blackdetect` 0 | `CB7A683AF4A9864CA6A1EDAB1C3F350019FF88E9329E12823601772E03791787` |
| I2V | `sa_solver` | `c56359c6-d7ca-4a64-bc30-b8add8ce5c7d` | 193.72 sec | 195.417 sec | local-only MP4; `blackdetect` 0 | `EB6487E54E1C8412A8BAAD2628CB25D24238E901B8939C8BF502B95C4E5F17B6` |

`ffprobe` confirmed `1344×768 / 24 fps / 158 frames / 6.583333 sec / H.264 / AAC stereo` for every output. First and middle frames were inspected: T2V produced a lake, mountains, mist, sunrise, and foliage shot; I2V produced a lake, mountains, mist, and reflection derived from the start frame. No OOM occurred.

Under the same T2V conditions, `sa_solver` took approximately 45.8% less inference time than `er_sde` in this environment. This is a sampler-only speed comparison; visual quality was not quantitatively evaluated.

## Reproduction links and artifacts

### Workflows and reports

- T2V `er_sde`: [workflow](../../../workflows/minimax_h3_kijai_lightx2v_4step_1344x768_er_sde_api.json), SHA-256 `C7680D1756F710D114219E819303295055EEC10ABF39AD52D1920CC3617C4B42`, [report](../../../runtime/4090/benchmark/h3-b87755af-c053-42c3-8c49-6c628013b124.md), [report JSON](../../../runtime/4090/benchmark/h3-b87755af-c053-42c3-8c49-6c628013b124.json)
- T2V `sa_solver`: [workflow](../../../workflows/minimax_h3_kijai_lightx2v_4step_1344x768_sa_solver_api.json), SHA-256 `5AE470B6EB816C4FFC71C74FD435549B3C4F8B74C8BA868CCC0E87463D63FC7C`, [report](../../../runtime/4090/benchmark/h3-405a78d2-9999-42b7-ab3b-759771760416.md), [report JSON](../../../runtime/4090/benchmark/h3-405a78d2-9999-42b7-ab3b-759771760416.json)
- I2V `er_sde`: [workflow](../../../workflows/minimax_h3_kijai_lightx2v_4step_1344x768_i2v_er_sde_api.json), SHA-256 `6BD295F8EFE7D643D8D4794284955A164C73D98E3996675509102830CE59C397`, [report](../../../runtime/4090/benchmark/h3-0734b9d9-105b-47b3-a562-ba4bb8e2f3b5.md), [report JSON](../../../runtime/4090/benchmark/h3-0734b9d9-105b-47b3-a562-ba4bb8e2f3b5.json)
- I2V `sa_solver`: [workflow](../../../workflows/minimax_h3_kijai_lightx2v_4step_1344x768_i2v_sa_solver_api.json), SHA-256 `2B8AF00CB840E6E777D4B79D3B2501C81DF340BDAD672CD5AF976A959D56AA09`, [report](../../../runtime/4090/benchmark/h3-c56359c6-d7ca-4a64-bc30-b8add8ce5c7d.md), [report JSON](../../../runtime/4090/benchmark/h3-c56359c6-d7ca-4a64-bc30-b8add8ce5c7d.json)

### Input and model artifacts

- I2V start image: [1344×768 input](../../../runtime/4090/input/MiniMax_H3_I2V_1344x768_start.png), SHA-256 `9E5893D7C5A9919726E7E60FF2BF4F19E77F746342D38E5FE3217FD2288A3D0F`
- Source image before conversion: [1280×704 input](../../../runtime/4090/input/MiniMax_H3_I2V_1280x704_start.png), SHA-256 `BE63F90186D46A2860A463C70E4E3E76FDF95A19E98F9DB9E696CD7610D96CD8`
- Full Kijai LoRA: `1,956,171,984` bytes, SHA-256 `FC9B6500F0331FE925B004738BAAA31BD34104741C8BF9334816F9AC3005C8C1`
- Primary record: [experiment.json](./experiment.json)
- Public evidence: [contact sheet](./previews/contact-sheet.jpg) and [manifest](./previews/contact-sheet.json)
- Source ledger: [English](./sources.md) / [日本語](./sources.ja.md)

The 1344×768 I2V image is a local derivative of the 1280×704 image, created by increasing scale with the original aspect ratio, center-cropping, and Lanczos-resizing to 1344×768.

## Local overview montage

Four generated MP4s were placed in a 2×2 HyperFrames comparison montage for a planned X parent-post layout. The artifact and render details below document the local composition; they do not establish that the montage or any source MP4 was publicly posted.

- Composition: [`hyperframes-kijai-parent-montage-2026-08-08/index.html`](../../../hyperframes-kijai-parent-montage-2026-08-08/index.html)
- Design: [`DESIGN.md`](../../../DESIGN.md)
- Output: [`MiniMax_H3_Kijai_LightX2V_parent_montage_1920x1080_24fps.mp4`](../../../sunwood-x-simulator-kijai-2026-08-08/assets/MiniMax_H3_Kijai_LightX2V_parent_montage_1920x1080_24fps.mp4)
- Format: `1920×1080 / 24 fps / 158 frames / 6.583333 sec / H.264 + AAC stereo`
- Output size: `14,134,491` bytes
- Output SHA-256: `77DD8806E45F8885F30A8C1528E40AED73DF819316C132D28DEAB60BF27F9F11`
- Source media: only the four experiment-generated videos; no AI replacement footage was used

Run from the composition directory:

```powershell
npx hyperframes lint . --json
npx hyperframes validate .
npx hyperframes inspect . --json --samples 15
npx hyperframes render . --output renders/MiniMax_H3_Kijai_LightX2V_parent_montage_1920x1080_24fps.mp4 --fps 24 --quality standard
```

Recorded validation: lint `ok`, WCAG AA `35 text elements pass`, inspect `0 issues`, and render `158/158 frames`.

## Conclusion and limitations

The local reproduction connected Kijai's MiniMax-H3 LightX2V LoRA to the existing Docker Compose setup and generated both T2V and I2V outputs in four steps at LoRA strength `0.75`, 1344×768, 158 frames, and 24 fps. All four runs succeeded, had no OOM, had zero `blackdetect` intervals, and produced audio-bearing H.264/AAC output.

This is a partial match to the source conditions, not a complete reproduction of the X video. The following limits remain:

- The X post does not report GPU, seed, prompt, sampler, or scheduler.
- The Kijai README does not confirm the intended LoRA alpha.
- The X video's 1344×768 resolution and 6.583-second duration come from public media metadata, not a complete generation workflow.
- The I2V input is a local crop/resize derivative of an existing 1280×704 start frame, not the X post's input image.
- Sampler quality differences were checked visually only; no quantitative video-quality evaluation was performed.
