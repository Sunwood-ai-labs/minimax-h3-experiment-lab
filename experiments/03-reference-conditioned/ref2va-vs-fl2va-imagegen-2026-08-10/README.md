# MiniMax-H3 Ref2VA vs FL2VA with imagegen references

## Result

The same three newly generated reference images, prompt, seed, sampler, scheduler, resolution, and frame count were used for both runs. Only the `UNETLoader` checkpoint changed.

- Both runs succeeded at 1280×704, 175 frames, 24 fps, and 7.292 seconds with audio.
- No OOM occurred and `blackdetect=d=0.1:pix_th=0.10` found zero black intervals in both outputs.
- Ref2VA made the environment-first entrance clearer and had the higher encoded video bitrate in this pair.
- FL2VA brought the subject into frame earlier and produced louder audio.
- This run does not support a universal claim that FL2VA is higher quality.

See the [contact sheet](./previews/contact-sheet.jpg), the side-by-side [tile video](./outputs/ref2va-vs-fl2va-tile.mp4), the stacked [vertical tile video](./outputs/ref2va-vs-fl2va-tile-vertical.mp4), the full-width [vertical tile video](./outputs/ref2va-vs-fl2va-tile-vertical-fullwidth.mp4), [Ref2VA video](./outputs/ref2va.mp4), and [FL2VA video](./outputs/fl2va.mp4). The tile videos are muted for comparison.

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
- [Ref2VA workflow](./workflows/a-ref2va-api.json)
- [FL2VA workflow](./workflows/b-fl2va-api.json)
- [imagegen prompts](./reference-prompts.md)
- [reference assets](./references/)
- [sample frames and copied videos](./outputs/)

The two workflows share the same three input image hashes and change only `UNETLoader.inputs.unet_name`.

## Reproduction

```powershell
docker compose --profile 4090 up -d h3-4090
$workflow = Get-Content -Raw .\experiments\03-reference-conditioned\ref2va-vs-fl2va-imagegen-2026-08-10\workflows\a-ref2va-api.json | ConvertFrom-Json
$body = @{ prompt = $workflow; client_id = ([guid]::NewGuid().ToString()) } | ConvertTo-Json -Depth 50
Invoke-RestMethod -Uri http://127.0.0.1:8188/prompt -Method Post -ContentType application/json -Body $body
```

Use `b-fl2va-api.json` for the FL2VA run.

## Limitations

This is one scene, one seed, and one generated reference set. No blind preference test or automated identity score was run, and `ref_image_size=max` was not tested. The checkpoint swap is not the official R2V pairing, so multi-scene follow-up is still needed.

## Sources

- [ComfyUI H3 PR #15224](https://github.com/Comfy-Org/ComfyUI/pull/15224)
- [Official MiniMax-H3 R2V workflow](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json)
- [Original Reddit report](https://www.reddit.com/r/StableDiffusion/comments/1vk6j2w/anyone_figure_out_how_to_get_fl2va_quality_with/)
- [Referenced X post](https://x.com/umiyuki_ai/status/2086621244234039651)
