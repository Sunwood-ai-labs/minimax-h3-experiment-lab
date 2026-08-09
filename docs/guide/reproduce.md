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

Model weights are downloaded into `models/`, which is intentionally ignored by Git. Upstream model and custom-node licenses still apply.

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
