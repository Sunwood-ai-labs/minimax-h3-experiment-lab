# MiniMax-H3 I2V × SeedVR2 / 7秒動画アップスケール実験

実験日: 2026-08-10（JST）  
GPU: NVIDIA GeForce RTX 4090 / 24,564 MiB  
実行基盤: ComfyUI Docker service `h3-4090` / API `8188`  
公開再現キット: [`reproduce.py`](./reproduce.py) と固定workflow、入力画像を同梱

## 目的

Image Genで作成した縦長の自撮りVlog風スタートフレームをMiniMax-H3 I2Vで約7秒の動画にし、同じ時間軸を720p基準・1080p SeedVR2・4K SeedVR2で比較する。比較用タイルは3本を同じ時刻でhstackし、音声を削除した。

## 生成条件

### MiniMax-H3 I2V

| 項目 | 値 |
|---|---|
| workflow | `workflows/h3_portrait_vlog_i2v_7s_704x1280_api.json` |
| runner | [`reproduce.py`](./reproduce.py) の `h3-i2v` 呼び出し |
| 解像度 | 704×1280 |
| フレーム | 175 |
| fps | 24 |
| steps | 4 |
| sampler / scheduler | `sa_solver` / `simple` |
| seed | `2026081013` |
| UNET | `minimax_h3_fl2va_pruned_int8_convrot.safetensors` |
| LoRA | `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors` / strength `0.75` |
| CLIP | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| VAE | `minimax_h3_video_vae_fp16.safetensors` + audio VAE `minimax_h3_audio_vae_fp32.safetensors` |
| wall time | `420.81秒`（7分00.81秒） |

生成動画は比較入力用に720×1280へ整形し、`runtime/4090/input/seedvr2_portrait_vlog_h3_i2v_7s_720p_baseline.mp4`へ固定した。720p基準整形の専用wall timeは記録していない。

### SeedVR2

| 項目 | 値 |
|---|---|
| workflow | `workflows/seedvr2_portrait_vlog_7s_1080p_segment_api.json` / `seedvr2_portrait_vlog_7s_4k_segment_api.json` |
| runner | [`reproduce.py`](./reproduce.py) の10区間呼び出し |
| model | `seedvr2_3b_int8_convrot.safetensors` |
| VAE | `seedvr2_ema_vae_fp16.safetensors` |
| resize | Lanczos / center crop |
| VAE tile | 512 / overlap 128 / temporal 64 / temporal overlap 8 |
| temporal chunk | auto / temporal overlap 0 |
| sampler | Euler / `simple` / 1 step / CFG 1.0 / denoise 1.0 |
| segment | 0.75秒×9 + 0.541667秒×1 = 10区間 |

## 実測結果

| 出力 | 解像度 | Seed | GPU処理wall合計 | 出力bytes | SHA-256 |
|---|---:|---:|---:|---:|---|
| 720p基準 | 720×1280 | — | H3: 420.81秒 | 4,779,616 | `BF0C1D0950F1FD4465C105FC556F5E999D694B52EC7F6F95E29D60E04DDD0044` |
| 1080p SeedVR2 | 1080×1920 | 2026081014 | 376.637秒 | 12,756,252 | `90A8126D9A4F2E88D8B85B5291F17B9C69CEE2EF99EAAA708406953BBB18D3BC` |
| 4K SeedVR2 | 2160×3840 | 2026081015 | 1262.468秒 | 48,318,200 | `7721AC5EE9FB8108A474D67D49DEEAB10F254F4543310AD6DA1AB62516C2B1F5` |

3つのrunner wall合計は`2059.915秒`（約34分20秒）。再起動待ち、ffmpeg結合、返信用ラッパー作成、ファイルコピーは含めない。1080pと4Kの個別結合MP4はAAC音声を保持し、比較タイルだけ`-an`で無音化した。

## 再現手順（公開入口）

前提はWindows 11 + WSL2 + Docker Desktop + NVIDIA GPU、Python 3.10以上、`ffmpeg`です。リポジトリの共通セットアップは[`docs/ja/guide/reproduce.md`](../../../docs/ja/guide/reproduce.md)に従います。

```powershell
git clone https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab.git
cd minimax-h3-experiment-lab
Copy-Item .env.example .env
(Get-Content .env) -replace '^H3_PROFILE=.*', 'H3_PROFILE=fl2va-lightx2v' | Set-Content .env
docker compose --profile 4090 build h3-4090
docker compose --profile download run --rm model-downloader
docker compose --profile 4090 up -d h3-4090
```

SeedVR2の次の2ファイルは[`Comfy-Org/SeedVR2`](https://huggingface.co/Comfy-Org/SeedVR2)から取得し、`models/diffusion_models/seedvr2_3b_int8_convrot.safetensors`と`models/vae/seedvr2_ema_vae_fp16.safetensors`へ配置します。モデル重みはGitへ含めません。

```powershell
python .\experiments\07-upscaling\seedvr2-portrait-vlog-720p-1080p-4k\reproduce.py --target both --tile
```

`reproduce.py`は同梱の入力画像をComfyUIのinputへコピーし、H3 I2V、720p共通入力整形、SeedVR2の10区間×1080p/4K、結合、無音タイルまでAPI経由で実行する。実行結果は`runtime/4090/output/`、最後の実行概要は`runs/public-reproduction-last-run.json`へ出力する。PowerShellファイルは既存のローカル補助用で、公開再現の前提ではない。

区間ごとのJSON・Markdown・VRAM CSV、workflow、merge reportは同じ実験フォルダ内に保存している。

## 観察と次回検証

同期タイルでは4K側に微細な粒状ノイズが乗っているように見える。ただし、縮小表示・H.264圧縮・SeedVR2の復元処理を切り分けていないため未断定とする。次回は同一フレームの顔・髪・背景・平坦部をcropし、画素標準偏差、高周波成分、フレーム間差分を720p／1080p／4Kで比較する。
