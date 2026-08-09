# MiniMax-H3 Japanese Synth-Pop MV — Music-Driven Lyric Motion Experiment

日本語の詳細記録: [README.md](./README.md) · Machine-readable record: [experiment.json](./experiment.json)

Date: 2026-08-09 JST
Experiment ID: h3-mv-jpop-5segment
Status: verified

Frame tile: [contact sheet](./previews/contact-sheet.jpg) · [manifest](./previews/contact-sheet.json)

![Japanese synth-pop MV frame tile](./previews/contact-sheet.jpg)

> The tracked frame tile shows the time progression of the H3-generated footage and lyric motion. The completed video files are local-only.

## X video and reference URLs

- **Completed-video post:** [X post](https://x.com/hAru_mAki_ch/status/2086334052639142176) — status is uncertain. The publication record labels this URL as posted, but the payload is simulation-only and does not contain the URL; verify the original X attachment before treating it as canonical evidence.
- **References:** [Motion Context implementation](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context) · [source three-segment post](https://x.com/photogenicweeke/status/2085848283138891926?s=46) · [HyperFrames registry](https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry) · [HyperFrames guide](https://hyperframes.heygen.com/llms.txt)

### Workflow, run, and X mapping

| Workflow | Segment | Prompt ID | Measured run | Local output | X video |
|---|---:|---|---|---|---|
| [segment_01_api.json](./workflows/segment_01_api.json) | 1 | 3efb7532-36e0-40b4-a2ff-0cb2da0cf610 | success; 158 frames; 6.583008 s; 465.797 s generation | runtime/4090/output/video/h3_mv/segment_01_00001_.mp4 | [completed-video post](https://x.com/hAru_mAki_ch/status/2086334052639142176) (attachment mapping unconfirmed) |
| [segment_02_api.json](./workflows/segment_02_api.json) | 2 | 335aedc6-8b92-4319-b75a-40e6ec0c476f | success; 136 frames; 5.666667 s; 553.979 s generation | runtime/4090/output/video/h3_mv/segment_02_00001_.mp4 | [completed-video post](https://x.com/hAru_mAki_ch/status/2086334052639142176) (attachment mapping unconfirmed) |
| [segment_03_api.json](./workflows/segment_03_api.json) | 3 | 89ebf33d-0f0e-48e3-b3c1-a268d6e5cb47 | success; 136 frames; 5.666667 s; 553.619 s generation | runtime/4090/output/video/h3_mv/segment_03_00001_.mp4 | [completed-video post](https://x.com/hAru_mAki_ch/status/2086334052639142176) (attachment mapping unconfirmed) |
| [segment_04_api.json](./workflows/segment_04_api.json) | 4 | 2562fdd9-8b43-423f-b86a-ac4594281ff0 | success; 136 frames; 5.666667 s; 552.608 s generation | runtime/4090/output/video/h3_mv/segment_04_00001_.mp4 | [completed-video post](https://x.com/hAru_mAki_ch/status/2086334052639142176) (attachment mapping unconfirmed) |
| [segment_05_api.json](./workflows/segment_05_api.json) | 5 | 3dbe432d-cf8f-42fa-8243-212ded5df970 | success; 136 frames; 5.666667 s; 555.882 s generation | runtime/4090/output/video/h3_mv/segment_05_00001_.mp4 | [completed-video post](https://x.com/hAru_mAki_ch/status/2086334052639142176) (attachment mapping unconfirmed) |

The complete H3 graph and conditions are recorded in [workflows/manifest.json](./workflows/manifest.json).

## Purpose and result

This pipeline tested three linked operations:

1. Carry video, audio, and latent context from one MiniMax-H3 Motion Context segment into the next.
2. Use H3's generated audio as the common music timeline.
3. Drive Japanese lyric motion from analyzed audio events rather than treating the lyrics as static subtitles.

The result is a five-segment Japanese synth-pop / alt-pop MV. The H3 footage keeps the same Japanese female singer, black hair, silver hair clip, black satin jacket, deep-red dress, and silver ear cuff while moving from a rain-wet Tokyo rooftop through stairs, an underpass, and a pedestrian bridge before returning to a rooftop at dawn. HyperFrames then adds lyric animation over the H3 video and uses the same generated audio without replacing it with an external BGM track.

Measured result:

- H3: five segments at 1280×704 / 24 fps / 20 steps.
- H3 merged plate: 702 frames, 29.256 s, H.264/AAC, 32 kHz stereo.
- HyperFrames final: 1280×704 / 30 fps / 878 frames / 29.266667 s.
- Audio analysis: 30 fps RMS, 16-band FFT, beat and energy events.
- Lyric motion includes character-by-character reveal, mask/sweep, blur resolve, kinetic letter-in, and beat-responsive subtle pulses.
- The five lyric lines are planned prompt text; ASR verification of the generated singing was not performed.

Local outputs:

- Lyric-motion final: hyperframes-mv-lyrics/renders/h3_jpop_mv_lyric_motion.mp4; SHA-256 097EBE221189EE2726319DDC555E57B813483BCA9FD48640E18E75830B179050.
- H3-only merged plate: outputs/h3_jpop_mv_5segment_merged.mp4; SHA-256 28F1921260CF45A710E7C1BB8D64E72A91889379F049C5BDB91217F2E6EF92E.

Both video files are local-only. The public visual evidence is the tracked [frame tile](./previews/contact-sheet.jpg) and [manifest](./previews/contact-sheet.json).

## H3 segment design

Each workflow generated 158 raw frames. Segments 2–5 received the previous video's first 22 frames as video/audio context and removed the overlap with match_tail=true:

158 + 4 × (158 - 22) = 702 frames
702 / 24 fps = approximately 29.25 seconds

| Segment | Scene | Planned lyric | Raw / context | Output | Generation time |
|---:|---|---|---:|---:|---:|
| 1 | The singer begins on a rain-wet rooftop | 夜を越えて　光を探す (“Cross the night and search for light”) | 158 / 0 | 158 frames / 6.583008 s | 465.797 s |
| 2 | Descend from neon stairs toward an alley | 君となら　まだ飛べる (“With you, I can still fly”) | 158 / 22 | 136 frames / 5.666667 s | 553.979 s |
| 3 | Red and gold light runs through an underpass | 雨の向こう　夢が見える (“Beyond the rain, I can see a dream”) | 158 / 22 | 136 frames / 5.666667 s | 553.619 s |
| 4 | Perform on a pedestrian bridge above the city | この瞬間を　抱きしめて (“Hold this moment close”) | 158 / 22 | 136 frames / 5.666667 s | 552.608 s |
| 5 | Return to the rooftop after the rain, at dawn | 明日へ行こう　また会おう (“Let’s go to tomorrow; see you again”) | 158 / 22 | 136 frames / 5.666667 s | 555.882 s |
| **Total** |  |  |  | **702 / 29.256 s** | **2681.885 s** |

The generation-time total is the sum of the five ComfyUI runs and excludes HyperFrames analysis and rendering time.

## H3 audio analysis and lyric motion

### Audio source

The audio was extracted from the H3 merged plate and used as the HyperFrames input; it was not replaced by an external music track.

| Item | Value |
|---|---|
| Source | H3-generated audio |
| Extracted file | assets/bgm.mp3 |
| Duration | 29.255969 s |
| Sample rate | 32000 Hz / stereo |
| SHA-256 | D2895A21CBBDA95E3D0C8C76A7B4DC302D1EA3B7D4B7AD84D50EE57033094E48 |

[audiomap.json](./audiomap.json) stores tempo, beats, bars, event density, and energy phases. [audio-data.json](./audio-data.json) stores per-frame 30 fps RMS and normalized 16-band FFT values.

Analysis results:

- Estimated tempo: 123 BPM
- Time signature: 4/4
- Beats: 56
- Bars: 14
- Detected events: 146 (kick 38 / snare 60 / hihat 42 / perc 6)
- Rolls: 11
- Energy phases: 8
- FFT: 16 bands at 30 fps across 877 frames

The lyric composition feeds frame-level loudness and band energy into CSS variables to control motion strength. It does not place a generic equalizer on screen:

| Segment | Lyric treatment | Motion intent |
|---:|---|---|
| 1 | typewriter + stagger + neon flicker | Introduce the first lyric one character at a time and connect it to the opening groove |
| 2 | sideways sweep + mask reveal + overlay pop | Move the lyric laterally with the traveling shot |
| 3 | blur resolve + kinetic letter-in + negative-space hold | Hold the lyric centrally while the low-end energy remains |
| 4 | kinetic letter-in + stagger + overlay pop | Make the text more forceful at the performance peak |
| 5 | blur resolve + stagger + negative-space hold | Resolve outward into the dawn afterglow |

## Runtime, GPU, and implementation

### Host

| Item | Value |
|---|---|
| Host platform | Windows host + WSL2 Ubuntu |
| WSL distribution | Ubuntu, WSL version 2 |
| Docker Engine | 29.4.3 |
| Docker Compose | v5.1.3 |
| H3 GPU | NVIDIA GeForce RTX 4090 |
| GPU UUID | GPU-f877fbc1-9f24-bd97-3359-dd358eaa2caa |
| NVIDIA driver | 591.86 |
| VRAM | 24564 MiB |

HyperFrames browser capture used the host RTX 3060 as its hardware GPU. H3 generation itself ran in the Docker Compose h3-4090 service on the RTX 4090; these GPU roles are distinct.

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
| CUDA | 13.0 |
| ComfyUI arguments | --listen 0.0.0.0 --port 8188 --disable-pinned-memory --disable-async-offload --fp16-intermediates --preview-method none |
| Runtime environment | H3_MEMORY_USAGE_FACTOR=1.0; CUDA_MODULE_LOADING=LAZY; PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True |
| Input mount | ./runtime/4090/input:/opt/ComfyUI/input |
| Output mount | ./runtime/4090/output:/opt/ComfyUI/output |
| Model mount | ./models:/opt/ComfyUI/models:ro |

Models and implementation:

- Diffusion: models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors (20,970,379,616 bytes)
- Text encoder: models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors (15,687,142,551 bytes)
- Video VAE: models/vae/minimax_h3_video_vae_fp16.safetensors (5,207,808,496 bytes)
- Audio VAE: models/vae/minimax_h3_audio_vae_fp32.safetensors (605,254,808 bytes)
- Motion Context custom node: revision 15fc6a7bf7b78efb27f33d7eef3818e7ed0e118a
- SageAttention: sageattn_qk_int8_pv_fp16_cuda
- EasyCache, Sol-Attn, and Spectrum: disabled
- Custom-node source: [NikoDemon80/ComfyUI-H3-Motion-Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context)

The revision and the complete workflow graphs are fixed in [workflows/manifest.json](./workflows/manifest.json) and segment_01_api.json through segment_05_api.json.

## Fixed H3 conditions

| Item | Setting |
|---|---|
| Mode | T2V; no reference image |
| Resolution | 1280×704, 720p-equivalent and divisible by 32 |
| FPS | 24 |
| Raw frames per segment | 158 |
| Steps | 20 |
| Sampler / scheduler | res_multistep / simple |
| Denoise | 1.0 |
| Seed | 2026080911, shared by all segments |
| Context length | 22 |
| Audio context length | 22 |
| Encode mode | video |
| Anchor | head |
| Audio mode | timeline |
| Trim | match_tail=true |
| Attention | generic FP16 CUDA SageAttention only |

The English visual prompts embed Japanese singing instructions:

~~~text
Female Japanese vocals singing exactly 「夜を越えて　光を探す」
Female Japanese vocals sing exactly 「君となら　まだ飛べる」
Female Japanese vocals sing exactly 「雨の向こう　夢が見える」
Female Japanese vocals sing exactly 「この瞬間を　抱きしめて」
Female Japanese vocals sing exactly 「明日へ行こう　また会おう」
~~~

These are planned prompt lines. The generated vocal content was not checked with ASR.

## Fixed HyperFrames conditions

| Item | Value |
|---|---|
| Project | hyperframes-mv-lyrics |
| HyperFrames | 0.7.102 |
| Skill | music-to-video |
| Creative preset | broadside |
| Canvas | 1280×704 |
| Render FPS | 30 |
| Render quality | high |
| Frame count | 878 |
| Video plate | assets/h3_jpop_mv_5segment_keyint30.mp4 |
| Audio | assets/bgm.mp3 |
| Lyric plan | STORYBOARD.md |
| Audio map | audiomap.json / assets/audio-data.json |

The original 24 fps plate was re-encoded to 30 fps with GOP30 so HyperFrames random frame seeking would not operate over long keyframe intervals:

~~~powershell
ffmpeg -y -hide_banner -loglevel error -i outputs/h3_jpop_mv_5segment_merged.mp4 -c:v libx264 -r 30 -g 30 -keyint_min 30 -sc_threshold 0 -pix_fmt yuv420p -c:a copy -movflags +faststart hyperframes-mv-lyrics/assets/h3_jpop_mv_5segment_keyint30.mp4
~~~

Intermediate plate SHA-256: CB375A6C1E0D783444D6725AA2C57C7CADD0F1BB23523BE7D843F1A6C26DCAA7.

## Reproduction

From the repository root (<repo-root>):

1. Start H3 and verify the ComfyUI endpoint:

~~~powershell
docker compose --profile 4090 up -d h3-4090
Invoke-RestMethod http://127.0.0.1:8188/system_stats
~~~

2. Generate and run the five H3 workflows:

~~~powershell
python scripts/build-h3-mv-workflows.py --output-dir experiments/06-production-pipelines/jpop-mv-5segment/workflows
powershell -ExecutionPolicy Bypass -File scripts/run-h3-mv.ps1 -Port 8188 -TimeoutSeconds 7200
powershell -ExecutionPolicy Bypass -File scripts/merge-h3-mv.ps1
~~~

run-h3-mv.ps1 submits each segment to the ComfyUI API and copies the previous segment into runtime/4090/input/h3_mv for the next run. [run-progress.json](./run-progress.json) records Prompt IDs, ComfyUI execution time, ffprobe, blackdetect, bytes, and SHA-256.

3. Rebuild, check, and render the HyperFrames project. The first initialization is:

~~~powershell
npx hyperframes init experiments/06-production-pipelines/jpop-mv-5segment/hyperframes-mv-lyrics --non-interactive --example=blank --skill=music-to-video
~~~

Then use the included frame.md, BRIEF.md, STORYBOARD.md, compositions/frames/*.html, and assets/*:

~~~powershell
python scripts/build-h3-mv-lyric-frames.py --output-dir experiments/06-production-pipelines/jpop-mv-5segment/hyperframes-mv-lyrics/compositions/frames --audio-data experiments/06-production-pipelines/jpop-mv-5segment/audio-data.json
node scripts/patch-h3-mv-hyperframes-index.mjs experiments/06-production-pipelines/jpop-mv-5segment/hyperframes-mv-lyrics
cd experiments/06-production-pipelines/jpop-mv-5segment/hyperframes-mv-lyrics
npm install
npm run check -- --snapshots
npx hyperframes@0.7.102 render . --skill=music-to-video --quality high --output renders/h3_jpop_mv_lyric_motion.mp4 --fps 30
~~~

The snapshot check passed lint, runtime, layout, motion, and WCAG AA contrast checks. Text contrast was 64/64 pass.

## Outputs and validation

### H3 segment outputs

| Segment | Prompt ID | Output | Bytes | SHA-256 | blackdetect |
|---:|---|---|---:|---|---:|
| 1 | 3efb7532-36e0-40b4-a2ff-0cb2da0cf610 | runtime/4090/output/video/h3_mv/segment_01_00001_.mp4 | 1,530,760 | 0E49C3F87CD955FAD2E01059AE8EC86F2386D582368A952A0A9F5223508D5D96 | 0 |
| 2 | 335aedc6-8b92-4319-b75a-40e6ec0c476f | runtime/4090/output/video/h3_mv/segment_02_00001_.mp4 | 1,738,920 | 517FDF145AA5D2C2A71A598957B5702C4094765F6055D207A6B74167F2A254CF | 0 |
| 3 | 89ebf33d-0f0e-48e3-b3c1-a268d6e5cb47 | runtime/4090/output/video/h3_mv/segment_03_00001_.mp4 | 1,232,107 | 2856C6E0E1DC7C4889DF920FFE2E4E83B25490929186222C062D2E7AD50736E4 | 0 |
| 4 | 2562fdd9-8b43-423f-b86a-ac4594281ff0 | runtime/4090/output/video/h3_mv/segment_04_00001_.mp4 | 1,258,854 | 31A121BC62C2EFA43C3E6FB969D07EF9990BCE2C998C2DB3BFFFF232AAC1CF21 | 0 |
| 5 | 3dbe432d-cf8f-42fa-8243-212ded5df970 | runtime/4090/output/video/h3_mv/segment_05_00001_.mp4 | 1,170,175 | F44334ADDB5F4103BB481638763D333EF4591D8FDC2EC8DDC546E6739541823E | 0 |

All H3 segments are H.264/AAC at 1280×704 / 24 fps with 32000 Hz stereo audio. All five ComfyUI history runs completed; this run had no OOM and no CUDA runtime error.

### H3 merged plate

| Item | Value |
|---|---|
| Path | outputs/h3_jpop_mv_5segment_merged.mp4 |
| Evidence status | local-only; the public visual check is [the frame tile](./previews/contact-sheet.jpg) |
| Method | ffmpeg concat filter; libx264 CRF 18; AAC 192k; faststart |
| Video | H.264, 1280×704, 702 frames, 24 fps |
| Audio | AAC, 32 kHz stereo |
| Duration | 29.256 s |
| Bytes | 10,104,411 |
| SHA-256 | 28F1921260CF45A710E7C1BB8D64E72A91889379F0495C5BDB91217F2E6EF92E |

### HyperFrames final

| Item | Value |
|---|---|
| Path | hyperframes-mv-lyrics/renders/h3_jpop_mv_lyric_motion.mp4 |
| Video | H.264, 1280×704, 878 frames, 30 fps |
| Audio | AAC, 48 kHz stereo after render-time normalization |
| Duration | 29.266667 s |
| Bytes | 19,614,049 |
| SHA-256 | 097EBE221189EE2726319DDC555E57B813483BCA9FD48640E18E75830B179050 |
| blackdetect | none detected |
| freezedetect | no still interval of 0.50 s or longer |

The five-scene review contact sheet is [hyperframes-mv-lyrics/verification/h3_mv_contact.jpg](./hyperframes-mv-lyrics/verification/h3_mv_contact.jpg). It shows the backgrounds, singer, clothing, and lyric panels; no black frame or long freeze was observed.

## Interpretation and limitations

The verified result is that H3-generated audio can remain the common timeline for both the video and lyric treatment, and that volume, band energy, and beat events can control lyric motion in a music-video-style composition.

The following were not established:

- ASR confirmation that the Japanese pronunciation and lyrics match the prompt.
- Quantitative scores for singing continuity, person identity, or music seams between segments.
- The same five-segment, 720p-equivalent condition on an RTX 3060.
- Speed or audio-quality differences from enabling EasyCache, Sol-Attn, or Spectrum.
- Copyright and public-use conditions for the original H3-generated audio.

Accordingly, this record supports the narrower claim that analyzed loudness, band energy, and beat data synchronized lyric motion to an H3-generated music asset. A claim about lyric accuracy requires a later ASR check.

## Reference files and records

- [README.md](./README.md): Japanese/mixed detailed record
- [README.en.md](./README.en.md): this English counterpart
- [experiment.json](./experiment.json): machine-readable experiment record
- [workflows/manifest.json](./workflows/manifest.json): full segment prompts, seed, and Motion Context conditions
- [run-progress.json](./run-progress.json): execution times, Prompt IDs, and output checks
- [merge.json](./merge.json): H3 concat ffprobe, SHA-256, and blackdetect
- [audiomap.json](./audiomap.json): BPM, beats, bars, events, and energy phases
- [audio-data.json](./audio-data.json): 30 fps RMS and 16-band FFT
- [STORYBOARD.md](./hyperframes-mv-lyrics/STORYBOARD.md): five-frame timeline and motion design
- [BRIEF.md](./hyperframes-mv-lyrics/BRIEF.md): music-to-video brief
