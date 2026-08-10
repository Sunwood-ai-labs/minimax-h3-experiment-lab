# MiniMax-H3 Ref2VA vs FL2VA with imagegen references

> Public record: [this experiment folder](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10)
>
> The folder contains the full reference prompts, three reference PNGs, both API workflows, `experiment.json`, and extracted frames. Generated MP4s are kept out of Git by repository policy and were attached to the X replies.

## Result

The same three newly generated reference images, prompt, seed, sampler, scheduler, resolution, and frame count were used for both runs. Only the `UNETLoader` checkpoint changed.

- Both runs succeeded at 1280×704, 175 frames, 24 fps, and 7.292 seconds with audio.
- No OOM occurred and `blackdetect=d=0.1:pix_th=0.10` found zero black intervals in both outputs.
- Ref2VA made the environment-first entrance clearer and had the higher encoded video bitrate in this pair.
- FL2VA brought the subject into frame earlier and produced louder audio.
- This run does not support a universal claim that FL2VA is higher quality.

See the [contact sheet](./previews/contact-sheet.jpg) and [extracted frames](./outputs/). The tile and source MP4s were attached to the X replies; their SHA-256 values are recorded in `experiment.json` and in the video replies. The tile videos are muted for comparison.

## Fixed conditions

| Item | Condition |
|---|---|
| GPU | RTX 4090 |
| ComfyUI | 0.30.0 / `local/minimax-h3-comfyui:v0.30.0` |
| Node | `MiniMaxH3ReferenceToVideo` |
| Resolution / frames | 1280×704 / 175 / 24 fps |
| Steps / sampler / scheduler | 20 / `res_multistep` / `simple` |
| `ref_image_size` | `match` |
| Seed | `2026081011` |
| LoRA / EasyCache | none / none |

## Run comparison

| Run | Checkpoint | ComfyUI time | MP4 bytes | Video bitrate | Audio mean / max |
|---|---|---:|---:|---:|---:|
| A | Ref2VA | 898.216 s | 2,461,614 | 2,556,907 bps | -46.5 / -16.3 dB |
| B | FL2VA | 980.446 s | 2,165,866 | 2,232,987 bps | -39.1 / -14.9 dB |

## Artifacts

- [experiment.json](./experiment.json)
- [Ref2VA workflow](./workflows/a-ref2va-api.json) ([GitHub direct link](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10/workflows/a-ref2va-api.json))
- [FL2VA workflow](./workflows/b-fl2va-api.json) ([GitHub direct link](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10/workflows/b-fl2va-api.json))
- [full imagegen prompts](./reference-prompts.md) ([GitHub direct link](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10/reference-prompts.md))
- [reference assets](./references/)
  - [environment PNG](https://raw.githubusercontent.com/Sunwood-ai-labs/minimax-h3-experiment-lab/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10/references/ref-imagegen-rooftop-background.png)
  - [portrait PNG](https://raw.githubusercontent.com/Sunwood-ai-labs/minimax-h3-experiment-lab/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10/references/ref-imagegen-aoi-portrait.png)
  - [profile PNG](https://raw.githubusercontent.com/Sunwood-ai-labs/minimax-h3-experiment-lab/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10/references/ref-imagegen-aoi-fullbody.png)
- [sample frames](./outputs/)

The two workflows share the same three input image hashes and change only `UNETLoader.inputs.unet_name`.

## Acquire the models

The model weights are not stored in GitHub. Download them from the official Hugging Face repository at revision `93acf8c91365d40dc32a3abd19af06df6b6f7c65`. Run both the `ref2va` and `fl2va` profiles so both UNETs are present in `models/diffusion_models/`; the shared files plus both checkpoints require about 59.1 GiB.

The exact filenames, byte counts, and SHA-256 values are in `experiment.json` and `models/manifest.json`.

```powershell
Copy-Item .env.example .env
(Get-Content .env) -replace '^H3_PROFILE=.*', 'H3_PROFILE=ref2va' | Set-Content .env
docker compose --profile download run --rm model-downloader
(Get-Content .env) -replace '^H3_PROFILE=.*', 'H3_PROFILE=fl2va' | Set-Content .env
docker compose --profile download run --rm model-downloader
```

## Reproduce

```powershell
Copy-Item .\experiments\03-reference-conditioned\ref2va-vs-fl2va-imagegen-2026-08-10\references\*.png .\runtime\4090\input\ -Force
docker compose --profile 4090 build h3-4090
docker compose --profile 4090 up -d h3-4090
pwsh -File .\scripts\run-h3-post-condition.ps1 `
  -Gpu 4090 -Port 8188 `
  -Workflow .\experiments\03-reference-conditioned\ref2va-vs-fl2va-imagegen-2026-08-10\workflows\a-ref2va-api.json `
  -OutputPrefix video/MiniMax_H3_imagegen_ab_ref2va `
  -LowVram $false -Seed 2026081011 -TimeoutSeconds 2400

pwsh -File .\scripts\run-h3-post-condition.ps1 `
  -Gpu 4090 -Port 8188 `
  -Workflow .\experiments\03-reference-conditioned\ref2va-vs-fl2va-imagegen-2026-08-10\workflows\b-fl2va-api.json `
  -OutputPrefix video/MiniMax_H3_imagegen_ab_fl2va `
  -LowVram $false -Seed 2026081011 -TimeoutSeconds 2400
```

The helper saves ComfyUI status, runtime, output bytes, ffprobe, blackdetect, and output SHA-256 under `runtime/4090/benchmark/`. For direct API use, POST the workflow JSON as the `prompt` field to `http://127.0.0.1:8188/prompt`; the `LoadImage` names must match the copied reference PNGs.

## Limitations

This is one scene, one seed, and one generated reference set. No blind preference test or automated identity score was run, and `ref_image_size=max` was not tested. The checkpoint swap is not the official R2V pairing, so multi-scene follow-up is still needed.

## Sources

- [ComfyUI H3 PR #15224](https://github.com/Comfy-Org/ComfyUI/pull/15224)
- [Official MiniMax-H3 R2V workflow](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json)
- [Original Reddit report](https://www.reddit.com/r/StableDiffusion/comments/1vk6j2w/anyone_figure_out_how_to_get_fl2va_quality_with/)
- [Referenced X post](https://x.com/umiyuki_ai/status/2086621244234039651)
