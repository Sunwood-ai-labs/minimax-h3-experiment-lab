# MiniMax-H3 Experiment: pi-H3 1.0 (DWD + Spark-Attn SM89) on RTX 4090

- ID: `2026-11-23-pi-h3-dwd-spark-4090`
- Category: `02-low-step-generation`
- Status: `verified`
- GPU: `NVIDIA GeForce RTX 4090 (24564 MiB VRAM, SM 8.9)`

Record: [experiment.json](./experiment.json) · [tracked tile](./previews/contact-sheet.jpg) · [manifest](./previews/contact-sheet.json) · [768p comparison](./previews/compare_768p_2step_vs_4step.jpg)

## 実測結果サマリー（RTX 4090 · 5.17秒 / 124 frames / 24fps + ステレオ音声）

| 条件 | Seed | ComfyUI実行時間 | クライアントWall | Peak VRAM | Avg / Peak Power | キャッシュ状態 |
|---|---:|---:|---:|---:|---:|---|
| `480p_2step_cold` (864×480, 2-step) | 100 | 1463.079 s | 1463.342 s | 23,868 MiB | 13.2 / 296.2 W | コールド (初回読込+コンパイル) |
| **`480p_2step_warm`** (864×480, 2-step) | 42 | **19.729 s** | 20.208 s | 23,096 MiB | 133.4 / 303.2 W | モデル・プロンプトキャッシュ済み (`cached=11`) |
| `768p_2step_warmup` (1344×768, 2-step) | 41 | 72.526 s | 72.792 s | 23,592 MiB | 114.3 / 404.5 W | 解像度変更+初回768pコンパイル (`cached=9`) |
| **`768p_2step_warm`** (1344×768, 2-step) | 42 | **32.324 s** | 32.603 s | 24,007 MiB | 197.7 / 403.7 W | モデル・プロンプトキャッシュ済み (`cached=11`) |
| `480p_4step_cold` (864×480, 4-step) | 100 | 76.216 s | 76.729 s | 23,731 MiB | 99.1 / 293.3 W | 4-stepアダプター切替+再エンコード (`cached=5`) |
| **`480p_4step_warm`** (864×480, 4-step) | 42 | **28.367 s** | 28.883 s | 22,979 MiB | 167.3 / 295.4 W | モデル・プロンプトキャッシュ済み (`cached=11`) |
| `768p_4step_warmup` (1344×768, 4-step) | 41 | 83.495 s | 83.848 s | 23,411 MiB | 167.3 / 409.1 W | 解像度変更+再エンコード (`cached=9`) |
| **`768p_4step_warm`** (1344×768, 4-step) | 42 | **49.390 s** | 49.692 s | 23,811 MiB | 245.6 / 407.6 W | モデル・プロンプトキャッシュ済み (`cached=11`) |

- Spark-Attn SM89 (`MiniMaxH3SparkAttentionSM89`, `mode=speed`, `topk_ratio=0.2`) は全50ブロックで動作し、`unexpected_fallbacks=[]` を確認。
- 4本すべてのウォーム出力MP4で `124 frames`, `24fps`, `AAC 32000Hz stereo`, `blackdetect=[]` を確認。

## X video / reference URLs

- X video post: Not posted (`publication.status: not_posted`)
- Lakonik/pi-H3: https://huggingface.co/Lakonik/pi-H3
- ComfyUI-piFlow docs/piH3.md: https://github.com/Lakonik/ComfyUI-piFlow/blob/main/docs/piH3.md
- Spark-H3 v0.2.0: https://github.com/zechengtang/Spark-H3/releases/tag/comfyui-v0.2.0

