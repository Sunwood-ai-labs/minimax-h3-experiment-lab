<div align="center">
  <img src="https://raw.githubusercontent.com/Sunwood-ai-labs/minimax-h3-experiment-lab/master/docs/public/icon.svg" alt="MiniMax-H3 Experiment Lab" width="112">
  <h1>MiniMax-H3 Experiment Lab</h1>
  <p>Reproducible Docker Compose + ComfyUI experiments for MiniMax-H3 video generation.</p>
</div>

<p align="center">
  <a href="https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/actions/workflows/ci.yml"><img src="https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-5b8def.svg" alt="MIT License"></a>
  <a href="https://sunwood-ai-labs.github.io/minimax-h3-experiment-lab/"><img src="https://img.shields.io/badge/docs-GitHub%20Pages-6f42c1.svg" alt="Documentation"></a>
</p>

<p align="center"><a href="./README.ja.md">日本語版 / Japanese README</a></p>

This repository is a growing experiment lab rather than a model mirror. It keeps the Docker/ComfyUI runtime, reproducible workflows, GPU-specific measurements, prompts, provenance, failure evidence, and shareable frame-tile previews in one place.

## 🧭 Start here

- [Browse the visual experiment gallery](./experiments/README.md)
- [Open the machine-readable experiment ledger](./experiments/index.md)
- [Read the reproducibility contract](./LAB.md)
- [Open the documentation site](https://sunwood-ai-labs.github.io/minimax-h3-experiment-lab/)
- [Review X publishing payloads and simulators](./social/README.md)
- [Inspect the frame-tile rules](./LAB.md#フレームタイルプレビュー)

## 🚀 Quick start

Requirements: Windows 11 + WSL2 + Docker Desktop, an NVIDIA driver with Docker GPU support, and an RTX 3060 or RTX 4090. The model download is external to Git and is roughly 42.5 GB for the tested variant.

```powershell
git clone https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab.git
cd minimax-h3-experiment-lab
Copy-Item .env.example .env
nvidia-smi -L
# Set GPU_3060_UUID and GPU_4090_UUID in .env when the defaults do not match.

docker compose --profile 4090 build h3-4090
docker compose --profile download run --rm model-downloader
docker compose --profile 4090 up -d h3-4090
```

- RTX 4090: <http://localhost:8188>
- RTX 3060: <http://localhost:8189>
- Both services: `docker compose --profile 3060 --profile 4090 up -d`

The Compose file pins GPU services separately, mounts models read-only, and separates runtime state under `runtime/3060` and `runtime/4090`.

## 🧪 What is already measured

| Area | Current evidence |
|---|---|
| Baseline | RTX 3060 and RTX 4090 T2V/I2V runs, including the retained 3060 black-output failure route |
| Low-step generation | 4-step T2V/I2V with LightX2V-style LoRA and `er_sde` / `sa_solver` |
| Reference conditioning | ImageGen-started I2V, ref2va 6-vs-20-step comparison, and 3-reference R2V scenes |
| Acceleration | Sol-Attn + generic FP16 CUDA SageAttention + EasyCache under the same R2V conditions |
| Temporal continuity | Motion Context with video/audio latent context carried across segments |
| Production pipelines | Japanese cat-café Vlog and Japanese synth-pop MV with lyric motion |

The gallery currently contains ten machine-readable experiment records. Each record exposes its README, JSON, tracked contact sheet, and contact-sheet manifest. The failed black-output route remains documented so later experiments do not mistake it for a successful baseline.

## 🗂️ Experiment structure

Experiments are organized by function, not by date, distributor, or person name:

```text
experiments/<category>/<slug>/
  README.md
  experiment.json
  sources.md                 # when external sources need a separate summary
  workflows/                 # experiment-specific API workflows
  previews/
    contact-sheet.jpg        # shareable frame-tile preview
    contact-sheet.json       # source paths, sample times, hashes, dimensions
```

The six current categories are [baseline](./experiments/01-baseline/), [low-step generation](./experiments/02-low-step-generation/), [reference conditioning](./experiments/03-reference-conditioned/), [acceleration](./experiments/04-acceleration/), [temporal continuity](./experiments/05-temporal-continuity/), and [production pipelines](./experiments/06-production-pipelines/). Add a new slug to an existing category whenever possible; introduce a new category only when the function is genuinely distinct and update the schema, validator, and ledger together.

## 🖼️ Frame-tile previews

Videos are useful locally but awkward to attach to documentation and X threads. Each completed experiment therefore keeps a compact contact sheet. Frames progress left-to-right and then top-to-bottom; multiple input videos are stacked as separate row blocks. The companion manifest records the exact source video, SHA-256, dimensions, frame rate, duration, and sample timestamps. The source MP4 may be local-only; the tile is the tracked public visual evidence.

```powershell
pwsh -File .\scripts\make-video-contact-sheet.ps1 `
  -InputPath .\runtime\4090\output\video\example.mp4 `
  -OutputPath .\experiments\03-reference-conditioned\my-experiment\previews\contact-sheet.jpg `
  -FrameCount 8 -Columns 4 -Overwrite
```

The generated tile is tracked; large runtime outputs and model weights are not.

## 🔁 Reproduce and validate

Start from the experiment README and `experiment.json`, then use the recorded workflow, seed, model revision, resolution, frame count, sampler, and runtime conditions.

```powershell
pwsh -File .\scripts\validate-experiment-lab.ps1
docker compose config --quiet
```

The stronger verified records record wall time, ComfyUI status, workflow/model hashes, `ffprobe` output, black-frame checks, signal statistics, output hashes, and limitations. Older baseline/failure records identify any missing replay evidence explicitly. `blackdetect=0` is not treated as a sufficient visual-quality claim by itself.

## 📚 Documentation and related files

- [Documentation site](https://sunwood-ai-labs.github.io/minimax-h3-experiment-lab/)
- [Public artifact and media boundary](./docs/guide/artifacts.md)
- [Experiment ledger](./experiments/index.md)
- [Lab operations guide](./LAB.md)
- [Research notes](./research-notes.md)
- [Verification log](./verification-log.md)
- [X payload and simulator index](./social/README.md)
- [Docker Compose definition](./compose.yaml)

## ⚖️ Scope and licensing

This repository contains runtime code, workflows, experiment metadata, documentation, and selected preview assets. Model weights are intentionally not included. MiniMax-H3, ComfyUI, custom nodes, LoRAs, and downloaded assets remain subject to their respective upstream licenses and terms; check those terms before redistribution or commercial use.

The repository-authored code, documentation, and experiment records are released under the [MIT License](./LICENSE). See [CONTRIBUTING.md](./CONTRIBUTING.md) before adding a new experiment.

## 🔗 Primary references

- [MiniMax-H3 model card](https://huggingface.co/MiniMaxAI/MiniMax-H3)
- [MiniMax-H3 source repository](https://github.com/MiniMax-AI/MiniMax-H3)
- [ComfyUI MiniMax-H3 guide](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)
- [MiniMax-H3 ComfyUI files](https://huggingface.co/Kijai/MiniMax-H3_comfy)
- [H3 Motion Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context)
