# MiniMax-H3 Experiment: <short name>

> 日本語版: [README.ja.md](./README.ja.md)

- ID: `<YYYY-MM-DD-slug>`
- Category: `<01-baseline|02-low-step-generation|03-reference-conditioned|04-acceleration|05-temporal-continuity|06-production-pipelines|07-upscaling>`
- Status: `planned`
- GPU: `<RTX ...>`
- Owner: `MiniMax-H3 Experiment Lab`

The same-directory `experiment.json` is the machine-readable canonical record. Do not infer values missing from a source; separate source-reported values from locally fixed test values.

Record: [`experiment.json`](./experiment.json) · [tracked tile](./previews/contact-sheet.jpg) · [manifest](./previews/contact-sheet.json) · [Japanese README](./README.ja.md)

## X video and reference URLs

- Generated video post: `<https://x.com/...>` or `Not published / local-only`
- Source/reference URLs: list every X, GitHub, Hugging Face, and official documentation URL used for this experiment.
- Workflow/run mapping: link each workflow JSON to the generated post URL, or explicitly write `local-only` / `not posted`.

## Hypothesis

What is being tested and what is the comparison target?

## Sources

Link the same-directory `sources.md` and `sources.ja.md` when source notes are needed. State what the source specifies and what it does not specify.

## Conditions

- Docker Compose service:
- Docker image / digest:
- ComfyUI / Python / PyTorch / CUDA:
- GPU / VRAM / driver:
- Base model / text encoder / VAE:
- LoRA / strength:
- Resolution / frames / fps:
- Steps / sampler / scheduler:
- EasyCache / attention / offload:
- Seed / prompt:

## Reproduction kit

- Compose: [`compose.yaml`](../../../compose.yaml)
- Image build: [`Dockerfile`](../../../Dockerfile)
- Host config: [`.env.example`](../../../.env.example)
- Model setup: [`docker/download-h3-model.sh`](../../../docker/download-h3-model.sh)
- Model lock: [`models/manifest.json`](../../../models/manifest.json)
- Workflow JSON: `./workflows/` or a shared file under [`workflows/`](../../../workflows/)

## Results

| Run | Status | Start | End | Runner wall | OOM | blackdetect |
|---|---|---|---|---:|---|---:|
| 1 | pending | | | | | |

Record relative paths, bytes, SHA-256, `ffprobe`, black-frame/audio checks, and visual limitations. Keep generated MP4/audio links explicitly `local-only` when they are not tracked.

## Conclusion and limitations

- Conclusion:
- Reproduction boundary:
- Unverified:

## Checks after adding the record

```powershell
.\scripts\validate-experiment-lab.ps1
.\scripts\validate-documentation-parity.ps1
.\scripts\validate-reproducibility.ps1
```
