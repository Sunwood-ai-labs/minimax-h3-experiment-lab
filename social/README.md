# X投稿・シミュレーター台帳

このディレクトリは、MiniMax-H3実験の公開説明を再現するためのX投稿payloadと、投稿前シミュレーターへの入口です。実験条件の正本は`experiments/`、投稿順・本文・添付の正本は各payloadです。

動画・音声は容量が大きいため通常のGit整理コミットには含めません。シミュレーターの動画srcはローカル検証用で、公開cloneでは追跡済みposter・フレームタイルへフォールバックします。公開配布が必要になった段階でGit LFSまたは外部artifact保存先を選びます。

X投稿やREADMEでは、動画本体の代わりに各実験の`previews/contact-sheet.jpg`を優先します。タイルは挙動の変化を一枚で確認でき、同名`contact-sheet.json`から入力動画・サンプル時刻・SHA-256を追跡できます。

## シミュレーター一覧

| 機能 / 実施日 | 正本の実験記録 | シミュレーター | payload / 下書き |
|---|---|---|---|
| GPU比較 / 2026-08-07 | [GPU baseline](../experiments/01-baseline/gpu-baseline/README.md) | [3060](../sunwood-x-simulator-2026-08-07/index.html) · [4090](../sunwood-x-simulator-4090-2026-08-07/index.html) | [3060 thread](../sunwood-x-thread-payload-2026-08-07.json) · [4090 thread](../sunwood-x-thread-payload-4090-2026-08-07.json) |
| 低ステップ / 2026-08-08 | [LightX2V 4-step](../experiments/02-low-step-generation/lightx2v-4step/README.md) | [シミュレーター](../sunwood-x-simulator-kijai-2026-08-08/index.html) | [simulation JSON](../sunwood-x-kijai-simulation-2026-08-08.json) |
| ImageGen開始I2V / 2026-08-08 | [4テーマI2V](../experiments/03-reference-conditioned/i2v-scenes/README.md) | [シーン実験](../sunwood-x-simulator-kijai-scenes-2026-08-08/index.html) | [simulation JSON](../sunwood-x-kijai-scenes-simulation-2026-08-08.json) |
| ref2va比較 / 2026-08-08 | [ref2va 6 vs 20](../experiments/03-reference-conditioned/ref2va-6v20/README.md) | [ref2va](../sunwood-x-simulator-ref2va-2026-08-08/index.html) | [simulation JSON](../sunwood-x-ref2va-simulation-2026-08-08.json) |
| 複数リファレンスR2V / 2026-08-08 | [multi-reference R2V](../experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s/README.md) | [R2V simulator](../sunwood-x-simulator-r2v-multi-reference-2026-08-08/index.html) | [payload](../sunwood-x-simulator-r2v-multi-reference-2026-08-08/payload.json) |
| R2V高速化 / 2026-08-09 | [Sol-Attn + Sage + EasyCache](../experiments/04-acceleration/sol-sage-easycache-4scenes-7s/README.md) | [高速化実験](../sunwood-x-simulator-r2v-optimizations-2026-08-09/index.html) | [payload](../sunwood-x-simulator-r2v-optimizations-2026-08-09/payload.json) |
| Motion Context / 2026-08-09 | [3セグメント連鎖](../experiments/05-temporal-continuity/motion-context-3segment/README.md) | [Motion Context](../sunwood-x-simulator-h3-motion-context-2026-08-09/index.html) | [payload](../sunwood-x-simulator-h3-motion-context-2026-08-09/payload.json) |
| 日本語猫カフェVlog / 2026-08-09 | [5セグメントVlog](../experiments/06-production-pipelines/catcafe-vlog-5segment/README.md) | [cat-cafe Vlog](../sunwood-x-simulator-h3-catcafe-vlog-2026-08-09/index.html) | [payload](../sunwood-x-simulator-h3-catcafe-vlog-2026-08-09/payload.json) |
| 日本語シンセポップMV / 2026-08-09 | [5セグメントMV](../experiments/06-production-pipelines/jpop-mv-5segment/README.md) | [J-pop MV](../sunwood-x-simulator-h3-mv-jpop-2026-08-09/index.html) | [payload](../sunwood-x-simulator-h3-mv-jpop-2026-08-09/payload.json) |

日付は実験日を示すだけで、分類軸ではありません。`sunwood-x-simulator-*`や`hyperframes-*`は投稿用の既存アセット置き場（legacy publication assets）であり、新しい実験は必ず機能別の`experiments/<category>/<slug>/`へ追加します。

## 投稿済みの主なスレッド

- [猫カフェVlog](https://x.com/hAru_mAki_ch/status/2086296391702438041)
- [日本語シンセポップMV](https://x.com/hAru_mAki_ch/status/2086334052639142176)

投稿済みかどうかは、各payloadの`simulationOnly`、実験記録、ローカル投稿履歴で確認します。シミュレーターは投稿前の確認面であり、Xの実際のギャラリー表示そのものではありません。

## 投稿時の整理ルール

- 親投稿はURLなし。
- 各返信は直前の投稿へ連結する。
- 異なるURLは別返信へ分ける。
- 1投稿あたりの添付は4本以下。
- 技術的な結果・条件・制限は本文に残し、機械的なQAメモだけを公開文にしない。
- 実験記録の相対パス、動画のSHA-256、生成条件をpayloadと対応づける。
