# MiniMax-H3 GPU Baseline Comparison (2026-08-07)

Language navigation: [Japanese record](./README.ja.md)

- ID: `2026-08-07-gpu-baseline`
- Status: `verified`
- GPUs: RTX 3060 / RTX 4090
- Owner: `MiniMax-H3 Experiment Lab`

Frame tile: [contact sheet](./previews/contact-sheet.jpg) / [manifest](./previews/contact-sheet.json)

Record: [experiment.json](./experiment.json) · [Japanese README](./README.ja.md)

![GPU baseline frame tile](./previews/contact-sheet.jpg)

> The tracked frame tile and manifest are the public visual evidence for this record. Source MP4s under `runtime/*/output` remain local-only.

## Purpose

Run RTX 3060 and RTX 4090 as separate Docker Compose services, then verify the reference/recipe conditions and the feasibility of approximately 720p-class text-to-video (T2V) and image-to-video (I2V) generation.

## Status and evidence boundary

The experiment is `verified`. The record marks four 1280×704 video posts as posted on X. Other baseline runs remain local-only. The tracked tile and manifest are the public visual evidence; the source MP4s are not treated as public artifacts merely because they exist under a local runtime directory.

## X video URLs and reference URLs

### Generated video posts

- RTX 3060 T2V: [X video](https://x.com/hAru_mAki_ch/status/2085730512677855266)
- RTX 3060 I2V: [X video](https://x.com/hAru_mAki_ch/status/2085731260169953315)
- RTX 4090 T2V: [X video](https://x.com/hAru_mAki_ch/status/2085738947553185852)
- RTX 4090 I2V: [X video](https://x.com/hAru_mAki_ch/status/2085738981866811714)

### Reference and research URLs

- RTX 3060 reference conditions: [TlanoAI post](https://x.com/TlanoAI/status/2084940455809286397)
- RTX 4090 reference post: [yume_arasaki post](https://x.com/yume_arasaki/status/2084766655331360999)
- RTX 4090 linked recipe: [RTX-4090-3090-Minimax-H3-15s](https://github.com/yume-arasaki/RTX-4090-3090-Minimax-H3-15s)
- Researched but excluded because key sampler/offload conditions were missing: [lizikk_zhu](https://x.com/lizikk_zhu/status/2084859489115648336) and [thekhoma](https://x.com/thekhoma/status/2084504336173076800)
- Researched but excluded because the exact base/LoRA/VAE/sampler were unknown: [onigirikila](https://x.com/onigirikila/status/2084858171462754672)

### Workflow/run and video mapping

This experiment is recorded per run rather than through an individual workflow README. The RTX 3060 runs use Compose service `h3-3060`; the RTX 4090 runs use `h3-4090`.

| `experiment.json` run ID | Run | Result | X video / evidence |
|---|---|---|---|
| `3060-tlanoai-cold` | RTX 3060, 864×480, cold run | success | local-only |
| `3060-tlanoai-warm` | RTX 3060, 864×480, warm inference | success | local-only |
| `4090-yume-recipe` | RTX 4090, 832×480, linked recipe | success | local-only |
| `4090-t2v-720p-class` | RTX 4090 T2V, 1280×704 | success | [X video](https://x.com/hAru_mAki_ch/status/2085738947553185852) |
| `4090-i2v-720p-class` | RTX 4090 I2V, 1280×704 | success | [X video](https://x.com/hAru_mAki_ch/status/2085738981866811714) |
| `3060-i2v-864x480` | RTX 3060 I2V, 864×480 | success | local-only |
| `3060-t2v-720p-class-wsl-restart` | RTX 3060 T2V, 1280×704, after WSL restart | success | [X video](https://x.com/hAru_mAki_ch/status/2085730512677855266) |
| `3060-i2v-720p-class-wsl-restart` | RTX 3060 I2V, 1280×704, after WSL restart | success | [X video](https://x.com/hAru_mAki_ch/status/2085731260169953315) |

The mapping above is the run-to-post mapping used by this record; it does not claim that the local-only runs were published.

## Runtime and key conditions

- Host: Windows 11 + WSL2 + Docker Desktop
- Container: PyTorch 2.11.0 + CUDA 13.0 + cuDNN 9
- Compose services: `h3-3060` and `h3-4090`
- Shared video shape for the 720p-class runs: 1280×704, 124 frames, 24 fps, 25 steps
- RTX 3060 reference-post condition: 864×480, 124 frames, 24 fps, 25 steps
- RTX 4090 linked-recipe condition: 832×480, 124 frames, 24 fps, 20 steps
- RTX 3060 settings: Dynamic VRAM, CPU offload, SageAttention, and EasyCache
- RTX 4090 settings: `memory_usage_factor=1.0`, pinned memory disabled, and fp16 intermediates

The RTX 3060 and RTX 4090 timings are measurements from different GPUs and conditions, not a controlled same-time speed comparison.

## Measured results

| Run | Status | Runner wall time | Output inspection |
|---|---|---:|---|
| RTX 3060 TlanoAI cold 864×480 | success | 425.526 sec | no `blackdetect` intervals; valid signal |
| RTX 3060 TlanoAI warm inference 864×480 | success | 270.289 sec | no `blackdetect` intervals; valid signal |
| RTX 4090 linked recipe 832×480 | success | 255.350 sec | no `blackdetect` intervals; valid signal |
| RTX 4090 T2V 1280×704 | success | 290.337 sec | no `blackdetect` intervals; visual inspection passed |
| RTX 4090 I2V 1280×704 | success | 275.309 sec | no `blackdetect` intervals; visual inspection passed |
| RTX 3060 I2V 864×480 | success | 375.399 sec | no `blackdetect` intervals; visual inspection passed |
| RTX 3060 T2V 1280×704 after WSL restart | success | 961.655 sec | no `blackdetect` intervals; no OOM |
| RTX 3060 I2V 1280×704 after WSL restart | success | 800.840 sec | no `blackdetect` intervals; no OOM |

## Reproduction and record links

- Primary record: [experiment.json](./experiment.json)
- Public evidence tile: [contact sheet](./previews/contact-sheet.jpg) and [manifest](./previews/contact-sheet.json)
- Detailed run log: [verification-log.en.md](../../../verification-log.en.md) / [日本語](../../../verification-log.md)
- Research notes: [research-notes.en.md](../../../research-notes.en.md) / [日本語](../../../research-notes.md)
- RTX 3060 benchmark index: [English](../../../runtime/3060/benchmark/index.md) / [日本語](../../../runtime/3060/benchmark/index.ja.md)
- RTX 4090 benchmark index: [English](../../../runtime/4090/benchmark/index.md) / [日本語](../../../runtime/4090/benchmark/index.ja.md)
- Related failed legacy route: [3060 black-output README](../3060-black-output/README.md)

The source MP4s for the runs are local runtime outputs and are not linked here as public evidence.

## Conclusion and limitations

- After switching to the correct VAE and PyTorch/CUDA conditions, the RTX 3060 completed both 1280×704 T2V and I2V.
- The RTX 4090 completed the same 1280×704-class modes in less wall time than the RTX 3060, but the GPU and conditions differ, so this is not a single speed multiplier.
- The 842×480 dimensions in the 4090 X post body and the 832×480 linked recipe differ; the 4090 result is recorded as recipe reproduction rather than an exact match to both descriptions.
- The earlier Turbo/full-int8 black-output route is kept as a separate `failed` record: [3060 legacy black-output](../3060-black-output/README.md).
