# MiniMax-H3実験: RTX 4090 / SeedVR2 FHD・4Kアップスケール

> English default: [README.md](./README.md)

- ID: `seedvr2-rtx4090-fhd-4k-segmented`
- 実施日: `2026-08-10`（JST）
- Category: `07-upscaling`
- Status: `verified`
- GPU: NVIDIA GeForce RTX 4090（24,564 MiB）

機械可読な正本は[`experiment.json`](./experiment.json)、詳細レポートは[`REPORT.md`](./REPORT.md)です。Gitへ追跡する視覚証跡は[コンタクトシート](./previews/contact-sheet.jpg)と[サンプリングmanifest](./previews/contact-sheet.json)です。

## X動画・参照URL

- 生成動画スレッド: [メイン投稿](https://x.com/hAru_mAki_ch/status/2086601484901495018) · [実験結果reply](https://x.com/hAru_mAki_ch/status/2086601566224814552)
- 続編スレッド: [参照URL reply](https://x.com/hAru_mAki_ch/status/2086601653873168501) · [連続性メモ](https://x.com/hAru_mAki_ch/status/2086601745233510417)
- 参考にした投稿: [aihonobono2023](https://x.com/aihonobono2023/status/2086281213334213104?s=46)
- SeedVR2公式配布元: [Comfy-Org/SeedVR2](https://huggingface.co/Comfy-Org/SeedVR2)
- H3モデルの文脈: [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)

## 実験の目的

MiniMax-H3で生成済みの1344×768 / 158フレーム動画を、RTX 4090上のSeedVR2でFHDと4Kへアップスケールする。4K全編の一括処理がVRAM不足になる場合、時間方向の分割で全編を完了できるかを確認する。

入力は既存のMiniMax-H3 LightX2V I2Vバトル動画です。この実験ではH3生成自体は再実行していません。参考投稿のworkflow・prompt・seed・モデルrevisionは、公開情報にないものを推測せず、完全再現とは扱いません。

## 固定条件

| 項目 | 条件 |
|---|---|
| 入力 | 1344×768、158フレーム、24fps、映像6.583333秒、音声6.575秒 |
| 出力 | FHD 1920×1080 / 4K 3840×2160 |
| SeedVR2 | 3B INT8 diffusion + FP16 EMA VAE |
| サンプラー | Euler / `simple`、1 step、CFG 1.0、seed `2026081001` |
| 前処理 | Lanczosリサイズ＋中央crop |
| VAEタイル | tile 512、overlap 128、temporal size 64、overlap 8 |
| 4K分割 | 0.75秒×8本＋最後0.583333秒 |
| 音声 | 元AACを保持し、検証済み4K映像へremux |

## 実行結果

| 実験 | 結果 | 実行時刻（JST） | 処理時間 | Peak VRAM | 出力 |
|---|---|---|---:|---:|---|
| FHD全編 | 成功 | 00:06:10.126–00:10:30.726 | 260.600秒 | 13,199 MiB | 1920×1080 / 158f |
| 4Kスモーク | 成功 | 00:11:40.313–00:12:40.512 | 60.199秒 | 12,677 MiB | 3840×2160 / 9f |
| 4K一括 | `VAEDecodeTiled`でCUDA OOM | 00:13:06.241–00:29:43.191 | 996.950秒 | 24,004 MiB | なし |
| 4K分割全編 | 9/9成功 | 00:31:52.222–00:53:13.753 | 1228.317秒* | 16,400 MiB | 3840×2160 / 158f |

\* 9本のSeedVR2処理だけの合計。結合・音声再接続は含みません。

4K最終検証版はlocal-onlyです。

```text
runtime/4090/output/video/seedvr2_experiment_4k_segmented_full_verified2.mp4
22,213,512 bytes
SHA-256: BF4D8E497DD6FC69ED07F5C2256623988ED9E6963C992050A51E6B2CD842FB07
```

`ffprobe`では3840×2160、H.264/AAC、158フレーム、24fps、映像6.583333秒、音声6.575秒、両方start 0です。記録した`blackdetect`では黒画面区間はありません。実行JSON・Markdown・VRAM CSVは[`runs/`](./runs/)、API workflowは[`workflows/`](./workflows/)に配置しています。

## 本質的な観察

4K一括処理のボトルネックはH3生成ではなく、SeedVR2のVAE decodeにおける時間方向のメモリ使用量です。9フレームの4K処理は通る一方、158フレームを一括投入すると24GB近くまで膨らみます。4090での実用的な解は、時間方向に分割してVRAM上限を固定する構成です。代償は処理時間の増加と、分割境界の目視確認です。

## 再現キット

- 単発runner: [`run-seedvr2-api.ps1`](./run-seedvr2-api.ps1)
- 4K分割runner: [`run-seedvr2-4k-segments.ps1`](./run-seedvr2-4k-segments.ps1)
- API workflow: [`workflows/`](./workflows/)
- 生ログ: [`runs/`](./runs/)
- 出典: [`sources.md`](./sources.md) / [`sources.ja.md`](./sources.ja.md)

生成MP4・入力PNG・モデル重みはリポジトリのclone-safe方針に従いlocal-onlyです。パス、bytes、SHA-256は`experiment.json`に記録しています。
