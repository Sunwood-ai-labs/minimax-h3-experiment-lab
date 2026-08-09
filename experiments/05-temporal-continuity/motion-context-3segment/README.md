# MiniMax-H3 Motion Context 3-Segment Experiment

日本語の詳細記録: [README.ja.md](./README.ja.md) · Machine-readable record: [experiment.json](./experiment.json)

Date: 2026-08-09 JST
Experiment ID: niko-h3-motion-context-3segment
Status: verified

Frame tile: [contact sheet](./previews/contact-sheet.jpg) · [manifest](./previews/contact-sheet.json)

![Motion Context frame tile](./previews/contact-sheet.jpg)

> The tracked frame tile and manifest are the public visual evidence for this experiment. The generated MP4 files remain local-only.

## X video and reference URLs

- **Generated-video post:** [X post](https://x.com/hAru_mAki_ch/status/2086223412129902756) — status is uncertain. The URL is present in a publication simulation, but simulation-only media provenance does not prove the exact attachment mapping for the three segments.
- **References:** [ComfyUI-H3-Motion-Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context) · [Photogenic Weekend source post](https://x.com/photogenicweeke/status/2085848283138891926?s=46)

The Photogenic Weekend post was checked from a user-provided screenshot. Its stated 1920×1088 conditions and exact workflow were not independently reproduced here.

### Workflow, run, and X mapping

| Workflow | Segment | Prompt ID | Measured run | Local output | X video |
|---|---:|---|---|---|---|
| [segment_01](./workflows/segment_01_api.json) | 1 | 366eb6a1-61b4-4790-ada2-e47c027fa843 | success; 124 frames; 5.167 s; 555.138 s wall time | runtime/4090/output/video/h3_motion_context/segment_01_00001_.mp4 | [X post](https://x.com/hAru_mAki_ch/status/2086223412129902756) (attachment mapping unconfirmed) |
| [segment_02](./workflows/segment_02_api.json) | 2 | c0ec519b-466d-43d8-a429-68206823879b | success; 102 trimmed frames; 4.250 s; 438.387 s wall time | runtime/4090/output/video/h3_motion_context/segment_02_00001_.mp4 | [X post](https://x.com/hAru_mAki_ch/status/2086223412129902756) (attachment mapping unconfirmed) |
| [segment_03](./workflows/segment_03_api.json) | 3 | 58dfc329-ae61-420c-8beb-e414a1732ccb | success; 119 trimmed frames; 4.959 s; 493.080 s wall time | runtime/4090/output/video/h3_motion_context/segment_03_00001_.mp4 | [X post](https://x.com/hAru_mAki_ch/status/2086223412129902756) (attachment mapping unconfirmed) |

The complete workflow set is also described by [workflows/manifest.json](./workflows/manifest.json).

## Purpose and result

This experiment integrated ComfyUI-H3-Motion-Context into a reusable Docker Compose environment and tested a three-segment text-to-video (T2V) chain. Segments 2 and 3 received the preceding video context, audio context, and saved video/audio latents.

Under the tested 1280×704 conditions, all three ComfyUI histories finished with success; there was no OOM, CUDA runtime error, node error, or black interval. All outputs were H.264/AAC with audio. The Motion Context logs reported 0.00 ms audio drift for segment 2 and 0.01 ms for segment 3. The trimmed chain was concatenated to 345 frames / 14.416667 s.

This verifies a reusable RTX 4090 / 1280×704 three-segment Motion Context chain. It does not verify the source post's 1920×1088 setup, its exact seed/prompt/workflow, or its reported speed and quality claims.

## Implementation

- Motion Context custom-node revision: 15fc6a7bf7b78efb27f33d7eef3818e7ed0e118a
- Docker build arg: H3_MOTION_CONTEXT_REF=15fc6a7bf7b78efb27f33d7eef3818e7ed0e118a
- Container path: /opt/ComfyUI/custom_nodes/ComfyUI-H3-Motion-Context
- Workflow generator: [scripts/build-h3-motion-context-workflows.py](../../../scripts/build-h3-motion-context-workflows.py)
- The container self-check logged:

  ~~~text
  h3_motion_context: interior keyframe anchors enabled
  h3_motion_context: keyframe/ref coexistence enabled
  ~~~

- Source node checks passed:

  ~~~text
  uv run --with numpy python tests/_mock_harness.py       # all checks passed
  uv run --with numpy python tests/_node_smoke_test.py    # smoke test passed
  ~~~

## Reproduction environment

### Host

| Item | Value |
|---|---|
| Host platform | Windows host + WSL2 Ubuntu |
| WSL kernel | 6.6.114.1-microsoft-standard-WSL2 |
| Docker Engine | 29.4.3 |
| Docker Compose | v5.1.3 |
| GPU | NVIDIA GeForce RTX 4090 |
| GPU UUID | GPU-f877fbc1-9f24-bd97-3359-dd358eaa2caa |
| NVIDIA driver | 591.86 |
| VRAM | 24564 MiB |

### Docker / ComfyUI

| Item | Value |
|---|---|
| Compose service | h3-4090 |
| Endpoint | http://127.0.0.1:8188 |
| Image | local/minimax-h3-comfyui:v0.30.0 |
| Image digest | sha256:8611a4bdaf00f565811cde2fd9d9e04fa0ad7648ce819111ae1d1573f55bff60 |
| ComfyUI | 0.30.0 |
| Python | 3.12.3 |
| PyTorch | 2.11.0+cu130 |
| Startup arguments | --disable-pinned-memory --disable-async-offload --fp16-intermediates --preview-method none |
| Input mount | ./runtime/4090/input:/opt/ComfyUI/input |
| Output mount | ./runtime/4090/output:/opt/ComfyUI/output |

Models loaded from the repository's models/ tree:

- Diffusion: minimax_h3_fl2va_pruned_int8_convrot.safetensors
- Text encoder: qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
- Video VAE: minimax_h3_video_vae_fp16.safetensors
- Audio VAE: minimax_h3_audio_vae_fp32.safetensors

## Fixed conditions

| Item | Setting |
|---|---|
| Mode | T2V; no reference image |
| Resolution | 1280×704 |
| FPS | 24 |
| Steps | 20 |
| Sampler / scheduler | res_multistep / simple |
| Denoise | 1.0 |
| Seed | 2026080909, shared by all three segments |
| Motion Context | context_length=22 |
| Video encode | encode_mode=video |
| Anchor | anchor_mode=head |
| Audio | audio_mode=timeline, audio_context_length=22 |
| Trim | match_tail=true, fps=24 |
| Attention | sageattn_qk_int8_pv_fp16_cuda, allow_compile=false |
| EasyCache / Sol-Attn / Spectrum | disabled |

EasyCache, Sol-Attn, and Spectrum were disabled to isolate Motion Context continuity rather than measure step-skipping or pinned-row optimization effects.

### Segment design

The design used 22 overlapping frames (22 / 24 = 0.9167 s) for segments 2 and 3, then trimmed that overlap:

| Segment | Prompt intent | Raw frames / seconds | Context | Trimmed output | Wall time |
|---:|---|---:|---:|---:|---:|
| 1 | A woman in a floral dress walks through a warm Japanese cafe at night while the camera tracks backward. | 124 / 5.1667 s | 0 | 124 frames / 5.167 s | 555.138 s |
| 2 | Continue with the same woman, cafe, lighting, camera direction, and soundtrack; pass a waiter and turn toward the counter. | 124 / 5.1667 s | 22 frames | 102 frames / 4.250 s | 438.387 s |
| 3 | Continue without a reset; reach the counter, slow down, and look toward the warm window while the camera stops. | 141 / 5.8750 s | 22 frames | 119 frames / 4.959 s | 493.080 s |

The generation total was 1486.605 s (24 m 46.605 s), excluding queue-wait time. The three trimmed outputs were concatenated with an ffmpeg concat filter.

## Outputs and measured validation

### Segment outputs

| Segment | Video/audio | Bytes | SHA-256 |
|---:|---|---:|---|
| 1 | runtime/4090/output/video/h3_motion_context/segment_01_00001_.mp4; H.264/AAC, 1280×704, 124 frames | 1,362,144 | 23C3D5A200CE954080E9CB04E409FA43B30300DB84B37A2EAA44149FDEDEC7AE |
| 2 | runtime/4090/output/video/h3_motion_context/segment_02_00001_.mp4; H.264/AAC, 1280×704, 102 frames | 1,239,950 | 31FEEBD5B08F1ADBA59DF41F3FDD49B0A86E237819FDE34174C6D9594528B64D |
| 3 | runtime/4090/output/video/h3_motion_context/segment_03_00001_.mp4; H.264/AAC, 1280×704, 119 frames | 1,148,458 | 870788B9C68B4D80D314AB374E6348B34C63A408CEBFA7C936CFB9310E5CC93F |

Each segment used AAC 32 kHz / stereo. Saved latents:

~~~text
runtime/4090/output/h3_context/clip_00001.safetensors  12,556,248 bytes
runtime/4090/output/h3_context/clip_00002.safetensors  12,556,248 bytes
runtime/4090/output/h3_context/clip_00003.safetensors  14,253,016 bytes
~~~

### Merged local output

| Item | Value |
|---|---|
| Path | outputs/h3_motion_context_3segment_merged.mp4 |
| Evidence status | local-only; the public visual check is [the frame tile](./previews/contact-sheet.jpg) |
| Method | ffmpeg concat filter; libx264 -crf 18; AAC 192k; +faststart |
| Output | 1280×704 / 24 fps / 345 frames / 14.416667 s |
| Bytes | 5,349,778 |
| SHA-256 | 24EAAF2B1F5F9965BD4FD887FBA1BF8CA4675A0E0EE53F6543E28996760D8598 |

### Checks

- ComfyUI history: 3/3 success
- Node errors, OOM, and CUDA runtime errors: none
- blackdetect=d=0.25:pic_th=0.98: no black interval in any segment
- All three outputs: H.264/AAC with audio
- Motion Context audio drift: segment 2 0.00 ms; segment 3 0.01 ms
- Segment 2 tail trim: 267 samples / 8.34 ms, with 102 video frames and audio aligned
- Visual review: the woman, floral dress, warm cafe lighting, and forward camera direction remained coherent; segment 3 reached the counter

The source seam_probe.py expects the next segment's pre-Trim audio to be saved separately. This workflow saved only final output audio, so the exact A-tail/B-pre-Trim cross-correlation probe was not run.

## Reproduction

From the repository root (<repo-root>):

~~~powershell
docker compose --profile 4090 build h3-4090
docker compose --profile 4090 up -d h3-4090
python scripts/build-h3-motion-context-workflows.py --output-dir experiments/05-temporal-continuity/motion-context-3segment/workflows
~~~

Submit each API workflow to ComfyUI /prompt with a top-level prompt object. For example:

~~~powershell
$workflow = Get-Content -Raw experiments/05-temporal-continuity/motion-context-3segment/workflows/segment_01_api.json | ConvertFrom-Json
$body = @{ prompt = $workflow } | ConvertTo-Json -Depth 100 -Compress
Invoke-RestMethod -Uri http://127.0.0.1:8188/prompt -Method Post -ContentType application/json -Body $body
~~~

Copy segment 1 to runtime/4090/input/h3_motion_context/segment_01.mp4 before submitting segment 2, and copy segment 2 to runtime/4090/input/h3_motion_context/segment_02.mp4 before submitting segment 3. LoadVideo resolves these paths relative to the container's /opt/ComfyUI/input. The saved h3_context/clip_00001.safetensors and clip_00002.safetensors must remain under the same container's /opt/ComfyUI/output.

Reproduction records and source links: [experiment.json](./experiment.json), [workflows/manifest.json](./workflows/manifest.json), [segment_01_api.json](./workflows/segment_01_api.json), and [build-h3-motion-context-workflows.py](../../../scripts/build-h3-motion-context-workflows.py).

## Limitations and next checks

- The source post's exact prompt, seed, workflow, and model revision were not reproduced.
- Generation at 1920×1088 was not tested.
- The source post's reported speedup and quality difference from single-shot generation were not tested.
- seam_probe.py cross-correlation using pre-Trim audio was not run.
- No quantitative person-identity or audio-continuity score was collected.
- The same three-segment condition was not run on an RTX 3060.

The supported conclusion is limited to: “Motion Context three-segment chaining is reproducible on an RTX 4090 at 1280×704 under the recorded conditions.”
