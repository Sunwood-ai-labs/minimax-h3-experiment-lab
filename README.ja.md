<div align="center">
  <img src="https://raw.githubusercontent.com/Sunwood-ai-labs/minimax-h3-experiment-lab/master/docs/public/icon.svg" alt="MiniMax-H3 Experiment Lab" width="112">
  <h1>MiniMax-H3 Experiment Lab</h1>
  <p>MiniMax-H3動画生成をDocker Compose + ComfyUIで再現検証する実験ラボです。</p>
</div>

<p align="center">
  <a href="https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/actions/workflows/ci.yml"><img src="https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/master/LICENSE"><img src="https://img.shields.io/badge/license-MIT-5b8def.svg" alt="MIT License"></a>
  <a href="https://sunwood-ai-labs.github.io/minimax-h3-experiment-lab/"><img src="https://img.shields.io/badge/docs-GitHub%20Pages-6f42c1.svg" alt="Documentation"></a>
</p>

<p align="center"><a href="./README.md">English / 英語版README</a></p>

このリポジトリはモデル本体のミラーではなく、MiniMax-H3の検証を継続的に蓄積する実験ラボです。Docker/ComfyUI環境、再現用workflow、GPU別の処理時間、prompt、出典、失敗経路、フレームタイルを同じ場所で管理します。

## 🧭 まず見る場所

- [実験台帳](./experiments/index.md)
- [再現性・記録の運用ガイド](./LAB.md)
- [公開ドキュメント](https://sunwood-ai-labs.github.io/minimax-h3-experiment-lab/)
- [X投稿payload・シミュレーター一覧](./social/README.md)
- [フレームタイルのルール](./LAB.md#フレームタイルプレビュー)

## 🚀 起動方法

前提は Windows 11 + WSL2 + Docker Desktop、DockerからGPUを利用できるNVIDIAドライバ、RTX 3060またはRTX 4090です。モデルはGitへ含めず、検証した構成では外部から約42.5GBを取得します。

```powershell
git clone https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab.git
cd minimax-h3-experiment-lab
Copy-Item .env.example .env
nvidia-smi -L
# 必要なら.envのGPU_3060_UUID / GPU_4090_UUIDを自分のUUIDへ変更

docker compose --profile 4090 build h3-4090
docker compose --profile download run --rm model-downloader
docker compose --profile 4090 up -d h3-4090
```

- RTX 4090: <http://localhost:8188>
- RTX 3060: <http://localhost:8189>
- 2枚同時: `docker compose --profile 3060 --profile 4090 up -d`

GPUサービスはComposeで分離し、モデルは読み取り専用、runtime状態は`runtime/3060`と`runtime/4090`へ分けています。

## 🧪 ここまでの検証範囲

| 分類 | 記録している内容 |
|---|---|
| 基準条件 | RTX 3060 / 4090のT2V・I2Vと、3060旧経路の黒画失敗 |
| 低ステップ | LightX2V系LoRAの4-step T2V・I2V、`er_sde` / `sa_solver` |
| 参照条件 | ImageGen開始フレームI2V、ref2va 6/20 steps、3リファレンスR2V |
| 高速化 | 同一R2V条件でのSol-Attn + SageAttention + EasyCache比較 |
| 時間連続性 | Motion Contextによる映像・音声latentのセグメント連鎖 |
| 制作パイプライン | 日本語猫カフェVlogと日本語シンセポップMV |

現在の台帳には機械可読な実験記録が10件あります。黒画経路も削除せず、成功条件と混同しないための失敗証跡として保存しています。

## 🗂️ 実験の構成

実験は日付・配布元・人物名ではなく、機能カテゴリで分類します。

```text
experiments/<category>/<slug>/
  README.md
  experiment.json
  sources.md                 # 必要な実験のみ
  workflows/                 # 実験専用API workflow
  previews/
    contact-sheet.jpg        # 共有用フレームタイル
    contact-sheet.json       # 入力・時刻・hash・解像度など
```

カテゴリは[基準条件](./experiments/01-baseline/)、[低ステップ](./experiments/02-low-step-generation/)、[参照条件](./experiments/03-reference-conditioned/)、[高速化](./experiments/04-acceleration/)、[時間連続性](./experiments/05-temporal-continuity/)、[制作パイプライン](./experiments/06-production-pipelines/)です。既存カテゴリに入る実験は同じカテゴリへslugを追加し、新機能系統だけschema・validator・台帳を同時更新してカテゴリを増やします。

## 🖼️ フレームタイル

動画はローカル検証には便利ですが、READMEやXへ添付しづらいため、可能な実験では代表フレームをタイル化します。フレームは左から右、次に上から下へ時間が進みます。複数動画は入力順にブロックを縦積みし、同名manifestへ入力動画、SHA-256、fps、duration、サンプル時刻を保存します。

```powershell
pwsh -File .\scripts\make-video-contact-sheet.ps1 `
  -InputPath .\runtime\4090\output\video\example.mp4 `
  -OutputPath .\experiments\03-reference-conditioned\my-experiment\previews\contact-sheet.jpg `
  -FrameCount 8 -Columns 4 -Overwrite
```

## 🔁 再現と検証

各実験のREADMEと`experiment.json`からworkflow、seed、モデルrevision、解像度、frames、steps、sampler、Docker条件を確認して再実行します。

```powershell
pwsh -File .\scripts\validate-experiment-lab.ps1
docker compose config --quiet
```

実行記録にはwall time、ComfyUI status、workflow/model hash、`ffprobe`、黒画検査、signal統計、出力hash、未検証項目を残します。`blackdetect=0`だけでは画質成功と判断しません。

## 📚 ドキュメント

- [公開ドキュメント](https://sunwood-ai-labs.github.io/minimax-h3-experiment-lab/)
- [実験台帳](./experiments/index.md)
- [LAB運用ガイド](./LAB.md)
- [調査メモ](./research-notes.md)
- [検証ログ](./verification-log.md)
- [X投稿・シミュレーター](./social/README.md)
- [Docker Compose](./compose.yaml)

## ⚖️ ライセンスと範囲

リポジトリにはruntimeコード、workflow、実験メタデータ、ドキュメント、選択したプレビュー素材を含めます。モデル本体は含めません。MiniMax-H3、ComfyUI、custom node、LoRA、取得した素材は各 upstream のライセンス・利用規約に従います。

リポジトリで作成したコード、ドキュメント、実験記録は[MIT License](./LICENSE)で公開します。実験追加時は[CONTRIBUTING.md](./CONTRIBUTING.md)を確認してください。

## 🔗 主な参照元

- [MiniMax-H3 model card](https://huggingface.co/MiniMaxAI/MiniMax-H3)
- [MiniMax-H3公式GitHub](https://github.com/MiniMax-AI/MiniMax-H3)
- [ComfyUI MiniMax-H3 guide](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)
- [Kijai MiniMax-H3 Comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy)
- [H3 Motion Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context)
