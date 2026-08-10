# MiniMax-H3 Ref2VA vs FL2VA（imagegen参照画像）

## 結論

同じ新規参照画像3枚、同じSeed、同じ`MiniMaxH3ReferenceToVideo`ワークフローで、UNETだけをRef2VA/FL2VAに差し替えて比較した。

- 両方とも成功。7.292秒、1280×704、175フレーム、音声付き。
- OOMなし、`blackdetect=d=0.1:pix_th=0.10`の黒画面区間は両方0。
- Ref2VAは環境の導入から人物が入る流れが明瞭で、今回のプロンプトにはやや忠実。
- FL2VAは人物が早く出て、人物中心のプロフィール寄り構図になった。
- FL2VAが一方的に高画質という結果ではない。今回の動画ビットレートはRef2VAの方が高かった。
- FL2VAの音声はRef2VAより大きかった。音声品質そのものは未評価。

比較用の[コンタクトシート](./previews/contact-sheet.jpg)、左右に並べた[タイル動画](./outputs/ref2va-vs-fl2va-tile.mp4)、上下に並べた[縦積みタイル動画](./outputs/ref2va-vs-fl2va-tile-vertical.mp4)、横幅を合わせた[フル幅縦積み動画](./outputs/ref2va-vs-fl2va-tile-vertical-fullwidth.mp4)、実際の[Ref2VA動画](./outputs/ref2va.mp4)、[FL2VA動画](./outputs/fl2va.mp4)を保存している。タイル動画は比較用に音声をミュートしている。

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
- [Ref2VA workflow](./workflows/a-ref2va-api.json)
- [FL2VA workflow](./workflows/b-fl2va-api.json)
- [imagegen prompt記録](./reference-prompts.ja.md)
- [参照画像](./references/)
- [抽出フレーム](./outputs/)

両条件は、参照画像3枚・プロンプト・Seed・解像度・Sampler・Schedulerを共有し、`UNETLoader.inputs.unet_name`だけを変更した。

## 再現コマンド

```powershell
docker compose --profile 4090 up -d h3-4090
$workflow = Get-Content -Raw .\experiments\03-reference-conditioned\ref2va-vs-fl2va-imagegen-2026-08-10\workflows\a-ref2va-api.json | ConvertFrom-Json
$body = @{ prompt = $workflow; client_id = ([guid]::NewGuid().ToString()) } | ConvertTo-Json -Depth 50
Invoke-RestMethod -Uri http://127.0.0.1:8188/prompt -Method Post -ContentType application/json -Body $body
```

FL2VAは`b-fl2va-api.json`に差し替える。

## 制限

1シーン・1 Seed・1つのimagegen参照セットだけの比較であり、盲検評価や自動的な人物同一性スコアは未実施。`ref_image_size=max`との比較も未実施。この差し替えは公式のR2Vモデル組み合わせではないため、複数シーンでの追試が必要。

## 公式情報

- [ComfyUI H3対応PR #15224](https://github.com/Comfy-Org/ComfyUI/pull/15224)
- [公式MiniMax-H3 R2Vワークフロー](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json)
- [元のReddit報告](https://www.reddit.com/r/StableDiffusion/comments/1vk6j2w/anyone_figure_out_how_to_get_fl2va_quality_with/)
- [参照したX投稿](https://x.com/umiyuki_ai/status/2086621244234039651)
