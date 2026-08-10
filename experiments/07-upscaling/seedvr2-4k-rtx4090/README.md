# MiniMax-H3 Experiment: SeedVR2 FHD / 4K upscaling on RTX 4090

> 日本語版: [README.ja.md](./README.ja.md)

- ID: `seedvr2-rtx4090-fhd-4k-segmented`
- Date: `2026-08-10` (JST)
- Category: `07-upscaling`
- Status: `verified`
- GPU: NVIDIA GeForce RTX 4090, 24,564 MiB
- Owner: `MiniMax-H3 Experiment Lab`

The machine-readable canonical record is [`experiment.json`](./experiment.json). The full Japanese run report is [`REPORT.md`](./REPORT.md). The tracked visual proof is [the contact sheet](./previews/contact-sheet.jpg), with its [sampling manifest](./previews/contact-sheet.json).

## X video and reference URLs

- Generated-video thread: [main post](https://x.com/hAru_mAki_ch/status/2086601484901495018) · [experiment evidence reply](https://x.com/hAru_mAki_ch/status/2086601566224814552)
- Thread continuation: [reference URL reply](https://x.com/hAru_mAki_ch/status/2086601653873168501) · [continuity note](https://x.com/hAru_mAki_ch/status/2086601745233510417)
- Source/reference post: [aihonobono2023](https://x.com/aihonobono2023/status/2086281213334213104?s=46)
- Model source: [Comfy-Org/SeedVR2](https://huggingface.co/Comfy-Org/SeedVR2)
- H3 model context: [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)
- Workflow/run mapping: the four API workflows are in [`workflows/`](./workflows/); the executed JSON, Markdown and VRAM traces are in [`runs/`](./runs/). The generated MP4s are local-only paths recorded in `experiment.json`.

## Hypothesis

FHD should fit in one SeedVR2 pass on a 24 GiB RTX 4090. A full 4K sequence may exceed VRAM during `VAEDecodeTiled`, while small temporal slices should keep peak memory bounded enough to complete the same 158 frames.

This is a post-process experiment. The input was an existing MiniMax-H3 LightX2V I2V battle clip at 1344×768; H3 generation itself was not rerun here.

## Sources

Detailed provenance is recorded in [`sources.md`](./sources.md) and [`sources.ja.md`](./sources.ja.md). The reference post motivates the follow-up experiment, but its exact workflow, prompt, seed and internal settings are not claimed as reproduced. SeedVR2 files were downloaded from [Comfy-Org/SeedVR2](https://huggingface.co/Comfy-Org/SeedVR2); local byte counts and SHA-256 values are recorded in `experiment.json`.

## Conditions

| Item | Fixed value |
|---|---|
| Input | 1344×768, 158 frames, 24 fps, video 6.583333 s, source AAC 6.575 s |
| Targets | FHD 1920×1080 and 4K 3840×2160 |
| SeedVR2 | 3B INT8 diffusion model + FP16 EMA VAE |
| Sampler | Euler / `simple`, 1 step, CFG 1.0, seed `2026081001` |
| Preprocess | Lanczos resize and center crop |
| VAE tiling | tile 512, overlap 128, temporal size 64, temporal overlap 8 |
| Container | `h3-4090`, ComfyUI 0.30.0, PyTorch 2.11.0+cu130 |
| Audio | source AAC retained and remuxed onto the verified 4K video |
| 4K fallback | eight 0.75 s segments plus a final 0.583333 s segment |

## Reproduction kit

- Compose service: [`compose.yaml`](../../../compose.yaml)
- Image build: [`Dockerfile`](../../../Dockerfile)
- Host config: [`.env.example`](../../../.env.example)
- Workflow JSON: [`workflows/`](./workflows/)
- Single-run runner: [`run-seedvr2-api.ps1`](./run-seedvr2-api.ps1)
- 4K segmented runner: [`run-seedvr2-4k-segments.ps1`](./run-seedvr2-4k-segments.ps1)
- Model hashes and source: [`experiment.json`](./experiment.json) and [`models/README.md`](../../../models/README.md)

Start the ComfyUI service, then run the FHD workflow:

```powershell
.\run-seedvr2-api.ps1 `
  -Workflow .\workflows\seedvr2_upscale_fhd_api.json `
  -ReportName seedvr2_fhd_full `
  -TimeoutSeconds 14400
```

Run all nine 4K segments:

```powershell
.\run-seedvr2-4k-segments.ps1 `
  -StartSegment 0 -SegmentCount 9 -SegmentSeconds 0.75 `
  -TotalSeconds 6.583333 -TimeoutSeconds 3600
```

Use [`workflows/seedvr2_4k_concat_list.txt`](./workflows/seedvr2_4k_concat_list.txt) to concatenate the nine local-only segment videos. The verified deliverable additionally remuxes the source AAC with a `-0.031006` second input offset:

```text
ffmpeg -itsoffset -0.031006 -i segmented_full.mp4 -i source.mp4 \
  -map 0:v:0 -map 1:a:0 -c:v copy -c:a copy verified2.mp4
```

## Results

| Run | Status | Local start (JST) | Local end (JST) | Wall | Peak VRAM | Max temp | Output |
|---|---|---|---|---:|---:|---:|---|
| FHD full | success | 00:06:10.126 | 00:10:30.726 | 260.600 s | 13,199 MiB | 84°C | 1920×1080 / 158f |
| 4K smoke | success | 00:11:40.313 | 00:12:40.512 | 60.199 s | 12,677 MiB | 81°C | 3840×2160 / 9f |
| 4K naive full | failed: `VAEDecodeTiled` OOM | 00:13:06.241 | 00:29:43.191 | 996.950 s | 24,004 MiB | 85°C | no output |
| 4K segmented full | success: 9/9 | 00:31:52.222–00:51:23.321 | 00:53:13.753 | 1,228.317 s* | 16,400 MiB | 86°C | 3840×2160 / 158f |

\* Sum of SeedVR2 segment wall times; concatenate/remux time is excluded.

The verified 4K output is local-only at:

```text
runtime/4090/output/video/seedvr2_experiment_4k_segmented_full_verified2.mp4
bytes: 22,213,512
SHA-256: BF4D8E497DD6FC69ED07F5C2256623988ED9E6963C992050A51E6B2CD842FB07
```

`ffprobe` reports 3840×2160, H.264/AAC, 158 frames, 24 fps, video 6.583333 s, audio 6.575 s, both starting at 0. `blackdetect` with the recorded check found no black interval. The tracked contact sheet samples the 4K segment boundaries so temporal discontinuity can be inspected after cloning.

## Interpretation

The bottleneck is temporal memory in the 4K VAE decode path, not the H3 generation stage. A 9-frame 4K input fits comfortably, but the full 158-frame pass reaches almost the entire 24 GiB budget and fails. Temporal segmentation is therefore the practical RTX 4090 strategy, at the cost of about 20 minutes of SeedVR2 processing and a required boundary review.

## Limitations

- The reference post's exact workflow, prompt, seed and model revision were not available and were not inferred.
- The segmented result uses independent temporal slices; the boundary sheet is visual evidence, not a quantitative seam score.
- The downloaded SeedVR2 model revision was not captured during the original download; local byte counts and SHA-256 values are fixed in `experiment.json`.
- Generated MP4s, source PNGs and model weights remain local-only by repository convention. The raw reports and VRAM CSV files in `runs/` preserve the execution evidence.
