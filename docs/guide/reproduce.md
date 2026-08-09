# Reproduce an experiment

## 1. Prepare the host

Use Windows 11 + WSL2 + Docker Desktop with NVIDIA GPU support. An RTX 3060 or RTX 4090 is supported by the Compose profiles in this repository.

```powershell
Copy-Item .env.example .env
nvidia-smi -L
```

Set `GPU_3060_UUID` and `GPU_4090_UUID` in `.env` if the defaults do not match the host.

## 2. Build and download

```powershell
docker compose --profile 4090 build h3-4090
docker compose --profile download run --rm model-downloader
```

Model weights are downloaded into `models/`, which is intentionally ignored by Git. Set `H3_PROFILE` in `.env` to `fl2va` (default), `ref2va`, `fl2va-lightx2v`, `ref2va-lightx2v`, or `legacy-turbo`. The tracked [`models/manifest.json`](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/models/manifest.json) pins each filename, upstream revision, byte count, and SHA-256; the downloader verifies all four kinds of model assets after download. Upstream model and custom-node licenses still apply.

## 3. Start one GPU service

```powershell
# RTX 4090: http://localhost:8188
docker compose --profile 4090 up -d h3-4090

# RTX 3060: http://localhost:8189
docker compose --profile 3060 up -d h3-3060
```

The two services use separate ports, GPU UUIDs, input/output mounts, and ComfyUI user state. This makes sequential GPU comparison reproducible without silently sharing runtime state.

## 4. Select an experiment record

Open an experiment README and its `experiment.json` before running. Copy the recorded workflow, seed, dimensions, frame count, step count, sampler, model revision, and attention/cache settings. Do not replace an omitted source condition with an assumption; mark the local fixed value explicitly.

The canonical reproduction kit is committed: [`compose.yaml`](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/compose.yaml), [`Dockerfile`](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/Dockerfile), [`.env.example`](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/.env.example), [`docker/download-h3-model.sh`](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/docker/download-h3-model.sh), [`models/manifest.json`](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/models/manifest.json), and the record-local API workflow JSON. The Dockerfile pins the PyTorch base image by digest and verifies the SageAttention wheel hash. The Compose services mount both `workflows/` and `experiments/` read-only so the same graph is available inside the container as well as from the host API runner.

Before starting a GPU run, verify the complete graph:

```powershell
pwsh -File .\scripts\validate-reproducibility.ps1
```

This check confirms that each record's workflow JSON, every root workflow JSON, experiment-specific helper scripts, Compose/Docker files, model manifest coverage, and tracked input graph resolve from the paths recorded in the repository. It does not claim that external model weights or a GPU-generated MP4 are already present in a fresh clone; package-index drift can also prevent bit-for-bit image reproduction even though the source refs are pinned.

## 5. Validate the lab

```powershell
pwsh -File .\scripts\validate-experiment-lab.ps1
docker compose config --quiet
```

For a new result, record ComfyUI status, API-to-success wall time, `ffprobe`, black-frame checks, signal statistics, output SHA-256, and any unverified visual or audio properties.

## Frame-tile preview

When a video is difficult to attach, generate the tracked preview tile:

```powershell
pwsh -File .\scripts\make-video-contact-sheet.ps1 `
  -InputPath .\runtime\4090\output\video\example.mp4 `
  -OutputPath .\experiments\03-reference-conditioned\my-experiment\previews\contact-sheet.jpg `
  -FrameCount 8 -Columns 4 -Overwrite
```

The companion `contact-sheet.json` records the source video path relative to the repository, source hash, dimensions, fps, duration, and sample timestamps. Frames advance left-to-right and then top-to-bottom; multiple source videos become stacked row blocks.
