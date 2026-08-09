# MiniMax-H3 Experiment Lab — Operations Guide

> 日本語版: [LAB.md](./LAB.md)

This guide defines how to run MiniMax-H3 experiments with Docker Compose and ComfyUI while keeping GPU, resolution, LoRA, sampler, VAE, and memory differences reproducible.

## Lab principles

- Treat RTX 3060 and RTX 4090 as separate services, ports, and runtimes.
- Do not infer values that are absent from a source post. Label locally fixed values as experiment choices.
- Preserve OOM, black-output, CUDA-error, and condition-mismatch records alongside successful runs.
- Define runner wall time as API submission through ComfyUI success/error. Do not mix post-processing into inference time.
- Store the detailed conditions and limitations in the repository record, not only in an X post.

## Directory contract

```text
experiments/
  README.md                  # bilingual visual gallery
  index.md / index.en.md     # Japanese / English ledgers
  experiment.schema.json     # machine-readable metadata contract
  _template/                 # new experiment template
  <category>/<slug>/
    README.md                # English/default detailed record
    README.ja.md             # Japanese counterpart
    experiment.json          # structured conditions, runs, and evidence
    sources.md               # English source notes when needed
    sources.ja.md            # Japanese source notes when needed
    workflows/               # experiment-specific API workflows
    previews/contact-sheet.jpg
    previews/contact-sheet.json
runtime/<gpu>/
  benchmark/                 # JSON/Markdown execution reports
  input/                     # reproducibility inputs and references
  output/                    # local generated media, not tracked
social/                      # bilingual simulator indexes and payloads
```

Model weights, runtime outputs, and dependency caches stay outside ordinary Git commits. `models/manifest.json` records profile, source revision, filename, size, SHA-256, and target path; the downloader verifies the assets after download.

## Required evidence for one experiment

1. Hypothesis, comparison target, and reproducibility boundary.
2. Source URLs, source-reported values, and values fixed locally.
3. GPU, VRAM, driver, Docker image, ComfyUI, PyTorch, CUDA, and launch arguments.
4. Workflow/model/LoRA revisions or SHA-256 values, seed, prompt, resolution, frames, and steps.
5. Start/end timestamps, runner wall time, OOM/error state, and execution status.
6. `ffprobe`, `blackdetect`, `signalstats`, and visual/audio checks as appropriate.
7. Relative artifact paths, byte counts, SHA-256 values, and the local-only/public boundary.
8. A conclusion labeled as full reproduction, partial match, or unverified.

## Standard workflow

```powershell
cd <repo-root>
Copy-Item experiments/_template experiments/03-reference-conditioned/my-experiment -Recurse
# Fill README.md, README.ja.md, experiment.json, sources.md, and workflow files.
# Run the API workflow and inspect runtime/<GPU>/benchmark reports.
.\scripts\validate-experiment-lab.ps1
.\scripts\validate-documentation-parity.ps1
docker compose config --quiet
```

## Source values versus local values

Source values are explicitly stated in an X post, GitHub repository, Hugging Face page, or official documentation. Prompt, seed, scheduler, sampler, attention, EasyCache thresholds, and offload choices added for a local comparison must be labeled as local fixed values rather than claimed as an exact source reproduction.

## Public evidence and frame tiles

Generated MP4/audio files are normally `local-only`. Do not publish dead Markdown links to ignored media. Keep the path, media properties, byte count, and SHA-256 in `experiment.json`, and keep `previews/contact-sheet.jpg` plus `contact-sheet.json` tracked as the clone-safe visual evidence. Each record README must expose the X video/reference URL section in both languages.

For multiple videos, place one block per input in input order, with time increasing left-to-right and top-to-bottom. The manifest must preserve source paths, sample timestamps, dimensions, duration, and hashes.

## Classification and future experiments

Classify experiments by tested function, not by date, distributor, or person name. Reuse an existing category when possible. When adding a new function, update the schema, validator, English/Japanese ledgers, and documentation navigation in the same change.

## Documentation language policy

Public guides and experiment entry points have English and Japanese counterparts. Raw benchmark reports, generated payloads, tool-owned instruction files, and social-copy drafts are indexed evidence artifacts and are explicitly exempt from line-by-line translation. See the [documentation language policy](./docs/guide/documentation.md).
