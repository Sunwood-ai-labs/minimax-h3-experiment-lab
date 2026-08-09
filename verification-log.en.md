# MiniMax-H3 verification log summary

Japanese detailed log: [verification-log.md](./verification-log.md)

This is the English navigation summary for the detailed run log. The per-run Markdown/JSON benchmark files remain generated evidence and are indexed by the bilingual [3060 benchmark index](./runtime/3060/benchmark/index.ja.md) and [4090 benchmark index](./runtime/4090/benchmark/index.ja.md).

## Host and container snapshot

- Host OS: Windows 11 Pro 64-bit, WSL2, Docker Desktop
- Host RAM: 137,270,165,504 bytes
- PowerShell: 5.1.26100.8875 Desktop
- Docker Engine: 29.4.3
- Docker Compose: v5.1.3
- NVIDIA driver: 591.86
- Container image: `local/minimax-h3-comfyui:v0.30.0`
- ComfyUI: 0.30.0
- Python: 3.12.3
- PyTorch: 2.11.0+cu130
- CUDA runtime: 13.0; cuDNN 9
- 3060 service: `h3-3060`, port 8189, Dynamic VRAM / CPU offload / SageAttention
- 4090 service: `h3-4090`, port 8188, disabled pinned memory / fp16 intermediates

## Verified run summary

| GPU | Run | Resolution | Runner wall | Result |
|---|---|---:|---:|---|
| RTX 3060 | TlanoAI cold reference | 864×480 | 425.526 sec | success; valid signal; no black interval |
| RTX 3060 | TlanoAI warm reference | 864×480 | 270.289 sec | success; valid signal; no black interval |
| RTX 4090 | linked yume recipe | 832×480 | 255.350 sec | success; valid signal; no black interval |
| RTX 4090 | T2V follow-up | 1280×704 | 290.337 sec | success; visual inspection passed |
| RTX 4090 | I2V follow-up | 1280×704 | 275.309 sec | success; visual inspection passed |
| RTX 3060 | I2V reference | 864×480 | 375.399 sec | success; visual inspection passed |
| RTX 3060 | T2V after WSL restart | 1280×704 | 961.655 sec | success; no OOM; no black interval |
| RTX 3060 | I2V after WSL restart | 1280×704 | 800.840 sec | success; no OOM; no black interval |

All records preserve start/end timestamps, ComfyUI status, workflow and model hashes, output paths and SHA-256 values, `ffprobe`, `blackdetect`, and `signalstats` where available. The source MP4s remain local-only; tracked contact sheets and manifests are the public visual evidence.

## WSL restart observation

`wsl --shutdown` reduced host RAM usage from approximately 126.22 / 127.84 GiB to 21.04 / 127.84 GiB. RTX 3060 VRAM fell from 9,745 MiB to 861 MiB, and RTX 4090 VRAM fell from 6,341 MiB to 244 MiB. After Docker Desktop recovered, the 3060-only 1280×704 T2V/I2V runs completed without OOM.

## Reproduction entry points

- Compose definition: [`compose.yaml`](./compose.yaml)
- English lab contract: [`LAB.en.md`](./LAB.en.md)
- Experiment record: [`experiments/01-baseline/gpu-baseline/README.md`](./experiments/01-baseline/gpu-baseline/README.md)
- 3060 reports: [`runtime/3060/benchmark/index.md`](./runtime/3060/benchmark/index.md)
- 4090 reports: [`runtime/4090/benchmark/index.md`](./runtime/4090/benchmark/index.md)
- Validation commands: [`scripts/validate-experiment-lab.ps1`](./scripts/validate-experiment-lab.ps1), [`scripts/validate-documentation-parity.ps1`](./scripts/validate-documentation-parity.ps1)
