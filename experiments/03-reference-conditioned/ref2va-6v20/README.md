# MiniMax-H3 ref2va + Kijai LightX2V — 6 vs 20 steps

[Japanese detailed record: README.ja.md](./README.ja.md)

- Experiment ID: `2026-08-08-reference-ref2va-6v20`
- Date: `2026-08-08 JST`
- GPU: `RTX 4090`
- Status: `verified`
- Purpose: verify, in both T2V and I2V, the screenshot-visible conditions of `ref2va`, the Kijai/LightX2V LoRA, LoRA strength `0.8`, `er_sde`, and a comparison of `6 steps` versus `20 steps` in the same Docker Compose environment.

Frame tile: [contact sheet](./previews/contact-sheet.jpg) / [manifest](./previews/contact-sheet.json)

Record: [experiment.json](./experiment.json) · [tracked frame tile](./previews/contact-sheet.jpg)

![ref2va frame tile](./previews/contact-sheet.jpg)

> The tracked tile is the public visual evidence. The source MP4s are local-only artifacts under `runtime/*/output`.

## X video and reference URLs

- **Generated video post**: [X post](https://x.com/hAru_mAki_ch/status/2085955887575990468) — `uncertain`. This is a post-simulation URL; correspondence between individual T2V/I2V and 6/20-step attachments has not been confirmed.
- **Reference sources**: [sd_tutorial post](https://x.com/sd_tutorial/status/2085760369612783646) / [Kijai MiniMax-H3 Comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy) / [official Comfy-Org MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)
- **Workflow-to-video mapping**:

  | Workflow | Run | X video |
  |---|---|---|
  | [`T2V 6-step`](./workflows/minimax_h3_ref2va_lora080_t2v_er_sde_6step_1344x768_api.json) | T2V / 6 steps | [X post](https://x.com/hAru_mAki_ch/status/2085955887575990468) (attachment correspondence unconfirmed) |
  | [`T2V 20-step`](./workflows/minimax_h3_ref2va_lora080_t2v_er_sde_20step_1344x768_api.json) | T2V / 20 steps | [X post](https://x.com/hAru_mAki_ch/status/2085955887575990468) (attachment correspondence unconfirmed) |
  | [`I2V 6-step`](./workflows/minimax_h3_ref2va_lora080_i2v_er_sde_6step_1344x768_api.json) | I2V / 6 steps | [X post](https://x.com/hAru_mAki_ch/status/2085955887575990468) (attachment correspondence unconfirmed) |
  | [`I2V 20-step`](./workflows/minimax_h3_ref2va_lora080_i2v_er_sde_20step_1344x768_api.json) | I2V / 20 steps | [X post](https://x.com/hAru_mAki_ch/status/2085955887575990468) (attachment correspondence unconfirmed) |

## Conclusion and measured results

All four outputs generated successfully. Each is an `1344×768 / 158 frames / 24 fps / 6.583333 sec` H.264/AAC video with `blackdetect=0` and no OOM.

Six steps is clearly faster than 20 steps, but the two settings do not produce identical frames even with the same seed. The pixel comparisons measured T2V SSIM `0.683275` and I2V SSIM `0.684799`. These support a comparison at the level of broad scene formation, but do not quantitatively prove that 6 steps has nearly the same image quality as 20 steps.

| Mode | Steps | ComfyUI measured | Runner wall | Result |
|---|---:|---:|---:|---|
| T2V | 6 | 459.42 sec | 460.953 sec | Success; no black frames; no OOM |
| T2V | 20 | 00:10:59 | 661.217 sec | Success; no black frames; no OOM |
| I2V | 6 | 294.42 sec | 295.606 sec | Success; no black frames; no OOM |
| I2V | 20 | 00:11:31 | 696.292 sec | Success; no black frames; no OOM |

The 20-step ComfyUI times were recorded from Docker log lines `Prompt executed in 00:10:59` and `00:11:31`. Runner wall time runs from API submission through confirmation of ComfyUI history success; it does not include `ffprobe` or SHA-256 post-processing.

## Reproduction target and evidence boundary

The following four conditions were treated as the reproduction target because they were readable in the user-provided screenshots:

- `ref2va` model
- Kijai/LightX2V turbo LoRA
- LoRA weight `0.8`
- `er_sde`, compared at `6 steps` and the ordinary `20 steps`

The screenshots do not show the GPU, prompt, seed, scheduler, EasyCache, VAE, or complete workflow. This is therefore a local verification with the visible conditions fixed, not a claim of full reproduction of the original post. Prompt, seed, resolution, VAE, and other unseen values were explicitly fixed in this repository for reproducibility.

The LoRA filename contains `4step`, but the same LoRA was applied at 6 and 20 steps as requested. This is a comparison experiment; it does not imply that the LoRA distributor officially guarantees 6- or 20-step use.

Source and investigation notes are separated in [`sources.en.md`](./sources.en.md) / [日本語](./sources.md).

## Experiment matrix and workflow/run mapping

All conditions other than mode and steps were held constant.

| Run | Mode | Steps | Seed | Workflow | Prompt ID |
|---|---|---:|---:|---|---|
| 1 | T2V | 6 | `2026080807` | [`t2v…6step`](./workflows/minimax_h3_ref2va_lora080_t2v_er_sde_6step_1344x768_api.json) | `976ed634-fad0-41be-bb2b-865637bb2758` |
| 2 | T2V | 20 | `2026080807` | [`t2v…20step`](./workflows/minimax_h3_ref2va_lora080_t2v_er_sde_20step_1344x768_api.json) | `23229ad1-a1da-4aa3-83e6-1d04eb74b926` |
| 3 | I2V | 6 | `2026080808` | [`i2v…6step`](./workflows/minimax_h3_ref2va_lora080_i2v_er_sde_6step_1344x768_api.json) | `40c56bb7-d5a3-489b-ad4a-08b59db84175` |
| 4 | I2V | 20 | `2026080808` | [`i2v…20step`](./workflows/minimax_h3_ref2va_lora080_i2v_er_sde_20step_1344x768_api.json) | `e6a6708a-0e2e-418d-9f5f-21709cc2e5cf` |

### Fixed prompts

T2V:

```text
A calm cinematic sunrise over a quiet Japanese mountain lake, gentle mist drifting across the water, slow camera movement, natural ambient birds and soft wind, no text, five seconds.
```

I2V:

```text
Animate the supplied sunrise lake start frame into a calm cinematic shot. Preserve the mountain silhouette and composition, add gentle camera movement, natural mist drifting over the water, subtle ripples and ambient birds and soft wind, no text.
```

The I2V start frame was shared by the 6- and 20-step runs: [`MiniMax_H3_I2V_1344x768_start.png`](../../../runtime/4090/input/MiniMax_H3_I2V_1344x768_start.png), `1344×768`, `1,187,835 bytes`, SHA-256 `9E5893D7C5A9919726E7E60FF2BF4F19E77F746342D38E5FE3217FD2288A3D0F`.

## Fixed inference conditions

| Item | Value |
|---|---|
| GPU | NVIDIA GeForce RTX 4090, 24,564 MiB |
| GPU UUID | `GPU-f877fbc1-9f24-bd97-3359-dd358eaa2caa` |
| Driver | `591.86` |
| Compose service | `h3-4090`, host `8188` |
| Base | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` |
| Base size | `20,970,379,616 bytes` |
| Base SHA-256 | `9255F52B6677845AD238F20DFAAFA94727053694127AB7F255C048F0F9365779` |
| Text encoder | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| Video VAE | `minimax_h3_video_vae_fp16.safetensors` |
| Audio VAE | `minimax_h3_audio_vae_fp32.safetensors` |
| LoRA | `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors` |
| LoRA size | `1,956,171,984 bytes` |
| LoRA SHA-256 | `FC9B6500F0331FE925B004738BAAA31BD34104741C8BF9334816F9AC3005C8C1` |
| LoRA loader | `LoraLoaderModelOnly` |
| LoRA strength | `0.8` |
| Sampler | `er_sde` |
| Scheduler | `simple` |
| EasyCache | reuse `0.3` / start `0.2` / end `0.9` |
| Resolution | `1344×768` (multiple of 32; approximately 720p-class to match the earlier public-video condition) |
| Length | `158 frames`, `24 fps` |
| Output | MP4, H.264 video, AAC stereo at `32000 Hz` |
| ComfyUI launch arguments | `--disable-pinned-memory --fp16-intermediates --preview-method none` |
| H3 memory factor | `1.0` |
| Low VRAM | requested/applied: `false` |
| SageAttention | not used |
| CUDA module loading | `LAZY` |

The 20 GB ref2va model was downloaded from the official Comfy-Org files using a chunked HTTPS downloader, then installed atomically after checking the expected size and SHA-256. After installation, `h3-4090` was restarted; the ref2va file appeared as a ComfyUI `UNETLoader` candidate and the execution log reported `model_type FLOW`.

## Host and Docker runtime

| Item | Value |
|---|---|
| Host OS | Windows 11 Pro, build `26200` |
| Host RAM | `137,270,165,504 bytes` |
| PowerShell | `5.1.26100.8875` |
| Locale / timezone | `ja-JP` / `Asia/Tokyo` |
| Docker Engine | `29.4.3` |
| Docker Compose | `5.1.3` |
| Image | `local/minimax-h3-comfyui:v0.30.0` |
| ComfyUI | `0.30.0` |
| Container Python | `3.12.3` |
| PyTorch / CUDA | `2.11.0+cu130` / `13.0` |
| CUDA base | cuDNN 9 |
| Volume | `./models:/opt/ComfyUI/models:ro`, `./runtime/4090/{input,output,user}` |

## Run results

| Mode | Steps | Prompt ID | ComfyUI | Runner wall | Output | Bytes | SHA-256 |
|---|---:|---|---:|---:|---|---:|---|
| T2V | 6 | `976ed634-fad0-41be-bb2b-865637bb2758` | 459.42 sec | 460.953 sec | local-only MP4 | 1,574,128 | `3A8B7EDA3B2F01EB3DC8635A1D7CFFBC7A7F8C9B3DE2D240BBC1145984075551` |
| T2V | 20 | `23229ad1-a1da-4aa3-83e6-1d04eb74b926` | 659 sec | 661.217 sec | local-only MP4 | 1,700,321 | `A9B8DA655BE3EB76660C034EBA04AA6A499845EABC1B877743404AF23975F39E` |
| I2V | 6 | `40c56bb7-d5a3-489b-ad4a-08b59db84175` | 294.42 sec | 295.606 sec | local-only MP4 | 2,467,722 | `228B82712E1849EA8E06CD90753F7E378515166EBF24A1711BB34C7A4C29BDEA` |
| I2V | 20 | `e6a6708a-0e2e-418d-9f5f-21709cc2e5cf` | 691 sec | 696.292 sec | local-only MP4 | 1,950,512 | `8952D5E1D639C58A9FE35F52BA94AB10E341F43EE2F4E0EE40104DE2432666E6` |

All four runs had the following `ffprobe` properties:

- Video: `1344×768`, H.264, `24/1 fps`, `158 frames`, `6.583333 sec`
- Audio: AAC-LC, stereo, `32000 Hz`, `6.575000 sec`
- `blackdetect.interval_count=0`
- ComfyUI history: `success`, `completed=true`
- Docker log search: no OOM, CUDA out-of-memory, Traceback, or Error

The startup log contains a Torch import-order warning, but it is unrelated to the four successful prompt executions. During generation, 4090 GPU utilization was observed at 100%, and `model_type FLOW` was confirmed.

## 6-step versus 20-step comparison

The 6- and 20-step videos were compared within each mode using FFmpeg SSIM/PSNR. The seeds were the same, but different step counts mean that the outputs are not identical frames.

| Comparison | SSIM | PSNR average | Interpretation |
|---|---:|---:|---|
| T2V 6 vs 20 | `0.683275` | `14.406153 dB` | Moderate pixel similarity; not an image-quality score |
| I2V 6 vs 20 | `0.684799` | `14.455215 dB` | Moderate pixel similarity; not an image-quality score |

The visual poster is [`posters/ref2va-6v20-contact.jpg`](./posters/ref2va-6v20-contact.jpg). Its layout is top-left T2V 6, top-right T2V 20, bottom-left I2V 6, bottom-right I2V 20. All four videos work as sunrise-lake, mountain, and mist scenes.

Comparison logs:

- [`t2v-6-vs-20.ssim-ffmpeg.log`](./quality/t2v-6-vs-20.ssim-ffmpeg.log)
- [`t2v-6-vs-20.psnr-ffmpeg.log`](./quality/t2v-6-vs-20.psnr-ffmpeg.log)
- [`i2v-6-vs-20.ssim-ffmpeg.log`](./quality/i2v-6-vs-20.ssim-ffmpeg.log)
- [`i2v-6-vs-20.psnr-ffmpeg.log`](./quality/i2v-6-vs-20.psnr-ffmpeg.log)

## Limitations

- This is a local verification of the screenshot-visible conditions, not a full reproduction of the original post; unseen prompt, seed, scheduler, VAE, and workflow choices were fixed locally.
- The 6-step and 20-step outputs are not identical frames, and the SSIM/PSNR values are similarity measurements, not image-quality scores.
- The `4step` LoRA was reused at 6 and 20 steps for this comparison; official support for those step counts is not claimed.
- No blind human preference test, identity score, or separate audio-quality evaluation was run.

## Reproduction procedure

Run from the repository root. Start `h3-4090` and wait for its healthcheck to pass:

```powershell
cd <repo-root>
docker compose --profile 4090 up -d h3-4090
docker compose ps

.\scripts\run-h3-post-condition.ps1 -Gpu 4090 -Port 8188 -Workflow .\experiments\03-reference-conditioned\ref2va-6v20\workflows\minimax_h3_ref2va_lora080_t2v_er_sde_6step_1344x768_api.json -OutputPrefix video/MiniMax_H3_Kijai_LightX2V_Ref2VA_T2V_1344x768_6step_er_sde_lora080 -LowVram $false -Seed 2026080807 -TimeoutSeconds 1800 -SkipModelHashes

.\scripts\run-h3-post-condition.ps1 -Gpu 4090 -Port 8188 -Workflow .\experiments\03-reference-conditioned\ref2va-6v20\workflows\minimax_h3_ref2va_lora080_t2v_er_sde_20step_1344x768_api.json -OutputPrefix video/MiniMax_H3_Kijai_LightX2V_Ref2VA_T2V_1344x768_20step_er_sde_lora080 -LowVram $false -Seed 2026080807 -TimeoutSeconds 1800 -SkipModelHashes

.\scripts\run-h3-post-condition.ps1 -Gpu 4090 -Port 8188 -Workflow .\experiments\03-reference-conditioned\ref2va-6v20\workflows\minimax_h3_ref2va_lora080_i2v_er_sde_6step_1344x768_api.json -OutputPrefix video/MiniMax_H3_Kijai_LightX2V_Ref2VA_I2V_1344x768_6step_er_sde_lora080 -LowVram $false -Seed 2026080808 -TimeoutSeconds 1800 -SkipModelHashes

.\scripts\run-h3-post-condition.ps1 -Gpu 4090 -Port 8188 -Workflow .\experiments\03-reference-conditioned\ref2va-6v20\workflows\minimax_h3_ref2va_lora080_i2v_er_sde_20step_1344x768_api.json -OutputPrefix video/MiniMax_H3_Kijai_LightX2V_Ref2VA_I2V_1344x768_20step_er_sde_lora080 -LowVram $false -Seed 2026080808 -TimeoutSeconds 1800 -SkipModelHashes
```

Place the same I2V image under `runtime/4090/input` with the relative filename `MiniMax_H3_I2V_1344x768_start.png` and confirm the SHA-256 above. The workflows and all run hashes are collected in [`experiment.json`](./experiment.json).

`-SkipModelHashes` avoids rehashing the approximately 20 GB model for every run; the runner report records that the hash was skipped. The ref2va model itself was separately checked against its expected SHA-256 during download. A complete reproduction record must verify the model source, size, and SHA-256.

## Saved artifacts and links

- Four API workflows: [`workflows/`](./workflows/)
- Machine-readable experiment record: [`experiment.json`](./experiment.json)
- Source and screenshot constraints: [`sources.en.md`](./sources.en.md) / [日本語](./sources.md)
- ComfyUI run reports: `runtime/4090/benchmark/h3-<prompt_id>.json` / `.md`
- Visual poster: [`posters/`](./posters/)
- SSIM/PSNR logs: [`quality/`](./quality/)

The full Japanese record is [`README.ja.md`](./README.ja.md).
