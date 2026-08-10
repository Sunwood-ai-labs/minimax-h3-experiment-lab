# MiniMax-H3 Experiment: <短い名前>

> English default: [README.md](./README.md)

- ID: `<YYYY-MM-DD-slug>`
- Category: `<01-baseline|02-low-step-generation|03-reference-conditioned|04-acceleration|05-temporal-continuity|06-production-pipelines|07-upscaling>`
- Status: `planned`
- GPU: `<RTX ...>`
- Owner: `MiniMax-H3 Experiment Lab`

このREADMEと同じディレクトリの`experiment.json`を機械可読な正本にします。出典にない値を推測で補完せず、検証用に固定した値と分けて記録します。

Record: [experiment.json](./experiment.json) · [tracked tile](./previews/contact-sheet.jpg) · [manifest](./previews/contact-sheet.json)

Video/source X URL: `<https://x.com/...>` or `Not published / local-only`

公開用の視覚証跡は追跡済みのフレームタイルとmanifestです。生成MP4・音声・モデル重みは通常local-onlyとして扱い、READMEのリンクにはせず、`experiment.json`へパス・bytes・SHA-256を記録します。

テンプレートは`experiments/<category>/<slug>/`へコピーします。実施日は`experiment.json`に記録し、フォルダ名には日付を使いません。

## 仮説

何を検証し、何と比較するか。

## 出典

詳細は同じディレクトリの`sources.md`（英語）と`sources.ja.md`（日本語）へ。出典に書かれていない条件は推測で埋めない。

## 実験条件

- Docker Compose service:
- Docker image:
- ComfyUI / Python / PyTorch / CUDA:
- Base model:
- Text encoder:
- VAE:
- LoRA / strength:
- Resolution / frames / fps:
- Steps / sampler / scheduler:
- EasyCache / attention / offload:
- Seed / prompt:

## 再現キット

- Compose: [`compose.yaml`](../../../compose.yaml)
- Image build: [`Dockerfile`](../../../Dockerfile)
- Host config: [`.env.example`](../../../.env.example)
- Model setup: [`docker/download-h3-model.sh`](../../../docker/download-h3-model.sh)
- Model lock: [`models/manifest.json`](../../../models/manifest.json)
- Workflow JSON: `./workflows/` or a shared file under [`workflows/`](../../../workflows/)

## 実行結果

| Run | Status | Start | End | runner wall | OOM | blackdetect |
|---|---|---|---|---:|---|---:|
| 1 | pending | | | | | |

## 成果物

相対パス、bytes、SHA-256、ffprobe結果、目視確認を書きます。

## 結論と制限

- 結論:
- 再現範囲:
- 未検証:

## 追加後の確認

```powershell
.\scripts\validate-experiment-lab.ps1
.\scripts\validate-reproducibility.ps1
```
