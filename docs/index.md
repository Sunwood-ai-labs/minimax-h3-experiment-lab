---
layout: home

hero:
  name: MiniMax-H3 Experiment Lab
  text: Reproducible video-generation experiments
  tagline: Docker Compose, ComfyUI, GPU comparisons, reference conditioning, temporal continuity, and production pipelines.
  image:
    src: /icon.svg
    alt: MiniMax-H3 Experiment Lab
  actions:
    - theme: brand
      text: Reproduce an experiment
      link: /guide/reproduce
    - theme: alt
      text: Browse the experiment index
      link: /guide/experiments

features:
  - icon: 🧪
    title: Evidence-first records
    details: Prompts, seeds, workflow hashes, wall time, output checks, and limitations stay with each experiment.
  - icon: 🐳
    title: Docker Compose runtime
    details: RTX 3060 and RTX 4090 services are separated by profile, port, GPU UUID, and runtime directory.
  - icon: 🖼️
    title: Shareable frame tiles
    details: Contact sheets make temporal behavior legible in a README or X thread without attaching a full video.
---

## Current scope

The lab currently covers baseline GPU comparisons, 4-step generation, ref2va and multi-reference R2V, attention/cache acceleration, Motion Context, and Japanese Vlog/MV production experiments.

The repository is organized by function rather than by date, distributor, or person name. Start with the [visual experiment gallery](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/README.md) to scan the tracked tiles, then use the [experiment ledger](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/index.md) as the canonical machine-readable index.

- [Visual gallery with frame tiles](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/README.md)
- [Full experiment ledger](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/index.md)
- [X simulator and payload index](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/social/README.md)

## Language

- [日本語ドキュメント](/ja/)
- [English README](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/README.md)
- [日本語README](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/README.ja.md)
