# MiniMax-H3 Ref2VA vs FL2VA（imagegen参照画像）

> 公開正本：[この実験フォルダ](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10)
>
> `reference-prompts.ja.md`、参照PNG 3枚、2本のAPI workflow、`experiment.json`、抽出フレームは上記フォルダから直接取得できる。生成MP4はリポジトリの生成物管理ルールでGitには含めず、X返信に実測動画を添付している。

## X投稿

- [主投稿｜Ref2VA × FL2VA比較動画](https://x.com/hAru_mAki_ch/status/2086695817826672706)
- [Ref2VA実測動画返信](https://x.com/hAru_mAki_ch/status/2086695843747487753)
- [FL2VA実測動画返信](https://x.com/hAru_mAki_ch/status/2086695868137435325)

## 結論

同じ新規参照画像3枚、同じSeed、同じ`MiniMaxH3ReferenceToVideo`ワークフローで、UNETだけをRef2VA/FL2VAに差し替えて比較した。

- 両方とも成功。7.292秒、1280×704、175フレーム、音声付き。
- OOMなし、`blackdetect=d=0.1:pix_th=0.10`の黒画面区間は両方0。
- Ref2VAは環境の導入から人物が入る流れが明瞭で、今回のプロンプトにはやや忠実。
- FL2VAは人物が早く出て、人物中心のプロフィール寄り構図になった。
- FL2VAが一方的に高画質という結果ではない。今回の動画ビットレートはRef2VAの方が高かった。
- FL2VAの音声はRef2VAより大きかった。音声品質そのものは未評価。

比較用の[コンタクトシート](./previews/contact-sheet.jpg)と[抽出フレーム](./outputs/)を公開している。タイルと実測MP4はX返信に添付したローカル成果物で、元ファイルのSHA-256は`experiment.json`と各動画返信に記録している。タイル動画は比較用に音声をミュートしている。

## 固定条件

| 項目 | 条件 |
|---|---|
| GPU | RTX 4090 |
| ComfyUI | 0.30.0 / Docker `local/minimax-h3-comfyui:v0.30.0` |
| ノード | `MiniMaxH3ReferenceToVideo` |
| 解像度 / フレーム | 1280×704 / 175 / 24fps |
| Steps / sampler / scheduler | 20 / `res_multistep` / `simple` |
| `ref_image_size` | `match` |
| Seed | `2026081011` |
| LoRA / EasyCache | なし / なし |

## 実行結果

| 条件 | モデル | ComfyUI実行時間 | MP4サイズ | 動画bitrate | 音声mean / max |
|---|---|---:|---:|---:|---:|
| A | Ref2VA | 898.216秒 | 2,461,614 bytes | 2,556,907 bps | -46.5 / -16.3 dB |
| B | FL2VA | 980.446秒 | 2,165,866 bytes | 2,232,987 bps | -39.1 / -14.9 dB |

## アセットと再現記録

- [experiment.json](./experiment.json)
- [Ref2VA workflow](./workflows/a-ref2va-api.json)（[GitHub直リンク](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10/workflows/a-ref2va-api.json)）
- [FL2VA workflow](./workflows/b-fl2va-api.json)（[GitHub直リンク](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10/workflows/b-fl2va-api.json)）
- [imagegen prompt全文](./reference-prompts.ja.md)（[GitHub直リンク](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10/reference-prompts.ja.md)）
- [参照画像フォルダ](./references/)
  - [環境PNG](https://raw.githubusercontent.com/Sunwood-ai-labs/minimax-h3-experiment-lab/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10/references/ref-imagegen-rooftop-background.png)
  - [人物ポートレートPNG](https://raw.githubusercontent.com/Sunwood-ai-labs/minimax-h3-experiment-lab/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10/references/ref-imagegen-aoi-portrait.png)
  - [人物プロフィールPNG](https://raw.githubusercontent.com/Sunwood-ai-labs/minimax-h3-experiment-lab/main/experiments/03-reference-conditioned/ref2va-vs-fl2va-imagegen-2026-08-10/references/ref-imagegen-aoi-fullbody.png)
- [抽出フレーム](./outputs/)

両条件は、参照画像3枚・プロンプト・Seed・解像度・Sampler・Schedulerを共有し、`UNETLoader.inputs.unet_name`だけを変更した。

## モデルを揃える

モデル重みはGitHubに含めていない。公式Hugging Faceの固定revision `93acf8c91365d40dc32a3abd19af06df6b6f7c65`から取得する。2条件を再現するには、`ref2va`と`fl2va`を順に実行して両方のUNETを`models/diffusion_models/`へ入れる。共通モデルを含めた必要容量は約59.1 GiB。

| ファイル | bytes | SHA-256 | 取得元 |
|---|---:|---|---|
| `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | 20,970,379,616 | `9255F52B6677845AD238F20DFAAFA94727053694127AB7F255C048F0F9365779` | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3/tree/93acf8c91365d40dc32a3abd19af06df6b6f7c65) |
| `minimax_h3_fl2va_pruned_int8_convrot.safetensors` | 20,970,379,616 | `E889202C41DAFB67B10D67B97F0D8541508036A6090AF23425A5C2615D03C47A` | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3/tree/93acf8c91365d40dc32a3abd19af06df6b6f7c65) |
| `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | 15,687,142,551 | `35A88D51044231FE332301D7A62AA81E3F2CBA62FEBEB446E2C1E3E0EF76F2C6` | 同上 |
| `minimax_h3_video_vae_fp16.safetensors` | 5,207,808,496 | `7C1F131492E7EDDACAAC9069A61B81BDD39DE5CC96561E677C5EAB1CDCE5E522` | 同上 |
| `minimax_h3_audio_vae_fp32.safetensors` | 605,254,808 | `8E505D95DD1561D47ABD43D4238FD40D9BB1AE9E147ED0A4CBA778D76AE4DB48` | 同上 |

```powershell
Copy-Item .env.example .env
(Get-Content .env) -replace '^H3_PROFILE=.*', 'H3_PROFILE=ref2va' | Set-Content .env
docker compose --profile download run --rm model-downloader
(Get-Content .env) -replace '^H3_PROFILE=.*', 'H3_PROFILE=fl2va' | Set-Content .env
docker compose --profile download run --rm model-downloader
```

downloaderがbytesとSHA-256を検証してからインストールするため、手動でファイル名を合わせるだけではなく、実験記録の重みを確認できる。

## 再現手順

```powershell
Copy-Item .\experiments\03-reference-conditioned\ref2va-vs-fl2va-imagegen-2026-08-10\references\*.png .\runtime\4090\input\ -Force
docker compose --profile 4090 build h3-4090
docker compose --profile 4090 up -d h3-4090

# Ref2VAを実行
pwsh -File .\scripts\run-h3-post-condition.ps1 `
  -Gpu 4090 -Port 8188 `
  -Workflow .\experiments\03-reference-conditioned\ref2va-vs-fl2va-imagegen-2026-08-10\workflows\a-ref2va-api.json `
  -OutputPrefix video/MiniMax_H3_imagegen_ab_ref2va `
  -LowVram $false -Seed 2026081011 -TimeoutSeconds 2400

# FL2VAを同じ入力・Seedで実行
pwsh -File .\scripts\run-h3-post-condition.ps1 `
  -Gpu 4090 -Port 8188 `
  -Workflow .\experiments\03-reference-conditioned\ref2va-vs-fl2va-imagegen-2026-08-10\workflows\b-fl2va-api.json `
  -OutputPrefix video/MiniMax_H3_imagegen_ab_fl2va `
  -LowVram $false -Seed 2026081011 -TimeoutSeconds 2400
```

`run-h3-post-condition.ps1`はComfyUIの成功状態、実行時間、出力bytes、ffprobe、blackdetect、出力SHA-256を`runtime/4090/benchmark/`へ保存する。ワークフローを直接APIへ投げる場合は、同じJSONの`prompt`を`http://127.0.0.1:8188/prompt`へPOSTすればよい。入力画像名はworkflow内の`LoadImage`と一致させる。

## 制限

1シーン・1 Seed・1つのimagegen参照セットだけの比較であり、盲検評価や自動的な人物同一性スコアは未実施。`ref_image_size=max`との比較も未実施。この差し替えは公式のR2Vモデル組み合わせではないため、複数シーンでの追試が必要。

## 公式情報

- [ComfyUI H3対応PR #15224](https://github.com/Comfy-Org/ComfyUI/pull/15224)
- [公式MiniMax-H3 R2Vワークフロー](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json)
- [元のReddit報告](https://www.reddit.com/r/StableDiffusion/comments/1vk6j2w/anyone_figure_out_how_to_get_fl2va_quality_with/)
- [参照したX投稿](https://x.com/umiyuki_ai/status/2086621244234039651)
