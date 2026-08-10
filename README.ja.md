<div align="center">
  <img src="https://raw.githubusercontent.com/Sunwood-ai-labs/minimax-h3-experiment-lab/main/docs/public/icon.svg" alt="MiniMax-H3 Experiment Lab" width="112">
  <h1>MiniMax-H3 Experiment Lab</h1>
  <p>MiniMax-H3動画生成をDocker Compose + ComfyUIで再現検証する実験ラボです。</p>
</div>

<p align="center">
  <a href="https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/actions/workflows/ci.yml"><img src="https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-5b8def.svg" alt="MIT License"></a>
  <a href="https://sunwood-ai-labs.github.io/minimax-h3-experiment-lab/"><img src="https://img.shields.io/badge/docs-GitHub%20Pages-6f42c1.svg" alt="Documentation"></a>
</p>

<p align="center"><a href="./README.md">English / 英語版README</a></p>

このリポジトリはモデル本体のミラーではなく、MiniMax-H3の検証を継続的に蓄積する実験ラボです。Docker/ComfyUI環境、再現用workflow、GPU別の処理時間、prompt、出典、失敗経路、フレームタイルを同じ場所で管理します。

## 🧭 まず見る場所

- [実験ギャラリー](./experiments/README.md)
- [Google Colab CLI L4の再現記録](./experiments/02-low-step-generation/colab-cli-l4-turbo-720p-5s/README.ja.md)
- [このページでタイルを一覧プレビュー](#🖼️-実験タイルプレビュー)
- [機械可読な実験台帳](./experiments/index.md)
- [再現性・記録の運用ガイド](./LAB.md)
- [公開ドキュメント](https://sunwood-ai-labs.github.io/minimax-h3-experiment-lab/)
- [X投稿payload・シミュレーター一覧](./social/README.md)
- [フレームタイルのルール](./LAB.md#フレームタイルプレビュー)

## 🖼️ 実験タイルプレビュー

Git clone直後でも挙動を比較できるよう、Git追跡済みのcontact sheetを表紙に直接表示します。タイルをクリックすると実験記録へ移動でき、X動画スレッドまたは参照元投稿も同じカードから開けます。生成MP4はローカルのみとし、公開視覚証跡は追跡済みタイルとmanifestです。

<table>
  <tr>
    <td width="50%" valign="top"><a href="./experiments/01-baseline/gpu-baseline/README.ja.md"><img src="./experiments/01-baseline/gpu-baseline/previews/contact-sheet.jpg" alt="GPU baseline contact sheet" width="480"></a><br><strong>GPU基準比較</strong><br>RTX 3060 / 4090 · T2V + I2V<br><a href="./experiments/01-baseline/gpu-baseline/README.ja.md">記録</a> · <a href="https://x.com/hAru_mAki_ch/status/2085730512677855266">3060 T2V</a> · <a href="https://x.com/hAru_mAki_ch/status/2085731260169953315">3060 I2V</a> · <a href="https://x.com/hAru_mAki_ch/status/2085738947553185852">4090 T2V</a> · <a href="https://x.com/hAru_mAki_ch/status/2085738981866811714">4090 I2V</a></td>
    <td width="50%" valign="top"><a href="./experiments/01-baseline/3060-black-output/README.ja.md"><img src="./experiments/01-baseline/3060-black-output/previews/contact-sheet.jpg" alt="3060 black-output contact sheet" width="480"></a><br><strong>3060黒画失敗</strong><br>成功基準と混同しないための失敗証跡<br><a href="./experiments/01-baseline/3060-black-output/README.ja.md">記録</a> · <a href="https://x.com/TlanoAI/status/2084940455809286397">参照動画投稿</a></td>
  </tr>
  <tr>
    <td valign="top"><a href="./experiments/02-low-step-generation/colab-cli-l4-turbo-720p-5s/README.ja.md"><img src="./experiments/02-low-step-generation/colab-cli-l4-turbo-720p-5s/previews/contact-sheet.jpg" alt="Google Colab CLI L4 Turbo contact sheet" width="480"></a><br><strong>Google Colab CLI L4 Turbo</strong><br>Windows → WSL2 → Colab · 1280×704 · 正確に5秒<br><a href="./experiments/02-low-step-generation/colab-cli-l4-turbo-720p-5s/README.ja.md">記録</a> · <a href="https://github.com/googlecolab/google-colab-cli">Colab CLI source</a></td>
  </tr>
  <tr>
    <td valign="top"><a href="./experiments/02-low-step-generation/lightx2v-4step/README.ja.md"><img src="./experiments/02-low-step-generation/lightx2v-4step/previews/contact-sheet.jpg" alt="LightX2V low-step contact sheet" width="480"></a><br><strong>LightX2V 4-step</strong><br>T2V / I2V · `er_sde` / `sa_solver`<br><a href="./experiments/02-low-step-generation/lightx2v-4step/README.ja.md">記録</a> · <a href="https://x.com/hAru_mAki_ch/status/2085926432086307010">Xスレッド（添付対応は未確定）</a> · <a href="https://x.com/sd_tutorial/status/2085760369612783646">参照投稿</a></td>
    <td valign="top"><a href="./experiments/03-reference-conditioned/i2v-scenes/README.ja.md"><img src="./experiments/03-reference-conditioned/i2v-scenes/previews/contact-sheet.jpg" alt="ImageGen-started I2V contact sheet" width="480"></a><br><strong>ImageGen開始I2V</strong><br>車・スポーツ・イラスト・バトル<br><a href="./experiments/03-reference-conditioned/i2v-scenes/README.ja.md">記録</a> · <a href="https://x.com/sd_tutorial/status/2085760369612783646">参照動画投稿</a></td>
  </tr>
  <tr>
    <td valign="top"><a href="./experiments/03-reference-conditioned/ref2va-6v20/README.ja.md"><img src="./experiments/03-reference-conditioned/ref2va-6v20/previews/contact-sheet.jpg" alt="ref2va steps comparison contact sheet" width="480"></a><br><strong>ref2va 6 vs 20 steps</strong><br>T2V / I2V · LoRA 0.8<br><a href="./experiments/03-reference-conditioned/ref2va-6v20/README.ja.md">記録</a> · <a href="https://x.com/hAru_mAki_ch/status/2085955887575990468">Xスレッド（添付対応は未確定）</a> · <a href="https://x.com/sd_tutorial/status/2085760369612783646">参照投稿</a></td>
    <td valign="top"><a href="./experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s/README.ja.md"><img src="./experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s/previews/contact-sheet.jpg" alt="multi-reference R2V contact sheet" width="480"></a><br><strong>複数リファレンスR2V</strong><br>背景＋人物2人 · 4シーン<br><a href="./experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s/README.ja.md">記録</a> · <a href="https://x.com/hAru_mAki_ch/status/2086019982308352292">Xスレッド（添付対応は未確定）</a> · <a href="https://x.com/sd_tutorial/status/2085760369612783646">参照投稿</a></td>
  </tr>
  <tr>
    <td valign="top"><a href="./experiments/04-acceleration/sol-sage-easycache-4scenes-7s/README.ja.md"><img src="./experiments/04-acceleration/sol-sage-easycache-4scenes-7s/previews/contact-sheet.jpg" alt="attention and cache acceleration contact sheet" width="480"></a><br><strong>Attention / cache高速化</strong><br>Sol-Attn + SageAttention + EasyCache<br><a href="./experiments/04-acceleration/sol-sage-easycache-4scenes-7s/README.ja.md">記録</a> · <a href="https://x.com/hAru_mAki_ch/status/2086051398735847471">Xスレッド（添付対応は未確定）</a> · <a href="https://x.com/sunbaolong_2001/status/2085689404031672372">参照投稿</a></td>
    <td valign="top"><a href="./experiments/05-temporal-continuity/motion-context-3segment/README.ja.md"><img src="./experiments/05-temporal-continuity/motion-context-3segment/previews/contact-sheet.jpg" alt="Motion Context contact sheet" width="480"></a><br><strong>Motion Context</strong><br>映像＋音声latentの連続性<br><a href="./experiments/05-temporal-continuity/motion-context-3segment/README.ja.md">記録</a> · <a href="https://x.com/hAru_mAki_ch/status/2086223412129902756">Xスレッド（添付対応は未確定）</a> · <a href="https://x.com/photogenicweeke/status/2085848283138891926">参照投稿</a></td>
  </tr>
  <tr>
    <td valign="top"><a href="./experiments/06-production-pipelines/catcafe-vlog-5segment/README.ja.md"><img src="./experiments/06-production-pipelines/catcafe-vlog-5segment/previews/contact-sheet.jpg" alt="Japanese cat cafe vlog contact sheet" width="480"></a><br><strong>日本語猫カフェVlog</strong><br>5セグメント · 日本語セリフ · 約30秒<br><a href="./experiments/06-production-pipelines/catcafe-vlog-5segment/README.ja.md">記録</a> · <a href="https://x.com/hAru_mAki_ch/status/2086296391702438041">X URL（添付対応は未確定）</a></td>
    <td valign="top"><a href="./experiments/06-production-pipelines/jpop-mv-5segment/README.ja.md"><img src="./experiments/06-production-pipelines/jpop-mv-5segment/previews/contact-sheet.jpg" alt="Japanese synth-pop MV contact sheet" width="480"></a><br><strong>日本語シンセポップMV</strong><br>生成音声 · ビート解析 · リリックモーション<br><a href="./experiments/06-production-pipelines/jpop-mv-5segment/README.ja.md">記録</a> · <a href="https://x.com/hAru_mAki_ch/status/2086334052639142176">X URL（添付対応は未確定）</a></td>
  </tr>
</table>

一覧表は[実験台帳](./experiments/index.md)、動画URLだけを確認する場合は[動画リンク台帳](./experiments/video-links.ja.md)を開いてください。英語版は[English ledger](./experiments/index.en.md)と[English video links](./experiments/video-links.md)です。

## 🚀 起動方法

前提は Windows 11 + WSL2 + Docker Desktop、DockerからGPUを利用できるNVIDIAドライバ、RTX 3060またはRTX 4090です。モデルはGitへ含めず、既定の`fl2va` / `ref2va` profileでは外部から約42.5GBを取得します。

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

取得profileは`.env`で選択します。`fl2va`（既定）、`ref2va`、`fl2va-lightx2v`、`ref2va-lightx2v`、`legacy-turbo`に対応しています。大きいprofileを選ぶ前に[`models/README.ja.md`](./models/README.ja.md)と、固定値を記録した[`models/manifest.json`](./models/manifest.json)を確認してください。

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
| Google Colab CLI | Windows → WSL2 → Colab CLI 0.6.0、NVIDIA L4、legacy Turbo LoRA v4、1280×704、正確な5秒出力 |

台帳には機械可読な実験記録があり、各記録からREADME、JSON、Git追跡済みタイル、タイルmanifestへ移動できます。黒画経路も削除せず、成功条件と混同しないための失敗証跡として保存しています。

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

## 🧰 再現キット

実行に必要な主要ファイルはGit管理下にあり、各実験から辿れるようにしています。

| 層 | 正本ファイル | 役割 |
|---|---|---|
| Compose | [`compose.yaml`](./compose.yaml) | RTX 3060 / RTX 4090サービスとモデル取得profile |
| Image build | [`Dockerfile`](./Dockerfile) | PyTorch base digest、ComfyUI/custom nodeのrevision、SageAttention wheel hashを固定 |
| ホスト設定 | [`.env.example`](./.env.example) | GPU UUID、モデルprofile、upstream revision、build revision |
| モデル取得 | [`docker/download-h3-model.sh`](./docker/download-h3-model.sh) | profile別にモデルを取得し、サイズとSHA-256を検査 |
| モデル固定表 | [`models/manifest.json`](./models/manifest.json) と [`models/README.ja.md`](./models/README.ja.md) | モデル名、source revision、配置先、bytes、hash |
| workflow | [`workflows/`](./workflows/) と各記録の`workflows/` | API形式のComfyUIグラフとhash |
| Google Colab CLI | [`run-colab-l4-turbo-720p.ps1`](./experiments/02-low-step-generation/colab-cli-l4-turbo-720p-5s/run-colab-l4-turbo-720p.ps1) | Windows → WSL2 → Colab session起動、setup、API実行、download、ローカル5秒検証 |
| 検証 | [`scripts/validate-reproducibility.ps1`](./scripts/validate-reproducibility.ps1) | Compose / Docker / workflow / 入力の実在性を確認 |

モデル本体と生成動画は外部・ローカル扱いです。Colab L4記録もX添付MP4をGit外に置き、contact sheet、manifest、workflow、runner、実測metadataだけを保存します。clone直後にDockerまたはColabのbuild入力、runtime、モデル固定表、workflowの構成は再現できますが、動画の再生成にはモデル取得とGPU実行が必要です。Python/apt依存は固定したupstream sourceとbuild時のpackage indexに従うため、bit単位の出力一致までは保証しません。

## 🖼️ フレームタイル

動画はローカル検証には便利ですが、READMEやXへ添付しづらいため、完了した実験は代表フレームをタイル化します。フレームは左から右、次に上から下へ時間が進みます。複数動画は入力順にブロックを縦積みし、同名manifestへ入力動画、SHA-256、fps、duration、サンプル時刻を保存します。生成元MP4は`runtime/*/output`などにローカル保存される場合があり、GitHub公開物ではタイルとmanifestを正本にします。

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

詳細なverified記録にはwall time、ComfyUI status、workflow/model hash、`ffprobe`、黒画検査、signal統計、出力hash、未検証項目を残します。古い基準・失敗記録は、再現に不足する証拠があれば明示します。`blackdetect=0`だけでは画質成功と判断しません。

## 📚 ドキュメント

- [公開ドキュメント](https://sunwood-ai-labs.github.io/minimax-h3-experiment-lab/)
- [公開成果物と動画の境界](./docs/ja/guide/artifacts.md)
- [実験ギャラリー](./experiments/README.md)
- [実験台帳](./experiments/index.md) / [English ledger](./experiments/index.en.md)
- [LAB運用ガイド](./LAB.md) / [English guide](./LAB.en.md)
- [調査メモ](./research-notes.md)
- [English research summary](./research-notes.en.md)
- [検証ログ](./verification-log.md)
- [English verification summary](./verification-log.en.md)
- [X投稿・シミュレーター](./social/README.ja.md) / [English index](./social/README.md)
- [Docker Compose](./compose.yaml)
- [動画リンク台帳](./experiments/video-links.ja.md) / [English index](./experiments/video-links.md)

## ⚖️ ライセンスと範囲

リポジトリにはruntimeコード、workflow、実験メタデータ、ドキュメント、選択したプレビュー素材を含めます。モデル本体は含めません。MiniMax-H3、ComfyUI、custom node、LoRA、取得した素材は各 upstream のライセンス・利用規約に従います。

リポジトリで作成したコード、ドキュメント、実験記録は[MIT License](./LICENSE)で公開します。実験追加時は[CONTRIBUTING.md](./CONTRIBUTING.md)を確認してください。

## 🔗 主な参照元

- [MiniMax-H3 model card](https://huggingface.co/MiniMaxAI/MiniMax-H3)
- [MiniMax-H3公式GitHub](https://github.com/MiniMax-AI/MiniMax-H3)
- [ComfyUI MiniMax-H3 guide](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)
- [Kijai MiniMax-H3 Comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy)
- [H3 Motion Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context)
