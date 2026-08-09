# RTX 3060 Black Output on the Legacy Route (2026-08-07)

Language navigation: [Japanese record](./README.ja.md)

- ID: `2026-08-07-3060-legacy-black-output`
- Status: `failed`
- GPU: RTX 3060 12GB
- Owner: `MiniMax-H3 Experiment Lab`

Frame tile: [contact sheet](./previews/contact-sheet.jpg) / [manifest](./previews/contact-sheet.json)

Record: [experiment.json](./experiment.json) · [Japanese README](./README.ja.md)

![3060 black-output frame tile](./previews/contact-sheet.jpg)

> The tracked frame tile and manifest are the public visual evidence for this failed record. The failed source MP4s remain local-only; their hashes are preserved in the manifest.

## Purpose and hypothesis

Test whether the initially used Turbo/full-int8 configuration could generate a video on an RTX 3060 under its memory constraints.

## Status and evidence boundary

This experiment is explicitly `failed`. The generated-result video was not posted to X and remains `local-only`. The tracked contact sheet and manifest are the public visual evidence; the failed source MP4s are not treated as public success videos.

## X video and reference URLs

- Generated video: none. There is no generated-result X URL for this record, and the black-output failure was not presented as a successful public video.
- Condition reference: [TlanoAI RTX 3060 post](https://x.com/TlanoAI/status/2084940455809286397)
- Related successful re-verification: [GPU baseline comparison](../gpu-baseline/README.md). Its successful videos are a separate experiment and must not be attributed to this failed record.

## Runtime and key conditions

- GPU: RTX 3060 12GB
- Base: Turbo/full-int8
- Video VAE: Kijai experimental int8 video VAE
- Sampler: Turbo
- Steps: 8
- Runtime: legacy Docker Compose route

## Workflow/run mapping and measured results

No public workflow file is attached to this failed record. The record maps the two tested legacy-route variants below:

| `experiment.json` run ID | Variant | Status | Measurement |
|---|---|---|---|
| `legacy-turbo-int8` | Turbo/full-int8 base with the legacy route | failed | all frames black by `blackdetect`; black signal by `signalstats`; no OOM |
| `kijai-int8-vae-ab` | A/B switch to Kijai int8 VAE | failed | black output; no OOM |

The resulting MP4s did not become valid visual results. The route was excluded from the successful baseline results, and the configuration was changed to the official FP16 video VAE / FP32 audio VAE path for re-verification.

## Reproduction and evidence links

- Primary record: [experiment.json](./experiment.json)
- Public evidence tile: [contact sheet](./previews/contact-sheet.jpg) and [manifest](./previews/contact-sheet.json)
- Black-output inspection, CUDA OOM checks, and recovery procedure: [verification-log.en.md](../../../verification-log.en.md) / [日本語](../../../verification-log.md)
- Condition research and root-cause isolation: [research-notes.en.md](../../../research-notes.en.md) / [日本語](../../../research-notes.md)
- Successful follow-up under the corrected conditions: [GPU baseline README](../gpu-baseline/README.md)

The old MP4s may remain under the local runtime. If present, they are failure evidence only and should not be reused as successful outputs.

## Conclusion and limitations

The legacy Turbo/full-int8 plus Kijai int8 VAE route produced black video and was excluded from the final configuration.

- The model files needed to reproduce the old MP4s are outside Git; another PC would need to obtain them separately.
- The black-output cause is not assigned to one node alone. This record treats it as a route-level issue involving VAE, base model, sampler, and Docker/runtime differences.

## Prevention checklist

1. Prefer the VAE and major PyTorch/CUDA versions specified by the reference post.
2. Immediately inspect new output with `ffprobe`, `blackdetect`, `signalstats`, and extracted frames.
3. Keep black output and OOM cases in a separate `failed` record rather than mixing them into the successful experiment results.
