# MiniMax-H3 × Google Colab CLI — L4 Turbo LoRA 720p相当・5秒動画

> English: [README.md](./README.md)

- ID: `2026-08-10-colab-cli-l4-turbo-720p-5s`
- Status: `verified`
- GPU: Google Colab CLI 0.6.0経由のNVIDIA L4
- 実行経路: Windows PowerShell → WSL2 Ubuntu → Colab runtime

記録: [`experiment.json`](./experiment.json) · [追跡フレーム](./previews/contact-sheet.jpg) · [manifest](./previews/contact-sheet.json)

![MiniMax-H3 L4出力の先頭フレーム](./previews/contact-sheet.jpg)

## X動画・参照URL

- 生成動画の投稿: `simulation_only / not posted`
- 動画添付: local-only MP4。リポジトリ外に置き、Xへ別途添付する。
- 出典: [Google Colab CLI](https://github.com/googlecolab/google-colab-cli) · [ComfyUI](https://github.com/Comfy-Org/ComfyUI) · [MiniMax-H3 Turbo node](https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo) · [MiniMax-H3 models](https://huggingface.co/Comfy-Org/MiniMax-H3) · [legacy Turbo LoRA](https://huggingface.co/larryvrh/MiniMax-H3-Turbo-Lora)
- workflow/run対応: [`minimax_h3_turbo_l4_1280x704_api.json`](./workflows/minimax_h3_turbo_l4_1280x704_api.json) → `l4-colab-2026-08-10` → Colab原本と5.00秒整形版。

## 検証できたこと

WindowsからWSL2 Ubuntu上のGoogle Colab CLIを呼び出し、ColabのNVIDIA L4でMiniMax-H3のlegacy Turbo LoRA v4を実行した。Turbo nodeは検出され、259個のbackbone moduleへLoRAが適用された状態で8 stepsを完走した。

X添付用の成果物は`1280×704`、`24 fps`、`120 frames`、正確に`5.000秒`で、MP4はlocal-onlyとする。H3の標準生成は`124 frames`で`5.166667秒`になるため、Colab生成原本をローカルのffmpeg runnerで120 framesへ整形している。

## 条件

| 項目 | 値 |
|---|---|
| GPU | NVIDIA L4 / 約22.56 GiB VRAM |
| ComfyUI | `v0.30.0` |
| PyTorch | `2.11.0+cu128` |
| Base | `minimax_h3_fl2va_int8_convrot.safetensors` |
| Text encoder | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| VAE | 公式FP16 video VAE + FP32 audio VAE |
| Turbo LoRA | `minimax_h3_turbo_4step_ema_ckpt850.safetensors` |
| LoRA strength | `1.0` |
| 解像度 | `1280×704` |
| 生成frames | `124` / `24 fps` |
| Steps | `8` / `simple` scheduler |
| Seed | `2026081001` |
| Runtime flags | `--disable-dynamic-vram --novram --disable-async-offload` |

## 再現用一式

今回の経路で使うrunner一式を、この実験フォルダに追加した。

- Windows/WSL2 orchestrator: [`run-colab-l4-turbo-720p.ps1`](./run-colab-l4-turbo-720p.ps1)
- Colab setup・モデルhash検証: [`scripts/colab_h3_setup.py`](./scripts/colab_h3_setup.py)
- ComfyUI起動flags: [`scripts/colab_h3_start.py`](./scripts/colab_h3_start.py)
- ComfyUI API submit/poll・実行レポート: [`scripts/colab_h3_run.py`](./scripts/colab_h3_run.py)
- 5.00秒整形・ffprobe検証: [`scripts/trim-exact-5s.ps1`](./scripts/trim-exact-5s.ps1)
- Colab runtime固定値: [`colab_runtime.json`](./colab_runtime.json)
- API workflow: [`workflows/minimax_h3_turbo_l4_1280x704_api.json`](./workflows/minimax_h3_turbo_l4_1280x704_api.json)
- モデル名・revision・size・hash: [`../../../models/manifest.json`](../../../models/manifest.json)
- H3 VAE runtime patch: [`../../../docker/h3-runtime-patch.py`](../../../docker/h3-runtime-patch.py)

WSL2 Ubuntuと認証済みColab CLIがあるWindows環境で、次の1コマンドから実行できる。

```powershell
pwsh -File .\experiments\02-low-step-generation\colab-cli-l4-turbo-720p-5s\run-colab-l4-turbo-720p.ps1
```

初回は約`56.3 GB`（`52.45 GiB`）のモデル取得とruntime installが発生する。既に起動中のsessionでsetupを繰り返さない場合は:

```powershell
pwsh -File .\experiments\02-low-step-generation\colab-cli-l4-turbo-720p-5s\run-colab-l4-turbo-720p.ps1 -SkipSetup -KeepSession
```

`-KeepSession`はデバッグ用。既定ではrunnerが作成したsessionを、成果物ダウンロード後に停止する。Google Driveへのモデルキャッシュは次の効率化で、現時点の完了事項としては扱っていない。

wrapperの既定GPUは`-Gpu L4`。Colab CLIが受け付ける候補として`T4`、`G4`、`H100`、`A100`も指定できる。

`-OutputPath`の既定値はリポジトリ外のユーザーVideosフォルダ（`Videos\minimax-h3-colab\...mp4`）なので、生成MP4が誤ってGitへ入らない。別の外部パスも明示指定できる。

`ffmpeg.exe` / `ffprobe.exe`が`PATH`にない場合は、`-FfmpegBinDir 'C:\path\to\ffmpeg\bin'`で配置ディレクトリを指定できる。

## 結果

| Run | Status | 生成wall | Session wall | 出力 |
|---|---|---:|---:|---|
| `l4-colab-2026-08-10` | success | `1315.539秒` | `2232秒` | X添付用5.00秒MP4（local-only） |

- 生成分CU概算: 約`0.62 CU`
- session全体CU概算: 約`1.06 CU`
- Colab原本: `1280×704`、`124 frames`、`5.166667秒`、SHA-256 `8C64503640EB4022C53468718EA7FA5E4E793780B8D217B9994A8D9357111E9F`
- X添付用local-only整形版: `1280×704`、`120 frames`、`5.000000秒`、SHA-256 `35BA074D0008B03852A6B3D371ED04570148273DC53033ECF16E3A635D48EE01`
- `blackdetect` event: `0`。video/audio decode diagnosticsはfinite。

CUは公開L4レートを仮定したwall-time概算で、実際のColab UI表示を優先する。

## 出所と制約

成功runは、この実験フォルダを整備する前に完了していた。追跡済みscriptは、同じsetup・起動flags・API graph・5秒整形処理を再現用にパッケージしたものだが、元sessionで使った一時ファイルとbyte単位で同一という意味ではない。生成MP4はX添付用であり、リポジトリの証跡には含めず、Git外に置く。

- Colab CLIはWSL2経由で使う。Windowsネイティブ対応とは表現しない。
- v5 experimental artifactは現行Turbo loaderで暗号化コンテナの読み込みが止まるため使わず、hash固定したlegacy v4 LoRAで成功した。
- `SelectVAEDevice=cpu`は今回のnodeでunsupportedだったため、追跡workflowはsupportedな`default`へ修正した。
- 新規sessionではモデル再ダウンロードが発生する。Drive cacheは次の改善項目。

## 検査

```powershell
pwsh -File .\scripts\validate-experiment-lab.ps1
pwsh -File .\scripts\validate-reproducibility.ps1
```
