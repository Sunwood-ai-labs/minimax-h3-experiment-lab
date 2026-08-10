# MiniMax-H3 / RTX 4090 / SeedVR2 縦長Vlog画像アップスケール続編レポート

実験日: 2026-08-10（JST）  
正本: [`experiment.json`](./experiment.json)  
前回: [`seedvr2-4k-rtx4090`](../seedvr2-4k-rtx4090/README.ja.md)

## 結論

- Image Genで作成した架空の成人自撮りVlog素材を、9:16の720×1280へ中央crop＋Lanczos変換した。
- その同一720p入力をSeedVR2へ渡し、1080×1920と2160×3840の両方を1枚画像の1 passで生成できた。
- 4K画像でも記録上のRTX 4090 peak VRAMは8,651 MiBで、前回の動画4K一括処理のような時間方向分割は不要だった。
- 720p・1080p・4Kを同じ構図で横並びにした証跡を[`previews/contact-sheet.jpg`](./previews/contact-sheet.jpg)へ固定した。

![720p / 1080p / 4K comparison](./previews/contact-sheet.jpg)

## 比較の定義

| 表示 | 解像度 | 役割 | SeedVR2 |
|---|---:|---|---|
| 720p | 720×1280 | Image Gen素材から作った共通入力の基準 | なし |
| 1080p | 1080×1920 | 共通720p入力をLanczos resize後にアップスケール | あり |
| 4K | 2160×3840 | 共通720p入力をLanczos resize後にアップスケール | あり |

720pは「入力基準」であり、3枚すべてがSeedVR2出力という意味ではない。1080pと4Kは同じ720p PNGから実行しているため、素材差ではなく解像度・SeedVR2処理差を比較できる。

## 条件

| 項目 | 値 |
|---|---|
| GPU | NVIDIA GeForce RTX 4090 / 24,564 MiB |
| Driver | 591.86 |
| ComfyUI | 0.30.0 / Docker service `h3-4090` |
| PyTorch | 2.11.0+cu130 |
| Image Gen素材 | 1024×1536、架空の成人自撮りVlog、local-only |
| 720p前処理 | Lanczos + center crop、720×1280 |
| SeedVR2入力 | 720×1280 PNGを1080p／4Kの両方で共有 |
| SeedVR2 | `seedvr2_3b_int8_convrot.safetensors`、1 step |
| VAE | `seedvr2_ema_vae_fp16.safetensors` |
| Sampler | Euler / `simple` / CFG 1.0 |
| Seed | 1080p: `2026081002` / 4K: `2026081003` |
| VAE tile | 512 / overlap 128 / temporal 64 / temporal overlap 8 |
| 色補正 | `none` |

モデルbytesとSHA-256、Image Genプロンプトは[`sources.md`](./sources.md)と[`experiment.json`](./experiment.json)に記録した。

## 実行結果

| Run | 結果 | 実行時刻（JST） | 処理時間 | Peak VRAM | 最大温度 | 出力 |
|---|---|---|---:|---:|---:|---|
| 720p基準作成 | 成功 | 10:23:23.008–10:23:28.122 | 5.114秒 | 841 MiB | 37°C | 720×1280 PNG |
| 1080p SeedVR2 | 成功 | 10:24:03.417–10:24:33.528 | 30.112秒 | 6,843 MiB | 54°C | 1080×1920 PNG |
| 4K SeedVR2 | 成功 | 10:24:50.545–10:25:05.661 | 15.116秒 | 8,651 MiB | 63°C | 2160×3840 PNG |

4K runはComfyUIの既存ロードノードを一部cacheしていたため、wall timeにはcache状態を含む。生成画像自体の厳密な品質比較は、同一PNGのピクセル差・顔同一性スコア・知覚品質スコアでは評価していない。

## 出力ハッシュ

| Label | Path | Bytes | SHA-256 |
|---|---|---:|---|
| 720p baseline | `runtime/4090/output/image/seedvr2_portrait_vlog_720p_source_00001_.png` | 1,445,393 | `C89A249352F32C952730109FD2EB0DA296163F595E0EB4F7D3EAEC0866182929` |
| 1080p SeedVR2 | `runtime/4090/output/image/seedvr2_portrait_vlog_1080p_00001_.png` | 2,970,656 | `2494CBCD4A5969F9C77E37D8FCD4BEA78D14A57E3F48C65EF410CEE968C95030` |
| 4K SeedVR2 | `runtime/4090/output/image/seedvr2_portrait_vlog_4k_00001_.png` | 13,757,456 | `8FD9E71E688C4C6E359B9B39CAB4B968F21C31368B7B37C15CF114A9A9F2F25B` |

## 再現

ComfyUIのinput mountにImage Gen素材を配置した後、720p基準を作る。

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\run-seedvr2-image-api.ps1 `
  -Workflow .\workflows\prepare_portrait_720p_api.json `
  -ReportName prepare_720p_source
```

生成された720p PNGをinput mountへコピーし、1080pと4Kを同じ入力から実行する。

```powershell
Copy-Item `
  ..\..\..\runtime\4090\output\image\seedvr2_portrait_vlog_720p_source_00001_.png `
  ..\..\..\runtime\4090\input\seedvr2_portrait_vlog_720p_source_00001_.png

powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\run-seedvr2-image-api.ps1 `
  -Workflow .\workflows\seedvr2_portrait_1080p_api.json `
  -ReportName seedvr2_1080p

powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\run-seedvr2-image-api.ps1 `
  -Workflow .\workflows\seedvr2_portrait_4k_api.json `
  -ReportName seedvr2_4k
```

生ログは[`runs/`](./runs/)、API workflowは[`workflows/`](./workflows/)、プロンプトと出典は[`sources.md`](./sources.md) / [`sources.ja.md`](./sources.ja.md)にある。

## 本質的な観察と制限

今回の静止画では、前回動画実験の主ボトルネックだった時間方向のlatent列が1枚分に収まるため、4Kでも分割なしで処理できた。比較上は1080pが最もシャープ・彩度変化が見え、4Kは自然なディテール保持と軽い色味差が確認できるが、これは目視所見であり、定量評価ではない。

Image Gen原素材、720p入力、1080p／4K出力、モデル重みはlocal-only。Gitへはcontact sheet、manifest、JSON、workflow、runner、実行ログを追跡する。
