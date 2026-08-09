# X投稿・シミュレーター台帳

このディレクトリは、MiniMax-H3実験の公開説明を再現するためのX投稿payloadと、実際の添付動画を確認するシミュレーターへの入口です。実験条件の正本は`experiments/`、投稿順・本文・添付の正本は各payloadです。

動画・音声は容量が大きいため通常のGit整理コミットには含めず、ローカルのシミュレーターと実験記録から参照します。公開配布が必要になった段階でGit LFSまたは外部artifact保存先を選びます。

## シミュレーター一覧

| 日付 | 内容 | シミュレーター | payload / 下書き |
|---|---|---|---|
| 2026-08-07 | RTX 3060 T2V / I2V | [3060](../sunwood-x-simulator-2026-08-07/index.html) | [thread payload](../sunwood-x-thread-payload-2026-08-07.json) |
| 2026-08-07 | RTX 4090 T2V / I2V | [4090](../sunwood-x-simulator-4090-2026-08-07/index.html) | [thread payload](../sunwood-x-thread-payload-4090-2026-08-07.json) |
| 2026-08-08 | 低ステップ動画生成（4-step T2V / I2V） | [シミュレーター](../sunwood-x-simulator-kijai-2026-08-08/index.html) | [simulation JSON](../sunwood-x-kijai-simulation-2026-08-08.json) |
| 2026-08-08 | 参照付きI2V（車・スポーツ・イラスト・バトル） | [シーン実験](../sunwood-x-simulator-kijai-scenes-2026-08-08/index.html) | [simulation JSON](../sunwood-x-kijai-scenes-simulation-2026-08-08.json) |
| 2026-08-08 | ref2va 6 vs 20 steps | [ref2va](../sunwood-x-simulator-ref2va-2026-08-08/index.html) | [simulation JSON](../sunwood-x-ref2va-simulation-2026-08-08.json) |
| 2026-08-08 | 複数リファレンスR2V | [multi-reference R2V](../sunwood-x-simulator-r2v-multi-reference-2026-08-08/index.html) | `payload.json` |
| 2026-08-09 | R2V高速化（Sol-Attn + Sage + EasyCache） | [高速化実験](../sunwood-x-simulator-r2v-optimizations-2026-08-09/index.html) | `payload.json` |
| 2026-08-09 | Motion Context 3セグメント | [Motion Context](../sunwood-x-simulator-h3-motion-context-2026-08-09/index.html) | `payload.json` |
| 2026-08-09 | 日本語猫カフェVlog | [cat-cafe Vlog](../sunwood-x-simulator-h3-catcafe-vlog-2026-08-09/index.html) | `payload.json` |
| 2026-08-09 | 日本語シンセポップMV | [J-pop MV](../sunwood-x-simulator-h3-mv-jpop-2026-08-09/index.html) | `payload.json` |

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
