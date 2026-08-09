# Experiment index

The repository ledger is grouped by the function being tested. The date remains in each machine-readable record, but it is not the navigation axis.

## Categories

- [01 — Baseline and GPU comparison](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/01-baseline)
- [02 — Low-step generation](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/02-low-step-generation)
- [03 — Reference-conditioned generation](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/03-reference-conditioned)
- [04 — Acceleration](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/04-acceleration)
- [05 — Temporal continuity](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/05-temporal-continuity)
- [06 — Production pipelines](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/06-production-pipelines)

## What to open first

1. [GPU baseline](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/01-baseline/gpu-baseline) — the reference T2V/I2V conditions.
2. [3060 black-output failure](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/01-baseline/3060-black-output) — the retained failure route and diagnosis.
3. [ref2va 6 vs 20 steps](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/03-reference-conditioned/ref2va-6v20) — speed/quality comparison with explicit limits.
4. [Multi-reference R2V](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s) — background plus two character references across four scenes.
5. [Cat-café Vlog](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/06-production-pipelines/catcafe-vlog-5segment) — a 30-second Japanese-dialogue pipeline.

Every experiment README links to its `previews/contact-sheet.jpg` when a visual output is available. The tile is intended for quick behavior review; the README and `experiment.json` remain the source of truth for conditions and conclusions.
