# MiniMax-H3 Experiment: pi-H3 1.0 (DWD + Spark-Attn SM89) on RTX 4090

> English record: [README.md](./README.md) · 詳細レポート: [PI_H3_RTX4090_DETAILED_REPORT.md](./PI_H3_RTX4090_DETAILED_REPORT.md)

- ID: `2026-11-23-pi-h3-dwd-spark-4090`
- Category: `02-low-step-generation`
- Status: `verified`
- GPU: `NVIDIA GeForce RTX 4090 (24564 MiB VRAM, SM 8.9)`

Record: [experiment.json](./experiment.json) · [tracked tile (480p/768p)](./previews/contact-sheet.jpg) · [manifest](./previews/contact-sheet.json) · [768p 2 vs 4-step](./previews/compare_768p_2step_vs_4step.jpg) · [720p/1080p tile](./previews/contact-sheet-720p-1080p.jpg) · [720p vs 1080p 4-step](./previews/compare_720p_vs_1080p_4step.jpg)

## ウォーム実測結果サマリー（RTX 4090 · 5.17秒 / 124 frames / 24fps + ステレオ音声）

| 条件 | DiT → 出力解像度 | Steps | Seed | ComfyUI実行時間 | クライアントWall | Peak VRAM | Avg / Peak Power | 備考 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| **`480p_2step_warm`** | `864×480` → `864×480` | 2 | 42 | **19.729 s** | 20.208 s | 23,096 MiB | 133.4 / 303.2 W | キャッシュ済み (`cached=11`) / 15,570 tokens |
| **`480p_4step_warm`** | `864×480` → `864×480` | 4 | 42 | **28.367 s** | 28.883 s | 22,979 MiB | 167.3 / 295.4 W | キャッシュ済み (`cached=11`) / 15,570 tokens |
| **`720p_2step_warm`** | `1280×736` → `1280×720` | 2 | 42 | **32.876 s** | 33.126 s | 24,029 MiB | 174.2 / 394.9 W | キャッシュ済み (`cached=11`) / 34,625 tokens |
| **`720p_4step_warm`** | `1280×736` → `1280×720` | 4 | 42 | **49.715 s** | 49.998 s | 23,969 MiB | 223.3 / 401.1 W | キャッシュ済み (`cached=11`) / 34,625 tokens |
| **`768p_2step_warm`** | `1344×768` → `1344×768` | 2 | 42 | **32.324 s** | 32.603 s | 24,007 MiB | 197.7 / 403.7 W | **公式 RTX 3090 (`gpu-unlock`) 34.6秒を上回る** / 37,881 tokens |
| **`768p_4step_warm`** | `1344×768` → `1344×768` | 4 | 42 | **49.390 s** | 49.692 s | 23,811 MiB | 245.6 / 407.6 W | 画質・速度のベストバランス / 37,881 tokens |
| **`1080p_upscaled_2step_warm`** | `1344×768` → `1920×1080` | 2 | 42 | **39.905 s** | 40.195 s | 23,949 MiB | 159.2 / 404.3 W | DWD 768p → Lanczos 1080p |
| **`1080p_upscaled_4step_warm`** | `1344×768` → `1920×1080` | 4 | 42 | **62.503 s** | 62.873 s | 23,405 MiB | 195.0 / 405.1 W | DWD 768p → Lanczos 1080p |
| `1080p_native_2step` | `1920×1088` → `1920×1080` | 2 | 42 | Error (24.275 s) | 24.722 s | 23,389 MiB | 43.6 / 61.7 W | `chunk_path="drop_k"` は現行 `spark_h3_kitchen 0.2.37` 未対応 |

- コールド / ウォームアップを含む全 17 ランの詳細データ・ステップ内訳・技術課題の修正記録は [PI_H3_RTX4090_DETAILED_REPORT.md](./PI_H3_RTX4090_DETAILED_REPORT.md) を参照してください。
- Spark-Attn SM89 (`MiniMaxH3SparkAttentionSM89`, `mode=speed`, `topk_ratio=0.2`) は全成功ランの 50 ブロックすべてで動作し、`unexpected_fallbacks=[]` を確認済みです。
- 8本すべてのウォーム出力MP4で `124 frames`, `24fps`, `AAC 32000Hz stereo`, `blackdetect=[]` を確認済みです。

## 再現手順

```powershell
# 1. モデル本体および pi-H3 1.0 DWD アダプターの取得・SHA-256 検証
$env:H3_PROFILE = "fl2va-pih3"
docker compose --profile download run --rm model-downloader

# 2. RTX 4090 用 pi-H3 ComfyUI コンテナのビルド・起動 (ポート 8195)
docker compose --profile pih3-4090 up -d --build

# 3. Suite 1 (480p / 768p) および Suite 2 (720p / 1080p) ベンチマーク実行
python experiments/02-low-step-generation/pi-h3-dwd-spark-4090/scripts/run_pih3_4090_benchmark.py
python experiments/02-low-step-generation/pi-h3-dwd-spark-4090/scripts/run_pih3_720p_1080p.py
```

## X動画・参照URL

- X投稿: 未投稿（`publication.status: not_posted`）
- Lakonik/pi-H3: https://huggingface.co/Lakonik/pi-H3
- ComfyUI-piFlow docs/piH3.md: https://github.com/Lakonik/ComfyUI-piFlow/blob/main/docs/piH3.md
- Spark-H3 v0.2.0: https://github.com/zechengtang/Spark-H3/releases/tag/comfyui-v0.2.0
