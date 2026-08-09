# X Publishing and Simulator Index

> 日本語版: [README.md](./README.md)

This directory contains X post payloads and pre-publication simulators for the MiniMax-H3 experiments. Experiment conditions are canonical under `experiments/`; post order, copy, and attachments are canonical in each payload.

Large video/audio files are normally excluded from Git. Simulator video sources are local verification inputs; a fresh clone falls back to tracked posters and frame tiles. The public boundary is recorded as `local-only` in the experiment record and payload.

## Simulator index

| Function / date | Experiment record | Simulator | Payload |
|---|---|---|---|
| GPU comparison / 2026-08-07 | [GPU baseline](../experiments/01-baseline/gpu-baseline/README.en.md) | [3060](../sunwood-x-simulator-2026-08-07/index.html) · [4090](../sunwood-x-simulator-4090-2026-08-07/index.html) | [3060 thread](../sunwood-x-thread-payload-2026-08-07.json) · [4090 thread](../sunwood-x-thread-payload-4090-2026-08-07.json) |
| Low-step / 2026-08-08 | [LightX2V 4-step](../experiments/02-low-step-generation/lightx2v-4step/README.en.md) | [simulator](../sunwood-x-simulator-kijai-2026-08-08/index.html) | [simulation JSON](../sunwood-x-kijai-simulation-2026-08-08.json) |
| ImageGen I2V / 2026-08-08 | [four I2V scenes](../experiments/03-reference-conditioned/i2v-scenes/README.en.md) | [scene simulator](../sunwood-x-simulator-kijai-scenes-2026-08-08/index.html) | [simulation JSON](../sunwood-x-kijai-scenes-simulation-2026-08-08.json) |
| ref2va / 2026-08-08 | [ref2va 6 vs 20](../experiments/03-reference-conditioned/ref2va-6v20/README.en.md) | [ref2va simulator](../sunwood-x-simulator-ref2va-2026-08-08/index.html) | [simulation JSON](../sunwood-x-ref2va-simulation-2026-08-08.json) |
| Multi-reference R2V / 2026-08-08 | [multi-reference R2V](../experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s/README.en.md) | [R2V simulator](../sunwood-x-simulator-r2v-multi-reference-2026-08-08/index.html) | [payload](../sunwood-x-simulator-r2v-multi-reference-2026-08-08/payload.json) |
| R2V acceleration / 2026-08-09 | [Sol-Attn + Sage + EasyCache](../experiments/04-acceleration/sol-sage-easycache-4scenes-7s/README.en.md) | [acceleration simulator](../sunwood-x-simulator-r2v-optimizations-2026-08-09/index.html) | [payload](../sunwood-x-simulator-r2v-optimizations-2026-08-09/payload.json) |
| Motion Context / 2026-08-09 | [three-segment chain](../experiments/05-temporal-continuity/motion-context-3segment/README.en.md) | [Motion Context](../sunwood-x-simulator-h3-motion-context-2026-08-09/index.html) | [payload](../sunwood-x-simulator-h3-motion-context-2026-08-09/payload.json) |
| Japanese cat-café Vlog / 2026-08-09 | [five-segment Vlog](../experiments/06-production-pipelines/catcafe-vlog-5segment/README.en.md) | [cat-café Vlog](../sunwood-x-simulator-h3-catcafe-vlog-2026-08-09/index.html) | [payload](../sunwood-x-simulator-h3-catcafe-vlog-2026-08-09/payload.json) |
| Japanese synth-pop MV / 2026-08-09 | [five-segment MV](../experiments/06-production-pipelines/jpop-mv-5segment/README.en.md) | [J-pop MV](../sunwood-x-simulator-h3-mv-jpop-2026-08-09/index.html) | [payload](../sunwood-x-simulator-h3-mv-jpop-2026-08-09/payload.json) |

Dates are metadata, not classification axes. The date-named `sunwood-x-simulator-*` and `hyperframes-*` directories are legacy publication assets; new experiments belong under function-based `experiments/<category>/<slug>/`.

## Publication rules

- The parent post has no URL; replies connect to the immediately preceding post.
- Split unrelated URLs into separate replies.
- Keep attachments at four or fewer per post.
- Publish useful technical results, conditions, and limitations, not mechanical QA notes.
- Map experiment-relative paths, video SHA-256 values, and generation parameters to the payload.
- Always distinguish posted, simulation-only, uncertain, and not-posted states.
