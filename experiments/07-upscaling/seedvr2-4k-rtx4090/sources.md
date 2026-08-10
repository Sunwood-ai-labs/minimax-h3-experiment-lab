# Sources

Japanese notes: [sources.ja.md](./sources.ja.md)

| Source | What it supports | Checked at |
|---|---|---|
| [Comfy-Org/SeedVR2](https://huggingface.co/Comfy-Org/SeedVR2) | Official SeedVR2 distribution page and model source used for the local diffusion model and VAE | 2026-08-10 09:03 JST |
| [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) | H3 model-family context for the existing input video; H3 generation was not rerun in this experiment | 2026-08-10 09:03 JST |
| [aihonobono2023 reference post](https://x.com/aihonobono2023/status/2086281213334213104?s=46) | User-provided reference for the continuation/upscale follow-up; exact internal workflow and settings are not asserted | 2026-08-10 09:03 JST |
| Local input: `runtime/4090/input/seedvr2_experiment_h3_battle_1344x768.mp4` | H3-generated 1344×768 / 24 fps / 158-frame input used as the fixed source | 2026-08-10 00:00–00:06 JST |
| [published experiment thread](https://x.com/hAru_mAki_ch/status/2086601484901495018) | Public post for the generated-video continuation | 2026-08-10 |
| [experiment evidence reply](https://x.com/hAru_mAki_ch/status/2086601566224814552) | Public evidence reply associated with the experiment | 2026-08-10 |
| [reference URL reply](https://x.com/hAru_mAki_ch/status/2086601653873168501) | Public thread reply carrying the source-post URL | 2026-08-10 |
| [continuity note](https://x.com/hAru_mAki_ch/status/2086601745233510417) | Public thread reply describing the continuation context | 2026-08-10 |

The reference post is motivation, not a hidden-condition source. Values such as the RTX 4090 memory peak, wall time, output hash, segment durations and audio offset come from the local run logs in [`runs/`](./runs/) and the verification commands recorded in [`experiment.json`](./experiment.json).
