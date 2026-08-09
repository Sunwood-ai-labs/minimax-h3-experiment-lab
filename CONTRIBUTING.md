# Contributing to MiniMax-H3 Experiment Lab

> 日本語版: [CONTRIBUTING.ja.md](./CONTRIBUTING.ja.md)

このラボでは、実験結果を「再実行できる記録」として追加します。成功した結果だけでなく、OOM、黒画、CUDAエラー、条件不一致も有用な証跡です。

## Add an experiment

1. Choose the existing function category under `experiments/`.
2. Copy `experiments/_template/` to a descriptive, stable slug.
3. Record the hypothesis, source URLs, fixed local conditions, GPU/runtime, workflow hash, seed, prompt, steps, dimensions, frames, wall time, output checks, and limitations.
4. Keep generated video/audio and model weights out of ordinary commits. Add a contact sheet and manifest when a visual result is useful.
5. Run the local checks:

   ```powershell
   pwsh -File .\scripts\validate-experiment-lab.ps1
   docker compose config --quiet
   ```

6. Use relative paths in committed metadata. Do not commit credentials, `.env`, model weights, or machine-specific secrets.

## Taxonomy rule

Add a new slug to an existing category whenever the experiment tests the same function. Add a new category only for a genuinely distinct function, and update all three of these in the same change:

- `experiments/experiment.schema.json`
- `scripts/validate-experiment-lab.ps1`
- `experiments/index.md`

## Pull requests

Describe the hypothesis, exact conditions, observed result, and what remains unverified. A contact sheet is preferred for visual review when attaching a video is impractical. Do not describe a result as reproducing an external post unless the conditions and limitations support that claim.
