# Experiment record contract

Each experiment lives at `experiments/<category>/<slug>/` and should remain understandable without the original conversation.

## Required evidence

For a `verified` record, the following evidence should be present. Historical failure records may be incomplete; they must say so explicitly instead of implying that a fresh clone can replay the failure.

- hypothesis, purpose, scope, and conclusion
- source URLs and a distinction between source-reported values and local fixed values
- GPU, VRAM, driver, Docker image, ComfyUI, PyTorch, CUDA, and launch arguments
- workflow/model/LoRA revisions or SHA-256 values
- prompt, negative prompt when used, seed, sampler, scheduler, VAE, attention/cache settings
- dimensions, frames, fps, steps, execution start/end, and API-to-success wall time
- `ffprobe`, black-frame/signal checks, visual or audio inspection, and limitations
- output relative paths, byte sizes, and SHA-256 values

Path rule: workflow files, reference inputs, and experiment-local artifacts are resolved from the experiment directory. `runtime/...` paths and contact-sheet manifest source paths are repository-root-relative. A path beginning with `../` is still resolved from the record directory; `<repo-root>` is a human-readable captured-host placeholder, not a command to paste unchanged.

## Status

| Status | Meaning |
|---|---|
| `planned` | Conditions and purpose are defined but the run has not started. |
| `running` | The run or result organization is in progress. |
| `verified` | Execution, output checks, and condition recording are complete. |
| `partial` | Only part of the intended conditions was tested. |
| `failed` | A failure route was reproduced and documented. |

## Extending the taxonomy

Use an existing category for a new variation of the same function. If a new function needs its own category, update the JSON schema, PowerShell validator, and experiment ledger together. This keeps the lab searchable as experiments accumulate.

## Large artifacts

Model weights, runtime output videos, dependency caches, and temporary logs stay outside ordinary Git tracking. Use contact sheets, posters, hashes, benchmark JSON, and Markdown explanations as the durable public evidence.

The public boundary is explicit: a fresh clone must be able to open the README, `experiment.json`, tracked frame tile, and tile manifest. A generated MP4 may remain `local-only`; keep its source path, media properties, byte count, and SHA-256 in the record, but do not publish a dead Markdown link to an ignored file.
