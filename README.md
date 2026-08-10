<div align="center">
  <img src="https://raw.githubusercontent.com/Sunwood-ai-labs/minimax-h3-experiment-lab/main/docs/public/icon.svg" alt="MiniMax-H3 Experiment Lab" width="112">
  <h1>MiniMax-H3 Experiment Lab</h1>
  <p>Reproducible Docker Compose + ComfyUI experiments for MiniMax-H3 video generation.</p>
</div>

<p align="center">
  <a href="https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/actions/workflows/ci.yml"><img src="https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-5b8def.svg" alt="MIT License"></a>
  <a href="https://sunwood-ai-labs.github.io/minimax-h3-experiment-lab/"><img src="https://img.shields.io/badge/docs-GitHub%20Pages-6f42c1.svg" alt="Documentation"></a>
</p>

<p align="center"><a href="./README.ja.md">日本語版 / Japanese README</a></p>

This repository is a growing experiment lab rather than a model mirror. It keeps the Docker/ComfyUI runtime, reproducible workflows, GPU-specific measurements, prompts, provenance, failure evidence, and shareable frame-tile previews in one place.

## 🧭 Start here

- [Browse the visual experiment gallery](./experiments/README.md)
- [Open the Google Colab CLI L4 reproduction record](./experiments/02-low-step-generation/colab-cli-l4-turbo-720p-5s/README.md)
- [See the tile previews on this page](#🖼️-experiment-tile-previews)
- [Open the English machine-readable experiment ledger](./experiments/index.en.md)
- [Read the English reproducibility contract](./LAB.en.md)
- [Open the documentation site](https://sunwood-ai-labs.github.io/minimax-h3-experiment-lab/)
- [Review X publishing payloads and simulators](./social/README.md)
- [Inspect the frame-tile rules](./LAB.en.md#public-evidence-and-frame-tiles)

## 🖼️ Experiment tile previews

These tracked contact sheets are the fastest way to compare temporal behavior from a fresh clone. Click a tile to open the full experiment record; each card also links to the corresponding video thread or source post on X. Generated MP4s are local-only; the public visual evidence is the tracked tile and manifest.

<table>
  <tr>
    <td width="50%" valign="top"><a href="./experiments/01-baseline/gpu-baseline/README.md"><img src="./experiments/01-baseline/gpu-baseline/previews/contact-sheet.jpg" alt="GPU baseline contact sheet" width="480"></a><br><strong>GPU baseline</strong><br>RTX 3060 / 4090 · T2V + I2V<br><a href="./experiments/01-baseline/gpu-baseline/README.md">Record</a> · <a href="https://x.com/hAru_mAki_ch/status/2085730512677855266">3060 T2V</a> · <a href="https://x.com/hAru_mAki_ch/status/2085731260169953315">3060 I2V</a> · <a href="https://x.com/hAru_mAki_ch/status/2085738947553185852">4090 T2V</a> · <a href="https://x.com/hAru_mAki_ch/status/2085738981866811714">4090 I2V</a></td>
    <td width="50%" valign="top"><a href="./experiments/01-baseline/3060-black-output/README.md"><img src="./experiments/01-baseline/3060-black-output/previews/contact-sheet.jpg" alt="3060 black-output contact sheet" width="480"></a><br><strong>3060 black-output failure</strong><br>Retained failure evidence · not a success baseline<br><a href="./experiments/01-baseline/3060-black-output/README.md">Record</a> · <a href="https://x.com/TlanoAI/status/2084940455809286397">source video post</a></td>
  </tr>
  <tr>
    <td valign="top"><a href="./experiments/02-low-step-generation/colab-cli-l4-turbo-720p-5s/README.md"><img src="./experiments/02-low-step-generation/colab-cli-l4-turbo-720p-5s/previews/contact-sheet.jpg" alt="Google Colab CLI L4 Turbo contact sheet" width="480"></a><br><strong>Google Colab CLI L4 Turbo</strong><br>Windows → WSL2 → Colab · 1280×704 · exact 5 seconds<br><a href="./experiments/02-low-step-generation/colab-cli-l4-turbo-720p-5s/README.md">Record</a> · <a href="https://github.com/googlecolab/google-colab-cli">Colab CLI source</a></td>
  </tr>
  <tr>
    <td valign="top"><a href="./experiments/02-low-step-generation/lightx2v-4step/README.md"><img src="./experiments/02-low-step-generation/lightx2v-4step/previews/contact-sheet.jpg" alt="LightX2V low-step contact sheet" width="480"></a><br><strong>LightX2V 4-step</strong><br>T2V / I2V · `er_sde` / `sa_solver`<br><a href="./experiments/02-low-step-generation/lightx2v-4step/README.md">Record</a> · <a href="https://x.com/hAru_mAki_ch/status/2085926432086307010">X thread (attachment uncertain)</a> · <a href="https://x.com/sd_tutorial/status/2085760369612783646">source post</a></td>
    <td valign="top"><a href="./experiments/03-reference-conditioned/i2v-scenes/README.md"><img src="./experiments/03-reference-conditioned/i2v-scenes/previews/contact-sheet.jpg" alt="ImageGen-started I2V contact sheet" width="480"></a><br><strong>ImageGen-started I2V</strong><br>Car · sports · illustration · battle<br><a href="./experiments/03-reference-conditioned/i2v-scenes/README.md">Record</a> · <a href="https://x.com/sd_tutorial/status/2085760369612783646">source video post</a></td>
  </tr>
  <tr>
    <td valign="top"><a href="./experiments/03-reference-conditioned/ref2va-6v20/README.md"><img src="./experiments/03-reference-conditioned/ref2va-6v20/previews/contact-sheet.jpg" alt="ref2va steps comparison contact sheet" width="480"></a><br><strong>ref2va 6 vs 20 steps</strong><br>T2V / I2V · LoRA 0.8<br><a href="./experiments/03-reference-conditioned/ref2va-6v20/README.md">Record</a> · <a href="https://x.com/hAru_mAki_ch/status/2085955887575990468">X thread (attachment uncertain)</a> · <a href="https://x.com/sd_tutorial/status/2085760369612783646">source post</a></td>
    <td valign="top"><a href="./experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s/README.md"><img src="./experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s/previews/contact-sheet.jpg" alt="multi-reference R2V contact sheet" width="480"></a><br><strong>Multi-reference R2V</strong><br>Background + two characters · four scenes<br><a href="./experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s/README.md">Record</a> · <a href="https://x.com/hAru_mAki_ch/status/2086019982308352292">X thread (attachment uncertain)</a> · <a href="https://x.com/sd_tutorial/status/2085760369612783646">source post</a></td>
  </tr>
  <tr>
    <td valign="top"><a href="./experiments/04-acceleration/sol-sage-easycache-4scenes-7s/README.md"><img src="./experiments/04-acceleration/sol-sage-easycache-4scenes-7s/previews/contact-sheet.jpg" alt="attention and cache acceleration contact sheet" width="480"></a><br><strong>Attention / cache acceleration</strong><br>Sol-Attn + SageAttention + EasyCache<br><a href="./experiments/04-acceleration/sol-sage-easycache-4scenes-7s/README.md">Record</a> · <a href="https://x.com/hAru_mAki_ch/status/2086051398735847471">X thread (attachment uncertain)</a> · <a href="https://x.com/sunbaolong_2001/status/2085689404031672372">source post</a></td>
    <td valign="top"><a href="./experiments/05-temporal-continuity/motion-context-3segment/README.md"><img src="./experiments/05-temporal-continuity/motion-context-3segment/previews/contact-sheet.jpg" alt="Motion Context contact sheet" width="480"></a><br><strong>Motion Context</strong><br>Video + audio latent continuity<br><a href="./experiments/05-temporal-continuity/motion-context-3segment/README.md">Record</a> · <a href="https://x.com/hAru_mAki_ch/status/2086223412129902756">X thread (attachment uncertain)</a> · <a href="https://x.com/photogenicweeke/status/2085848283138891926">source post</a></td>
  </tr>
  <tr>
    <td valign="top"><a href="./experiments/06-production-pipelines/catcafe-vlog-5segment/README.md"><img src="./experiments/06-production-pipelines/catcafe-vlog-5segment/previews/contact-sheet.jpg" alt="Japanese cat cafe vlog contact sheet" width="480"></a><br><strong>Japanese cat-café Vlog</strong><br>Five segments · Japanese dialogue · about 30 seconds<br><a href="./experiments/06-production-pipelines/catcafe-vlog-5segment/README.md">Record</a> · <a href="https://x.com/hAru_mAki_ch/status/2086296391702438041">X URL (attachment uncertain)</a></td>
    <td valign="top"><a href="./experiments/06-production-pipelines/jpop-mv-5segment/README.md"><img src="./experiments/06-production-pipelines/jpop-mv-5segment/previews/contact-sheet.jpg" alt="Japanese synth-pop MV contact sheet" width="480"></a><br><strong>Japanese synth-pop MV</strong><br>Generated audio · beat analysis · lyric motion<br><a href="./experiments/06-production-pipelines/jpop-mv-5segment/README.md">Record</a> · <a href="https://x.com/hAru_mAki_ch/status/2086334052639142176">X URL (attachment uncertain)</a></td>
  </tr>
</table>

For the same list in a compact ledger, see [the English experiment index](./experiments/index.en.md) and [the video-link index](./experiments/video-links.md).

## 🚀 Quick start

Requirements: Windows 11 + WSL2 + Docker Desktop, an NVIDIA driver with Docker GPU support, and an RTX 3060 or RTX 4090. The model download is external to Git and is roughly 42.5 GB for the default `fl2va` / `ref2va` profile.

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

The downloader profile is selected in `.env`: `fl2va` (default), `ref2va`, `fl2va-lightx2v`, `ref2va-lightx2v`, or `legacy-turbo`. See [`models/README.md`](./models/README.md) and the pinned [`models/manifest.json`](./models/manifest.json) before choosing a larger profile.

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
| Google Colab CLI | Windows → WSL2 → Colab CLI 0.6.0, NVIDIA L4, legacy Turbo LoRA v4, 1280×704, exact 5-second output |

The gallery exposes machine-readable experiment records. Each record exposes its README, JSON, tracked contact sheet, and contact-sheet manifest. The failed black-output route remains documented so later experiments do not mistake it for a successful baseline.

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

## 🧰 Reproduction kit

The files needed to rebuild the runtime are committed and linked from the records:

| Layer | Canonical file | Role |
|---|---|---|
| Compose | [`compose.yaml`](./compose.yaml) | Separate RTX 3060 / RTX 4090 services and the model-download profile |
| Image build | [`Dockerfile`](./Dockerfile) | Pinned PyTorch base digest, ComfyUI/custom-node refs, and SageAttention wheel hash |
| Host config | [`.env.example`](./.env.example) | GPU UUIDs, model profile, upstream revisions, and pinned build refs |
| Model setup | [`docker/download-h3-model.sh`](./docker/download-h3-model.sh) | Profile-aware external model download with size and SHA-256 checks |
| Model lock | [`models/manifest.json`](./models/manifest.json) and [`models/README.md`](./models/README.md) | Exact model filenames, source revisions, target paths, bytes, and hashes |
| Workflows | [`workflows/`](./workflows/) and each record's `workflows/` | API-format ComfyUI graphs with recorded hashes |
| Google Colab CLI | [`run-colab-l4-turbo-720p.ps1`](./experiments/02-low-step-generation/colab-cli-l4-turbo-720p-5s/run-colab-l4-turbo-720p.ps1) | Windows → WSL2 → Colab session orchestration, setup, API run, download, and local 5-second validation |
| Validation | [`scripts/validate-reproducibility.ps1`](./scripts/validate-reproducibility.ps1) | Confirms the Compose/Docker/workflow/input graph before a run |

The model weights and generated videos are intentionally external/local-only. The Colab L4 record keeps the X attachment outside Git and stores only the contact sheet, manifest, workflow, runner, and measured metadata. A fresh clone can reproduce the Docker or Colab build inputs, runtime, model inventory, and workflow graph after downloading the upstream model files; it still needs a GPU run to regenerate the video. Python/apt dependencies follow the pinned upstream source files and package indexes at build time, so bit-for-bit output identity is not claimed.

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
- [English experiment ledger](./experiments/index.en.md)
- [English lab operations guide](./LAB.en.md)
- [Research notes](./research-notes.en.md)
- [Verification log](./verification-log.en.md)
- [English X payload and simulator index](./social/README.md)
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
