# MiniMax-H3 / RTX 4090 / SeedVR2 アップスケール実験レポート

実験日: 2026-08-10（JST）
正本: [`experiment.json`](./experiment.json)
参考URL: <https://x.com/aihonobono2023/status/2086281213334213104?s=46>

## 結論

- 1344×768 / 158フレームの入力をFHD（1920×1080）へ全編アップスケールできた。
- 4K（3840×2160）は9フレームのスモークテストに成功した。
- 同じ4K workflowへ158フレームを一括投入すると、`VAEDecodeTiled`でCUDA OOMになった。peakは24,004 MiB。
- 4Kを0.75秒単位に8本、最後を0.583333秒に分割すると、9/9本が成功した。SeedVR2処理の合計は1,228.317秒（約20分28秒）。
- 結合後に元動画のAAC音声を再接続し、タイムスタンプを補正した検証済み最終版を得た。

最終版（local-only）:

```text
runtime/4090/output/video/seedvr2_experiment_4k_segmented_full_verified2.mp4
3840×2160 / 158 frames / 24 fps
video 6.583333 s / audio 6.575 s / start 0
bytes 22,213,512
SHA-256 BF4D8E497DD6FC69ED07F5C2256623988ED9E6963C992050A51E6B2CD842FB07
```

`blackdetect`（`pix_th=0.1`）では黒画面区間を検出しなかった。分割境界の視覚確認は[`previews/contact-sheet.jpg`](./previews/contact-sheet.jpg)に固定した。

## 条件

| 項目 | 値 |
|---|---|
| GPU | NVIDIA GeForce RTX 4090 / 24,564 MiB |
| Driver | 591.86 |
| ComfyUI | 0.30.0（Docker service `h3-4090`） |
| PyTorch | 2.11.0+cu130 |
| 入力 | 1344×768 / 158f / 24fps / 映像6.583333秒 |
| SeedVR2 | `seedvr2_3b_int8_convrot.safetensors`、1 step |
| VAE | `seedvr2_ema_vae_fp16.safetensors` |
| Sampler | Euler / `simple` / CFG 1 / seed `2026081001` |
| Preprocess | Lanczos resize + center crop |
| VAE tile | 512 / overlap 128 / temporal 64 / temporal overlap 8 |
| 音声 | 元AACを保持し、最終4K映像へremux |

モデルのbytesとSHA-256は[`experiment.json`](./experiment.json)へ記録した。重みはリポジトリにコミットしない。

## 実験結果

| 実験 | 結果 | 処理時間 | peak VRAM | 最大温度 | 出力 |
|---|---|---:|---:|---:|---|
| FHD全編 | 成功 | 260.600秒 | 13,199 MiB | 84°C | 1920×1080 / 158f |
| 4Kスモーク | 成功 | 60.199秒 | 12,677 MiB | 81°C | 3840×2160 / 9f |
| 4K一括 | `VAEDecodeTiled` OOM | 996.950秒 | 24,004 MiB | 85°C | 未生成 |
| 4K分割全編 | 9/9成功 | 1,228.317秒* | 最大16,400 MiB | 86°C | 3840×2160 / 158f |

\* 9本のSeedVR2処理のみ。結合・音声再接続は含まない。

### 4K分割の内訳

| Segment | 開始秒 | 長さ秒 | 結果 | 処理秒 | Peak MiB | 最大温度 |
|---:|---:|---:|---|---:|---:|---:|
| 00 | 0.000000 | 0.750000 | 成功 | 205.412 | 16,400 | 84°C |
| 01 | 0.750000 | 0.750000 | 成功 | 130.308 | 12,016 | 85°C |
| 02 | 1.500000 | 0.750000 | 成功 | 130.322 | 12,016 | 86°C |
| 03 | 2.250000 | 0.750000 | 成功 | 130.447 | 12,016 | 85°C |
| 04 | 3.000000 | 0.750000 | 成功 | 130.393 | 12,016 | 86°C |
| 05 | 3.750000 | 0.750000 | 成功 | 130.488 | 12,016 | 86°C |
| 06 | 4.500000 | 0.750000 | 成功 | 130.253 | 12,016 | 86°C |
| 07 | 5.250000 | 0.750000 | 成功 | 130.262 | 12,016 | 86°C |
| 08 | 6.000000 | 0.583333 | 成功 | 110.432 | 12,016 | 86°C |

## 再現

API workflowは[`workflows/`](./workflows/)、実行スクリプトは[`run-seedvr2-api.ps1`](./run-seedvr2-api.ps1)と[`run-seedvr2-4k-segments.ps1`](./run-seedvr2-4k-segments.ps1)、生ログは[`runs/`](./runs/)に分離した。

```powershell
.\run-seedvr2-api.ps1 `
  -Workflow .\workflows\seedvr2_upscale_fhd_api.json `
  -ReportName seedvr2_fhd_full `
  -TimeoutSeconds 14400
```

```powershell
.\run-seedvr2-4k-segments.ps1 `
  -StartSegment 0 -SegmentCount 9 -SegmentSeconds 0.75 `
  -TotalSeconds 6.583333 -TimeoutSeconds 3600
```

9本を[`workflows/seedvr2_4k_concat_list.txt`](./workflows/seedvr2_4k_concat_list.txt)で結合し、元音声を次の条件で再接続した。

```text
ffmpeg -itsoffset -0.031006 -i segmented_full.mp4 -i source.mp4 -map 0:v:0 -map 1:a:0 -c:v copy -c:a copy verified2.mp4
```

## 本質的な観察

4K一括処理のボトルネックはH3生成ではなく、SeedVR2のVAE decodeがフレーム列全体を扱うときのメモリ使用量だった。9フレームなら約12.7GBで通るが、158フレーム一括では24GB近くまで膨らみ、`VAEDecodeTiled`で失敗する。時間分割によって入力時系列の大きさを固定することが、4090での実用解になる。

代償は処理時間と分割境界である。今回のコンタクトシートでは黒画面・大きな構図飛びは確認しなかったが、定量的なseam scoreは実施していない。

## 未検証・制限

- 参考投稿の正確なworkflow、prompt、seed、モデルrevision。
- 4K単一パスを通すための別VAE設定、offload、tile設定の最適値。
- 分割境界の人物同一性・画質・音声の定量評価。
- SeedVR2の元ダウンロードrevision。ローカルファイルのbytesとSHA-256は固定済み。
- 生成MP4、入力PNG、モデル重みはlocal-only。clone後に再現可能なworkflow、manifest、JSON、Markdown、VRAM CSV、contact sheetを追跡する。
