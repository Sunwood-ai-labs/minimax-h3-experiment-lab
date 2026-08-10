# MiniMax-H3実験: 縦長自撮りVlog / 720p・1080p・4Kアップスケール比較

> English version: [README.md](./README.md)

- ID: `seedvr2-portrait-vlog-720p-1080p-4k`
- 実施日: `2026-08-10`（JST）
- Category: `07-upscaling`
- Status: `verified`
- GPU: NVIDIA GeForce RTX 4090（24,564 MiB）
- 続編元: [SeedVR2 RTX 4090 FHD・4K動画実験](../seedvr2-4k-rtx4090/README.ja.md)

正本は[`experiment.json`](./experiment.json)、静止画の詳細は[`REPORT.md`](./REPORT.md)、7秒動画続編の詳細は[`VIDEO-EXPERIMENT-7S.md`](./VIDEO-EXPERIMENT-7S.md)です。比較タイルは[`previews/contact-sheet.jpg`](./previews/contact-sheet.jpg)、manifestは[`previews/contact-sheet.json`](./previews/contact-sheet.json)です。

![720p・1080p・4Kの比較](./previews/contact-sheet.jpg)

## X動画・参照URL

- 生成画像比較: 未投稿 / local-only（画像のみの続編）
- 前回SeedVR2結果スレッド: <https://x.com/hAru_mAki_ch/status/2086601484901495018>
- 前回参照投稿: <https://x.com/aihonobono2023/status/2086281213334213104?s=46>
- SeedVR2公式配布元: <https://huggingface.co/Comfy-Org/SeedVR2>
- 7秒動画の公開再現入口: [`reproduce.py`](./reproduce.py)。詳細は[`VIDEO-EXPERIMENT-7S.md`](./VIDEO-EXPERIMENT-7S.md)、[`workflows/`](./workflows/)、[`runs/`](./runs/)を参照。

## 何を比較したか

Image Genで作った縦長の自撮りVlog風画像を、9:16の720×1280へ整えたものを共通入力にした。720pは基準画像、1080pと4Kは同じ720p画像からSeedVR2でアップスケールした。

| 表示 | 解像度 | 内容 |
|---|---:|---|
| 720p | 720×1280 | Image Gen素材の中央crop＋Lanczos基準 |
| 1080p | 1080×1920 | 720p入力 → SeedVR2 |
| 4K | 2160×3840 | 720p入力 → SeedVR2 |

## 結果

| Run | 結果 | 処理時間 | Peak VRAM | 出力 |
|---|---|---:|---:|---|
| 720p基準 | 成功 | 5.114秒 | 841 MiB | 720×1280 |
| 1080p | 成功 | 30.112秒 | 6,843 MiB | 1080×1920 |
| 4K | 成功 | 15.116秒 | 8,651 MiB | 2160×3840 |

4K静止画は24GB VRAM内で完了し、前回の動画4K一括処理で必要だった時間分割は不要だった。色補正は`none`、1 step Euler、tile 512 / overlap 128で固定している。

## 実験キット

- 正本: [`experiment.json`](./experiment.json)
- レポート: [`REPORT.md`](./REPORT.md)
- 出典・Image Genプロンプト: [`sources.ja.md`](./sources.ja.md) / [`sources.md`](./sources.md)
- Workflow: [`workflows/`](./workflows/)
- 7秒動画runner: [`reproduce.py`](./reproduce.py)
- 再現入力: [`inputs/seedvr2_portrait_vlog_h3_start_704x1280.png`](./inputs/seedvr2_portrait_vlog_h3_start_704x1280.png)
- Image runner: [`run-seedvr2-image-api.ps1`](./run-seedvr2-image-api.ps1)
- 実行ログ: [`runs/`](./runs/)
- 視覚証跡: [`previews/contact-sheet.jpg`](./previews/contact-sheet.jpg)

生成素材と3枚のPNG、モデル重みはlocal-only。Gitへはclone-safeな比較タイル、manifest、実験記録、workflow、ログを残す。

## 制限

- 720pは1024×1536 Image Gen画像からの中央crop＋Lanczosで、ネイティブ720×1280撮影ではない。
- 1080pと4Kは同一SeedVR2条件だが、seedは別（`2026081002` / `2026081003`）。
- 顔同一性、知覚品質、局所ディテールの定量スコアは未実施。
