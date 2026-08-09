# MiniMax-H3 Japanese Cat-Cafe Vlog — 5-Segment Motion Context Experiment

日本語の詳細記録: [README.md](./README.md) · Machine-readable record: [experiment.json](./experiment.json)

Date: 2026-08-09 JST
Experiment ID: h3-japanese-catcafe-vlog-5segment
Status: verified

Frame tile: [contact sheet](./previews/contact-sheet.jpg) · [manifest](./previews/contact-sheet.json)

![Japanese cat-cafe Vlog frame tile](./previews/contact-sheet.jpg)

> The tracked frame tile lets reviewers inspect the approximately 30-second Vlog's segment transitions. The video files themselves are local-only.

## X video and reference URLs

- **Completed-video post:** [X post](https://x.com/hAru_mAki_ch/status/2086296391702438041) — status is uncertain. A publication record exists, but the identity between the public X attachment and this local completed video, including attachment mapping, has not been confirmed.
- **References:** [Motion Context implementation](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context) · [source three-segment post](https://x.com/photogenicweeke/status/2085848283138891926?s=46)

The publication record labels the URL as posted, while its payload says simulationOnly=true. Verify the original X attachment before treating it as canonical evidence.

### Workflow, run, and X mapping

| Workflow | Segment | Prompt ID | Measured run | Local output | X video |
|---|---:|---|---|---|---|
| [segment_01_api.json](./segment_01_api.json) | 1 | 40bc8f28-fcf9-41ec-9f5c-a98f71ad7b3d | success; 158 frames; 6.583008 s; 464.903 s wall time | runtime/4090/output/video/h3_cat_cafe_vlog/segment_01_00001_.mp4 | [completed-video post](https://x.com/hAru_mAki_ch/status/2086296391702438041) (attachment mapping unconfirmed) |
| [segment_02_api.json](./segment_02_api.json) | 2 | 9ea36b47-769b-45d1-a38b-8d412509e69b | success; 136 frames; 5.666667 s; 556.262 s wall time | runtime/4090/output/video/h3_cat_cafe_vlog/segment_02_00001_.mp4 | [completed-video post](https://x.com/hAru_mAki_ch/status/2086296391702438041) (attachment mapping unconfirmed) |
| [segment_03_api.json](./segment_03_api.json) | 3 | 6095947a-5701-443c-9ceb-184e38a992fb | success; 136 frames; 5.666667 s; 555.960 s wall time | runtime/4090/output/video/h3_cat_cafe_vlog/segment_03_00001_.mp4 | [completed-video post](https://x.com/hAru_mAki_ch/status/2086296391702438041) (attachment mapping unconfirmed) |
| [segment_04_api.json](./segment_04_api.json) | 4 | 28ac5017-3a0e-468f-a6b1-3b5d07d1d8b2 | success; 136 frames; 5.666667 s; 556.361 s wall time | runtime/4090/output/video/h3_cat_cafe_vlog/segment_04_00001_.mp4 | [completed-video post](https://x.com/hAru_mAki_ch/status/2086296391702438041) (attachment mapping unconfirmed) |
| [segment_05_api.json](./segment_05_api.json) | 5 | 32ecf88e-b487-45bc-a762-aac7486ded7f | success; 136 frames; 5.666667 s; 554.413 s wall time | runtime/4090/output/video/h3_cat_cafe_vlog/segment_05_00001_.mp4 | [completed-video post](https://x.com/hAru_mAki_ch/status/2086296391702438041) (attachment mapping unconfirmed) |

The generated API workflows and run metadata are also in [manifest.json](./manifest.json) and [run-progress.json](./run-progress.json).

## Purpose and result

The test asks whether an approximately 30-second cat-cafe Vlog with Japanese dialogue can be assembled naturally from five short generations. The prompts are written in English, while the requested spoken dialogue is Japanese. The same influencer-style woman, clothing, voice, camera style, cat, cafe, lighting, and background audio were carried through a five-segment MiniMax-H3 T2V chain using video/audio context and saved latents.

Measured result:

- 5/5 ComfyUI history runs finished with success.
- The merged output is 1280×704, 24 fps, 702 frames, and 29.256 s.
- Every segment contains AAC audio at 32 kHz / stereo.
- blackdetect found no black interval.
- This run had no OOM and no CUDA runtime error.
- Total generation wall time was 2687.899 s (44 m 47.899 s).
- The local merged file is outputs/h3_cat_cafe_vlog_5segment_merged.mp4 with SHA-256 73200CA4577C710BCADB41FD23451EBE01BDDE3E30D8E4E3A734F5A9A88E10DC.

The Japanese dialogue was sent as UTF-8 request bytes; no replacement of Japanese characters with question marks was detected. Independent ASR verification of the actual generated speech was not performed. Visual samples unexpectedly contain Japanese caption-like text in some frames even though the prompts requested no subtitles or on-screen text; this is recorded as a model side effect, not an added subtitle edit.

## Segment design

Each segment was generated at 158 frames (158 / 24 = 6.583 seconds). Segments 2–5 received the first 22 frames (22 / 24 = 0.9167 seconds) of the preceding video/audio context and were trimmed after generation:

158 + 4 × (158 - 22) = 702 frames
702 / 24 = 29.25 seconds (measured: 29.256 s)

| Segment | Story beat | Raw frames | Context | Output frames / seconds | Generation time |
|---:|---|---:|---:|---:|---:|
| 1 | Introduction before entering the cafe | 158 | 0 | 158 / 6.583 s | 464.903 s |
| 2 | A cat greets her | 158 | 22 | 136 / 5.667 s | 556.262 s |
| 3 | She pets the cat; purring is requested | 158 | 22 | 136 / 5.667 s | 555.960 s |
| 4 | Treat time | 158 | 22 | 136 / 5.667 s | 556.361 s |
| 5 | Closing before leaving | 158 | 22 | 136 / 5.667 s | 554.413 s |
| **Total** |  |  |  | **702 / 29.256 s** | **2687.899 s** |

## Runtime and GPU

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

Models:

- Diffusion: minimax_h3_fl2va_pruned_int8_convrot.safetensors
- Text encoder: qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
- Video VAE: minimax_h3_video_vae_fp16.safetensors
- Audio VAE: minimax_h3_audio_vae_fp32.safetensors

Implementation revision and related experiments:

- Motion Context revision: 15fc6a7bf7b78efb27f33d7eef3818e7ed0e118a
- Base experiment: [motion-context-3segment README](../../05-temporal-continuity/motion-context-3segment/README.md) · [English counterpart](../../05-temporal-continuity/motion-context-3segment/README.en.md)
- Workflow builder: [scripts/build-h3-catcafe-vlog-workflows.py](../../../scripts/build-h3-catcafe-vlog-workflows.py)
- Runner: [scripts/run-h3-catcafe-vlog.ps1](../../../scripts/run-h3-catcafe-vlog.ps1)
- Merge and validation: [scripts/merge-h3-catcafe-vlog.ps1](../../../scripts/merge-h3-catcafe-vlog.ps1)

## Fixed H3 conditions

| Item | Setting |
|---|---|
| Mode | T2V; no reference image |
| Resolution | 1280×704, approximately 720p |
| FPS | 24 |
| Steps | 20 |
| Sampler / scheduler | res_multistep / simple |
| Denoise | 1.0 |
| Seed | 2026080910, shared by all segments |
| Motion Context | context_length=22 |
| Audio context | audio_context_length=22, audio_mode=timeline |
| Video encode | encode_mode=video |
| Anchor | anchor_mode=head |
| Trim | match_tail=true, fps=24 |
| Attention | sageattn_qk_int8_pv_fp16_cuda, allow_compile=false |
| EasyCache / Sol-Attn / Spectrum | disabled |

The optimization features were disabled to isolate Motion Context continuity. The reference baseline used only the generic FP16 CUDA SageAttention path.

## Prompt and dialogue design

The API files contain the full English prompts. Their requested Japanese dialogue is:

| Segment | Scene intent | Requested Japanese line | English gloss |
|---:|---|---|---|
| 1 | Enter a cozy Tokyo cat cafe in the late afternoon | 「今日は東京の猫カフェに来ました！たっぷり癒やされてきます」 | “I came to a Tokyo cat cafe today! I’m going to get thoroughly relaxed.” |
| 2 | An orange tabby with white paws and a blue collar comes to greet her | 「入ってすぐ、この子が来てくれた！めちゃくちゃ人懐っこい」 | “As soon as I came in, this one came over! So friendly!” |
| 3 | Pet the tabby on a low sofa and capture its purring | 「見て、このゴロゴロ音。かわいすぎて動けない」 | “Listen to this purring. It’s so cute I can’t move.” |
| 4 | Feed a small treat and laugh softly | 「おやつタイムです。食べ方までかわいいんだけど！」 | “It’s treat time. Even the way it eats is adorable!” |
| 5 | Play briefly, return to selfie view, and say goodbye | 「今日は本当に癒やされました。またこの子に会いに来ます！」 | “I’m truly refreshed today. I’ll come back to see this one again!” |

The prompts also requested no subtitles, no on-screen text, and no logos. Frames 14, 21, and 28 of the visual review nevertheless contain generated Japanese caption-like text.

## Reproduction

From the repository root (<repo-root>):

1. Start the ComfyUI service:

~~~powershell
docker compose --profile 4090 up -d --build h3-4090
Invoke-RestMethod http://127.0.0.1:8188/system_stats
~~~

2. Build the API workflows:

~~~powershell
uv run python scripts/build-h3-catcafe-vlog-workflows.py --output-dir experiments/06-production-pipelines/catcafe-vlog-5segment
~~~

This creates segment_01_api.json through segment_05_api.json and manifest.json.

3. Run the five segments in order:

~~~powershell
.\scripts\run-h3-catcafe-vlog.ps1 -Port 8188 -StartSegment 1 -TimeoutSeconds 7200
~~~

The runner submits each segment to ComfyUI /prompt and copies the preceding output into the next segment's runtime/4090/input/h3_cat_cafe_vlog directory. It sends the HTTP body as UTF-8 bytes, so the Japanese dialogue can be reproduced from Windows PowerShell. Resume with StartSegment 2 through StartSegment 5 if needed. Prompt IDs, timing, ffprobe, blackdetect, and SHA-256 values are written to [run-progress.json](./run-progress.json).

4. Merge and validate:

~~~powershell
.\scripts\merge-h3-catcafe-vlog.ps1
~~~

The merged file is outputs/h3_cat_cafe_vlog_5segment_merged.mp4, and the merge report is [merge.json](./merge.json).

## Outputs and validation

### Segment outputs

| Segment | Output | Frames / duration | Bytes | SHA-256 | blackdetect |
|---:|---|---:|---:|---|---:|
| 1 | runtime/4090/output/video/h3_cat_cafe_vlog/segment_01_00001_.mp4 | 158 / 6.583008 s | 1,813,877 | 3111BD6478094C1015C01691D7C485C0A59E42E1B244E838075BA0E9BB74D4F8 | 0 |
| 2 | runtime/4090/output/video/h3_cat_cafe_vlog/segment_02_00001_.mp4 | 136 / 5.666667 s | 1,866,529 | F093788DD228F68802F8AD3F86F5EF0243EC4E91B63C7514CB11F483FBDF5A24 | 0 |
| 3 | runtime/4090/output/video/h3_cat_cafe_vlog/segment_03_00001_.mp4 | 136 / 5.666667 s | 1,413,609 | D013D2D26EBD9AFC585139D0DB918BC42187F2F0296A5EBA391615E6D01BB97C | 0 |
| 4 | runtime/4090/output/video/h3_cat_cafe_vlog/segment_04_00001_.mp4 | 136 / 5.666667 s | 1,282,981 | F741DAA70C7FE69B399026EB353F8115057D30E002284C41AC9DD32AD5918761 | 0 |
| 5 | runtime/4090/output/video/h3_cat_cafe_vlog/segment_05_00001_.mp4 | 136 / 5.666667 s | 1,252,937 | E271965D47915F2868172E69AF326DCE6F497D45BB253B885A8C5983E0C7F4E9 | 0 |

All five segment files are H.264/AAC at 1280×704 / 24 fps with 32 kHz stereo audio.

### Merged output

| Item | Value |
|---|---|
| Path | outputs/h3_cat_cafe_vlog_5segment_merged.mp4 |
| Evidence status | local-only; the public visual check is [the frame tile](./previews/contact-sheet.jpg) |
| Method | ffmpeg concat filter; libx264 CRF 18; AAC 192k; faststart |
| Video | H.264, 1280×704, 702 frames, 24 fps |
| Audio | AAC, 32 kHz stereo |
| Duration | 29.256 s |
| Bytes | 11,404,834 |
| SHA-256 | 73200CA4577C710BCADB41FD23451EBE01BDDE3E30D8E4E3A734F5A9A88E10DC |
| blackdetect | 0 interval |

### Visual review

Review frames are [frame-00.png](./frames/frame-00.png), [frame-07.png](./frames/frame-07.png), [frame-14.png](./frames/frame-14.png), [frame-21.png](./frames/frame-21.png), and [frame-28.png](./frames/frame-28.png). The woman's clothing and hair color, warm cat-cafe atmosphere, and narrative progression from arrival through cat contact, petting, treats, and the closing selfie remain visible across the chain. The unexpected generated caption-like text is present in frames 14, 21, and 28 despite the no-subtitles instruction.

## Limitations

- Independent ASR verification of whether the generated Japanese speech matches the requested dialogue and pronunciation was not run.
- The spelling and contextual accuracy of generated Japanese text was not evaluated as subtitle quality.
- Frame count, audio streams, and black frames were checked, but no quantitative person-identity or audio-continuity score was collected.
- This run used an RTX 4090; it was not the same five-segment, 720p-equivalent experiment on an RTX 3060.
- EasyCache, Sol-Attn, and Spectrum comparisons were intentionally separated; the recorded generation time is a Motion Context plus generic SageAttention baseline.

## Records

- Japanese/mixed detailed record: [README.md](./README.md)
- English counterpart: [README.en.md](./README.en.md)
- Machine-readable record: [experiment.json](./experiment.json)
- Public visual evidence: [previews/contact-sheet.jpg](./previews/contact-sheet.jpg) and [previews/contact-sheet.json](./previews/contact-sheet.json)
