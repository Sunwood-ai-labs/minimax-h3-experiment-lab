# MiniMax-H3 × Google Colab CLI — L4 Turbo LoRA 720p-aligned 5-second run

> 日本語版: [README.ja.md](./README.ja.md)

- ID: `2026-08-10-colab-cli-l4-turbo-720p-5s`
- Status: `verified`
- GPU: NVIDIA L4 via Google Colab CLI 0.6.0
- Host path: Windows PowerShell → WSL2 Ubuntu → Colab runtime

Record: [`experiment.json`](./experiment.json) · [tracked frame](./previews/contact-sheet.jpg) · [manifest](./previews/contact-sheet.json)

![MiniMax-H3 L4 output first frame](./previews/contact-sheet.jpg)

## X video and reference URLs

- Generated video post: `simulation_only / not posted`
- Video attachment: local-only MP4; kept outside the repository and attached to X separately.
- Source/reference URLs: [Google Colab CLI](https://github.com/googlecolab/google-colab-cli) · [ComfyUI](https://github.com/Comfy-Org/ComfyUI) · [MiniMax-H3 Turbo node](https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo) · [MiniMax-H3 models](https://huggingface.co/Comfy-Org/MiniMax-H3) · [legacy Turbo LoRA](https://huggingface.co/larryvrh/MiniMax-H3-Turbo-Lora)
- Workflow/run mapping: [`minimax_h3_turbo_l4_1280x704_api.json`](./workflows/minimax_h3_turbo_l4_1280x704_api.json) → `l4-colab-2026-08-10` → local Colab output and tracked exact-5-second derivative.

## What was verified

The Windows → WSL2 Ubuntu → Google Colab CLI path successfully ran MiniMax-H3 legacy Turbo LoRA v4 on an NVIDIA L4. The Turbo node was detected, LoRA was applied to 259 backbone modules, and the run completed at 8 steps.

The X attachment is `1280×704`, `24 fps`, `120 frames`, exactly `5.000 seconds`, and remains local-only. H3の標準生成は`124 frames`で`5.166667 seconds`になるため、Colabで生成した原本をローカルのffmpeg runnerで120 framesへ整形している。

## Conditions

| Item | Value |
|---|---|
| GPU | NVIDIA L4 / about 22.56 GiB VRAM |
| ComfyUI | `v0.30.0` |
| PyTorch | `2.11.0+cu128` |
| Base | `minimax_h3_fl2va_int8_convrot.safetensors` |
| Text encoder | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| VAE | Official FP16 video VAE + FP32 audio VAE |
| Turbo LoRA | `minimax_h3_turbo_4step_ema_ckpt850.safetensors` |
| LoRA strength | `1.0` |
| Resolution | `1280×704` |
| Generation frames | `124` at `24 fps` |
| Steps | `8` / `simple` scheduler |
| Seed | `2026081001` |
| Runtime flags | `--disable-dynamic-vram --novram --disable-async-offload` |

## Reproduction kit

The repository now contains the complete runner set used for this path:

- Windows/WSL2 orchestrator: [`run-colab-l4-turbo-720p.ps1`](./run-colab-l4-turbo-720p.ps1)
- Colab setup and pinned model verification: [`scripts/colab_h3_setup.py`](./scripts/colab_h3_setup.py)
- Stable ComfyUI startup flags: [`scripts/colab_h3_start.py`](./scripts/colab_h3_start.py)
- ComfyUI API submit/poll/output report: [`scripts/colab_h3_run.py`](./scripts/colab_h3_run.py)
- Exact 5-second local post-process and ffprobe validation: [`scripts/trim-exact-5s.ps1`](./scripts/trim-exact-5s.ps1)
- Colab runtime pins: [`colab_runtime.json`](./colab_runtime.json)
- API workflow: [`workflows/minimax_h3_turbo_l4_1280x704_api.json`](./workflows/minimax_h3_turbo_l4_1280x704_api.json)
- Model names, revisions, sizes, and hashes: [`../../../models/manifest.json`](../../../models/manifest.json)
- H3 VAE runtime patch: [`../../../docker/h3-runtime-patch.py`](../../../docker/h3-runtime-patch.py)

From a fresh Windows checkout with WSL2 Ubuntu and an authenticated Colab CLI:

```powershell
powershell -ExecutionPolicy Bypass -File .\experiments\02-low-step-generation\colab-cli-l4-turbo-720p-5s\run-colab-l4-turbo-720p.ps1
```

The first run downloads about `56.3 GB` (`52.45 GiB`) of model files and installs the pinned runtime. To reuse an already-running session without repeating setup:

```powershell
powershell -ExecutionPolicy Bypass -File .\experiments\02-low-step-generation\colab-cli-l4-turbo-720p-5s\run-colab-l4-turbo-720p.ps1 -SkipSetup -KeepSession
```

`-KeepSession` is useful for debugging; the default behavior stops a session created by the runner after the output is downloaded. Google Drive model caching is the next optimization and is intentionally not represented as completed here.

The wrapper defaults to `-Gpu L4`; the CLI-supported alternatives are `T4`, `G4`, `H100`, and `A100`.

The default `-OutputPath` is outside the repository under the user's Videos folder (`Videos\minimax-h3-colab\...mp4`), so generated MP4s are not accidentally added to Git. You can pass another external path explicitly.

If `ffmpeg.exe` and `ffprobe.exe` are not on `PATH`, pass their directory explicitly with `-FfmpegBinDir 'C:\path\to\ffmpeg\bin'`.

## Results

| Run | Status | Generation wall | Session wall | Output |
|---|---|---:|---:|---|
| `l4-colab-2026-08-10` | success | `1315.539 s` | `2232 s` | local-only 5.00-second X attachment |

- Generation CU estimate: about `0.62 CU`
- Whole-session CU estimate: about `1.06 CU`
- Original Colab MP4: `1280×704`, `124 frames`, `5.166667 s`, SHA-256 `8C64503640EB4022C53468718EA7FA5E4E793780B8D217B9994A8D9357111E9F`
- Local-only exact output attached to X: `1280×704`, `120 frames`, `5.000000 s`, SHA-256 `35BA074D0008B03852A6B3D371ED04570148273DC53033ECF16E3A635D48EE01`
- `blackdetect` events: `0`; video/audio decode diagnostics were finite.

The CU values are wall-time estimates using a public L4 rate assumption. The actual Colab UI value is authoritative.

## Provenance and limitations

The successful run was completed before this experiment folder was packaged. The tracked scripts are a post-run reproducibility packaging of the same setup, startup flags, API graph, and exact-duration trim path; they are not a byte-for-byte claim about the temporary files used in the original session. The generated MP4 is intentionally kept outside Git because it is the X attachment, not repository evidence.

- Colab CLI is used through WSL2; Windows-native execution is not claimed.
- The v5 experimental artifact was not used because its encrypted container stops at the current Turbo loader. The successful run uses the hash-pinned legacy v4 LoRA.
- An attempted `SelectVAEDevice=cpu` value was rejected by the node as unsupported; the tracked workflow uses the supported `default` value.
- A fresh session currently redownloads the model set; Drive cache support remains a next improvement.

## Checks

```powershell
pwsh -File .\scripts\validate-experiment-lab.ps1
pwsh -File .\scripts\validate-reproducibility.ps1
```
