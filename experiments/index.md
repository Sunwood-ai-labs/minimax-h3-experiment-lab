# MiniMax-H3 Experiment Lab — 実験台帳

> English ledger: [index.en.md](./index.en.md)

更新日: 2026-08-09 JST
プロジェクト: `<repo-root>`

この台帳は、実施日ではなく「検証した機能」で実験を探せるように整理しています。実施日は各`experiment.json`の`date`に残し、詳細な条件・prompt・workflow・出力SHA-256・処理時間は各実験ディレクトリの`README.md`と`experiment.json`を正本とします。

各実験の動画挙動を素早く確認するため、可能な場合は`previews/contact-sheet.jpg`に代表フレームをタイル表示し、同名JSONに入力動画とサンプル時刻を記録します。

まず視覚的に探す場合は[実験ギャラリー](./README.md)を開いてください。各カードからREADME、`experiment.json`、追跡済みタイル、タイルmanifestへ移動できます。
動画投稿・参照元のURLだけを確認する場合は[動画リンク台帳](./video-links.md)を開いてください。生成結果のXスレッドと、条件を調べた参照投稿を区別しています。

## 機能別の入口

- [基準条件・GPU比較](#01--基準条件gpu比較)
- [低ステップ生成](#02--低ステップ生成)
- [参照条件付き生成](#03--参照条件付き生成)
- [高速化](#04--高速化)
- [時間連続性](#05--時間連続性)
- [制作パイプライン](#06--制作パイプライン)

## フォルダ契約

```text
experiments/<category>/<slug>/
  README.md
  experiment.json
  sources.md              # 英語の出典メモ（必要な実験）
  sources.ja.md           # 日本語の出典メモ（必要な実験）
  workflows/              # 実験専用workflow
  outputs/ posters/ ...   # 小さな証跡・成果物
```

`category`は機能名、`slug`は実験内容です。日付や配布元の名前を分類軸にしません。出典元の名前は`experiment.json`と`README.md`の出典欄に記録します。

既存カテゴリに収まる追加実験は、同じカテゴリに新しい`slug`を作ります。新しい機能系統だけを新カテゴリとして追加し、その場合はschema・validator・この台帳を同じ変更で更新します。

## ステータス定義

- `planned`: 条件と目的を定義済み、未実行
- `running`: 実行中または結果整理中
- `verified`: 実行成功、出力検査、条件記録が完了
- `partial`: 一部条件のみ実行、差分を明記
- `failed`: OOM、黒画、node errorなどを再現し原因を記録

## 01 — 基準条件・GPU比較

| ID | 実施日 | GPU / 条件 | 結果 | 記録 | タイル |
|---|---|---|---|---|---|
| `2026-08-07-gpu-baseline` | 2026-08-07 | RTX 3060 / 4090、T2V / I2V、864×480〜1280×704 | verified | [日本語](./01-baseline/gpu-baseline/README.md) / [English](./01-baseline/gpu-baseline/README.en.md) / [JSON](./01-baseline/gpu-baseline/experiment.json) / [3060 benchmark](../runtime/3060/benchmark/index.ja.md) / [4090 benchmark](../runtime/4090/benchmark/index.ja.md) | [contact sheet](./01-baseline/gpu-baseline/previews/contact-sheet.jpg) / [manifest](./01-baseline/gpu-baseline/previews/contact-sheet.json) |
| `2026-08-07-3060-legacy-black-output` | 2026-08-07 | 旧Turbo/full-int8 + int8 VAE | failed | [日本語](./01-baseline/3060-black-output/README.md) / [English](./01-baseline/3060-black-output/README.en.md) / [JSON](./01-baseline/3060-black-output/experiment.json) | [contact sheet](./01-baseline/3060-black-output/previews/contact-sheet.jpg) / [manifest](./01-baseline/3060-black-output/previews/contact-sheet.json) |

RTX 3060は、旧int8経路では黒画になった一方、公式FP16/FP32 VAE構成・WSL再起動後の1280×704 T2V/I2Vでは完走しました。失敗経路も削除せず、再発防止の証跡として残しています。

## 02 — 低ステップ生成

| ID | 実施日 | 機能 | 状態 | 記録 | タイル |
|---|---|---|---|---|---|
| `2026-08-08-low-step-lightx2v-4step` | 2026-08-08 | LoRAによる4-step T2V / I2V、1344×768、`er_sde` / `sa_solver` | verified | [日本語](./02-low-step-generation/lightx2v-4step/README.md) / [English](./02-low-step-generation/lightx2v-4step/README.en.md) / [JSON](./02-low-step-generation/lightx2v-4step/experiment.json) | [contact sheet](./02-low-step-generation/lightx2v-4step/previews/contact-sheet.jpg) / [manifest](./02-low-step-generation/lightx2v-4step/previews/contact-sheet.json) |

配布元・実装元は出典欄に記録し、フォルダは「少ないstepで生成する機能」で分類しています。

## 03 — 参照条件付き生成

| ID | 実施日 | 機能 | 状態 | 記録 | タイル |
|---|---|---|---|---|---|
| `2026-08-08-reference-i2v-scenes` | 2026-08-08 | ImageGen開始フレームを使う車・スポーツ・イラスト・バトルのI2V | verified | [日本語](./03-reference-conditioned/i2v-scenes/README.md) / [English](./03-reference-conditioned/i2v-scenes/README.en.md) / [JSON](./03-reference-conditioned/i2v-scenes/experiment.json) | [contact sheet](./03-reference-conditioned/i2v-scenes/previews/contact-sheet.jpg) / [manifest](./03-reference-conditioned/i2v-scenes/previews/contact-sheet.json) |
| `2026-08-08-reference-ref2va-6v20` | 2026-08-08 | ref2va、T2V / I2V、6 / 20 steps | verified | [日本語](./03-reference-conditioned/ref2va-6v20/README.md) / [English](./03-reference-conditioned/ref2va-6v20/README.en.md) / [JSON](./03-reference-conditioned/ref2va-6v20/experiment.json) | [contact sheet](./03-reference-conditioned/ref2va-6v20/previews/contact-sheet.jpg) / [manifest](./03-reference-conditioned/ref2va-6v20/previews/contact-sheet.json) |
| `2026-08-08-reference-multi-r2v-4scenes-7s` | 2026-08-08 | 背景＋人物2人の3リファレンス、4シーン、約7秒 | verified | [日本語](./03-reference-conditioned/multi-reference-r2v-4scenes-7s/README.md) / [English](./03-reference-conditioned/multi-reference-r2v-4scenes-7s/README.en.md) / [JSON](./03-reference-conditioned/multi-reference-r2v-4scenes-7s/experiment.json) | [contact sheet](./03-reference-conditioned/multi-reference-r2v-4scenes-7s/previews/contact-sheet.jpg) / [manifest](./03-reference-conditioned/multi-reference-r2v-4scenes-7s/previews/contact-sheet.json) |

参照画像を入力して内容・人物・背景を保持する系統を、I2V / ref2va / R2Vとしてまとめています。

## 04 — 高速化

| ID | 実施日 | 機能 | 状態 | 記録 | タイル |
|---|---|---|---|---|---|
| `2026-08-08-acceleration-sol-sage-easycache-4scenes-7s` | 2026-08-08 | Sol-Attn + 汎用FP16 CUDA SageAttention + EasyCache | verified | [日本語](./04-acceleration/sol-sage-easycache-4scenes-7s/README.md) / [English](./04-acceleration/sol-sage-easycache-4scenes-7s/README.en.md) / [JSON](./04-acceleration/sol-sage-easycache-4scenes-7s/experiment.json) | [contact sheet](./04-acceleration/sol-sage-easycache-4scenes-7s/previews/contact-sheet.jpg) / [manifest](./04-acceleration/sol-sage-easycache-4scenes-7s/previews/contact-sheet.json) |
| diagnostics | 2026-08-08 | attention / cache経路の比較・失敗診断 | diagnostic | [診断README](./04-acceleration/diagnostics/README.md) / [workflow](./04-acceleration/diagnostics/solattn-kjnodes-easycache-4scenes-7s/workflows/scene-01-sunset-meeting_api.json) | [親実験のタイル](./04-acceleration/sol-sage-easycache-4scenes-7s/previews/contact-sheet.jpg) |

同条件の4シーンで平均`738.7935 → 353.14525 sec`、平均`2.092倍`でした。参照投稿の最大3.2倍は、このDocker・RTX 4090・ref2va条件では再現していません。

## 05 — 時間連続性

| ID | 実施日 | 機能 | 状態 | 記録 | タイル |
|---|---|---|---|---|---|
| `niko-h3-motion-context-3segment` | 2026-08-09 | 映像・音声latentと22フレームのコンテキストを引き継ぐ連鎖生成 | verified | [日本語](./05-temporal-continuity/motion-context-3segment/README.md) / [English](./05-temporal-continuity/motion-context-3segment/README.en.md) / [JSON](./05-temporal-continuity/motion-context-3segment/experiment.json) | [contact sheet](./05-temporal-continuity/motion-context-3segment/previews/contact-sheet.jpg) / [manifest](./05-temporal-continuity/motion-context-3segment/previews/contact-sheet.json) |

## 06 — 制作パイプライン

| ID | 実施日 | 機能 | 状態 | 記録 | タイル |
|---|---|---|---|---|---|
| `h3-japanese-catcafe-vlog-5segment` | 2026-08-09 | 英語prompt＋日本語セリフ、約30秒の5セグメントVlog | verified | [日本語](./06-production-pipelines/catcafe-vlog-5segment/README.md) / [English](./06-production-pipelines/catcafe-vlog-5segment/README.en.md) / [JSON](./06-production-pipelines/catcafe-vlog-5segment/experiment.json) | [contact sheet](./06-production-pipelines/catcafe-vlog-5segment/previews/contact-sheet.jpg) / [manifest](./06-production-pipelines/catcafe-vlog-5segment/previews/contact-sheet.json) |
| `h3-mv-jpop-5segment` | 2026-08-09 | H3生成音声、123 BPM解析、HyperFramesリリックモーション | verified | [日本語](./06-production-pipelines/jpop-mv-5segment/README.md) / [English](./06-production-pipelines/jpop-mv-5segment/README.en.md) / [JSON](./06-production-pipelines/jpop-mv-5segment/experiment.json) | [contact sheet](./06-production-pipelines/jpop-mv-5segment/previews/contact-sheet.jpg) / [manifest](./06-production-pipelines/jpop-mv-5segment/previews/contact-sheet.json) |

## 成果物・再現入口

- GPU別の詳細レポート: [runtime/3060 日本語](../runtime/3060/benchmark/index.ja.md) / [English](../runtime/3060/benchmark/index.md)、[runtime/4090 日本語](../runtime/4090/benchmark/index.ja.md) / [English](../runtime/4090/benchmark/index.md)
- 共有workflow: [workflows](../workflows)
- 実験テンプレート: [experiments/_template](./_template/README.md)
- X用の動画・投稿payload: [social/README](../social/README.md)
- X動画・参照投稿URL: [video-links.ja.md](./video-links.ja.md) / [English](./video-links.md)

生成MP4・音声・モデル重みは通常Gitへ含めません。公開cloneで確認できる視覚証跡は追跡済みタイルとmanifestで、動画本体のパスとSHA-256は各記録に残します。

## 次の実験を追加するとき

機能に対応するカテゴリへテンプレートをコピーします。

```powershell
Copy-Item experiments/_template experiments/03-reference-conditioned/my-experiment -Recurse
# README.md / experiment.json / sources.md / workflow / 成果物を記録
.\scripts\validate-experiment-lab.ps1
```

実験の結論には、完全再現・部分一致・未検証を明示します。GPUや解像度が違う結果は、同一条件の速度比較として扱いません。
