# MiniMax-H3 Experiment Lab — Experiment Ledger

> 日本語版: [index.md](./index.md)

This ledger is organized by tested function rather than execution date, distributor, or person. Dates remain in each `experiment.json`; the record README and JSON are the canonical sources for conditions, prompts, workflows, timings, output hashes, and limitations.

The bilingual [visual gallery](./README.md) is the fastest way to inspect temporal behavior. The cross-index [video links](./video-links.md) lists public X posts and source references; each individual record README contains the complete URL list and workflow/run mapping.

## Function categories

- [01 — Baseline and GPU comparison](#01--baseline-and-gpu-comparison)
- [02 — Low-step generation](#02--low-step-generation)
- [03 — Reference-conditioned generation](#03--reference-conditioned-generation)
- [04 — Acceleration](#04--acceleration)
- [05 — Temporal continuity](#05--temporal-continuity)
- [06 — Production pipelines](#06--production-pipelines)
- [07 — Upscaling](#07--upscaling)

## 01 — Baseline and GPU comparison

| ID | Function | Status | Record | Tile |
|---|---|---|---|---|
| `2026-08-07-gpu-baseline` | RTX 3060/4090, T2V/I2V, 864×480–1280×704 | verified | [English](./01-baseline/gpu-baseline/README.md) · [日本語](./01-baseline/gpu-baseline/README.ja.md) · [JSON](./01-baseline/gpu-baseline/experiment.json) | [contact sheet](./01-baseline/gpu-baseline/previews/contact-sheet.jpg) · [manifest](./01-baseline/gpu-baseline/previews/contact-sheet.json) |
| `2026-08-07-3060-legacy-black-output` | Legacy Turbo/full-int8 + int8 VAE black-output failure | failed | [English](./01-baseline/3060-black-output/README.md) · [日本語](./01-baseline/3060-black-output/README.ja.md) · [JSON](./01-baseline/3060-black-output/experiment.json) | [contact sheet](./01-baseline/3060-black-output/previews/contact-sheet.jpg) · [manifest](./01-baseline/3060-black-output/previews/contact-sheet.json) |

## 02 — Low-step generation

| ID | Function | Status | Record | Tile |
|---|---|---|---|---|
| `2026-08-08-low-step-lightx2v-4step` | LightX2V LoRA, 4-step T2V/I2V, 1344×768, `er_sde` / `sa_solver` | verified | [English](./02-low-step-generation/lightx2v-4step/README.md) · [日本語](./02-low-step-generation/lightx2v-4step/README.ja.md) · [JSON](./02-low-step-generation/lightx2v-4step/experiment.json) | [contact sheet](./02-low-step-generation/lightx2v-4step/previews/contact-sheet.jpg) · [manifest](./02-low-step-generation/lightx2v-4step/previews/contact-sheet.json) |

## 03 — Reference-conditioned generation

| ID | Function | Status | Record | Tile |
|---|---|---|---|---|
| `2026-08-08-reference-i2v-scenes` | ImageGen start frames: car, sports, illustration, battle I2V | verified | [English](./03-reference-conditioned/i2v-scenes/README.md) · [日本語](./03-reference-conditioned/i2v-scenes/README.ja.md) · [JSON](./03-reference-conditioned/i2v-scenes/experiment.json) | [contact sheet](./03-reference-conditioned/i2v-scenes/previews/contact-sheet.jpg) · [manifest](./03-reference-conditioned/i2v-scenes/previews/contact-sheet.json) |
| `2026-08-08-reference-ref2va-6v20` | ref2va T2V/I2V, LoRA 0.8, 6 vs 20 steps | verified | [English](./03-reference-conditioned/ref2va-6v20/README.md) · [日本語](./03-reference-conditioned/ref2va-6v20/README.ja.md) · [JSON](./03-reference-conditioned/ref2va-6v20/experiment.json) | [contact sheet](./03-reference-conditioned/ref2va-6v20/previews/contact-sheet.jpg) · [manifest](./03-reference-conditioned/ref2va-6v20/previews/contact-sheet.json) |
| `2026-08-08-reference-multi-r2v-4scenes-7s` | Three references: background + two characters; four scenes, about 7 seconds | verified | [English](./03-reference-conditioned/multi-reference-r2v-4scenes-7s/README.md) · [日本語](./03-reference-conditioned/multi-reference-r2v-4scenes-7s/README.ja.md) · [JSON](./03-reference-conditioned/multi-reference-r2v-4scenes-7s/experiment.json) | [contact sheet](./03-reference-conditioned/multi-reference-r2v-4scenes-7s/previews/contact-sheet.jpg) · [manifest](./03-reference-conditioned/multi-reference-r2v-4scenes-7s/previews/contact-sheet.json) |

## 04 — Acceleration

| ID | Function | Status | Record | Tile |
|---|---|---|---|---|
| `2026-08-08-acceleration-sol-sage-easycache-4scenes-7s` | Sol-Attn + generic FP16 CUDA SageAttention + EasyCache | verified | [English](./04-acceleration/sol-sage-easycache-4scenes-7s/README.md) · [日本語](./04-acceleration/sol-sage-easycache-4scenes-7s/README.ja.md) · [JSON](./04-acceleration/sol-sage-easycache-4scenes-7s/experiment.json) | [contact sheet](./04-acceleration/sol-sage-easycache-4scenes-7s/previews/contact-sheet.jpg) · [manifest](./04-acceleration/sol-sage-easycache-4scenes-7s/previews/contact-sheet.json) |

## 05 — Temporal continuity

| ID | Function | Status | Record | Tile |
|---|---|---|---|---|
| `niko-h3-motion-context-3segment` | Video/audio latent and 22-frame context carry-over | verified | [English](./05-temporal-continuity/motion-context-3segment/README.md) · [日本語](./05-temporal-continuity/motion-context-3segment/README.ja.md) · [JSON](./05-temporal-continuity/motion-context-3segment/experiment.json) | [contact sheet](./05-temporal-continuity/motion-context-3segment/previews/contact-sheet.jpg) · [manifest](./05-temporal-continuity/motion-context-3segment/previews/contact-sheet.json) |

## 06 — Production pipelines

| ID | Function | Status | Record | Tile |
|---|---|---|---|---|
| `h3-japanese-catcafe-vlog-5segment` | English prompts + Japanese dialogue; five-segment cat-café Vlog | verified | [English](./06-production-pipelines/catcafe-vlog-5segment/README.md) · [日本語](./06-production-pipelines/catcafe-vlog-5segment/README.ja.md) · [JSON](./06-production-pipelines/catcafe-vlog-5segment/experiment.json) | [contact sheet](./06-production-pipelines/catcafe-vlog-5segment/previews/contact-sheet.jpg) · [manifest](./06-production-pipelines/catcafe-vlog-5segment/previews/contact-sheet.json) |
| `h3-mv-jpop-5segment` | H3 generated audio, beat analysis, and HyperFrames lyric motion | verified | [English](./06-production-pipelines/jpop-mv-5segment/README.md) · [日本語](./06-production-pipelines/jpop-mv-5segment/README.ja.md) · [JSON](./06-production-pipelines/jpop-mv-5segment/experiment.json) | [contact sheet](./06-production-pipelines/jpop-mv-5segment/previews/contact-sheet.jpg) · [manifest](./06-production-pipelines/jpop-mv-5segment/previews/contact-sheet.json) |

## 07 — Upscaling

| ID | Function | Status | Record | Tile |
|---|---|---|---|---|
| `seedvr2-rtx4090-fhd-4k-segmented` | SeedVR2 FHD / 4K upscaling of an H3 1344×768 source; naive 4K OOM and temporal segmentation workaround | verified | [English](./07-upscaling/seedvr2-4k-rtx4090/README.md) · [日本語](./07-upscaling/seedvr2-4k-rtx4090/README.ja.md) · [JSON](./07-upscaling/seedvr2-4k-rtx4090/experiment.json) · [REPORT](./07-upscaling/seedvr2-4k-rtx4090/REPORT.md) | [contact sheet](./07-upscaling/seedvr2-4k-rtx4090/previews/contact-sheet.jpg) · [manifest](./07-upscaling/seedvr2-4k-rtx4090/previews/contact-sheet.json) |

## Shared entry points

- GPU benchmark indexes: [`runtime/3060`](../runtime/3060/benchmark/index.md) / [日本語](../runtime/3060/benchmark/index.ja.md) and [`runtime/4090`](../runtime/4090/benchmark/index.md) / [日本語](../runtime/4090/benchmark/index.ja.md)
- Shared workflows: [`workflows/`](../workflows)
- New experiment template: [`experiments/_template/README.md`](./_template/README.md)
- X payload/simulator index: [`social/README.md`](../social/README.md)
- X video/source cross-index: [`video-links.md`](./video-links.md) / [日本語](./video-links.ja.md)
- Documentation language policy: [`docs/guide/documentation.md`](../docs/guide/documentation.md)

Generated MP4, audio, and model weights are normally excluded from Git. A public clone contains tracked tiles and manifests; each record retains local paths, media facts, and SHA-256 values for local outputs.
