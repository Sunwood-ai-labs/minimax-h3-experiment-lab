# 出典

English notes: [sources.md](./sources.md)

| 出典 | 何を裏付けるか | 確認日時 |
|---|---|---|
| [Comfy-Org/SeedVR2](https://huggingface.co/Comfy-Org/SeedVR2) | 使用したSeedVR2の公式配布元とモデル名 | 2026-08-10 09:03 JST |
| [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) | 入力動画の元になったH3モデルファミリーの文脈 | 2026-08-10 09:03 JST |
| [aihonobono2023の参考投稿](https://x.com/aihonobono2023/status/2086281213334213104?s=46) | 続編・アップスケール実験の動機。内部workflowや設定の完全再現を示すものではない | 2026-08-10 09:03 JST |
| 公開スレッド[メイン投稿](https://x.com/hAru_mAki_ch/status/2086601484901495018) | 実験結果を公開した投稿 | 2026-08-10 |
| [実験結果reply](https://x.com/hAru_mAki_ch/status/2086601566224814552) | 実験結果に紐づく公開reply | 2026-08-10 |
| [参照URL reply](https://x.com/hAru_mAki_ch/status/2086601653873168501) | 参考投稿のURLを記載した公開reply | 2026-08-10 |
| [連続性メモ](https://x.com/hAru_mAki_ch/status/2086601745233510417) | 続編スレッドの連続性メモ | 2026-08-10 |

入力動画のパス、各runの開始・終了時刻、VRAMピーク、出力bytes、SHA-256は、推測ではなく[`runs/`](./runs/)の生ログと[`experiment.json`](./experiment.json)に記録したローカル検証値です。モデルrevisionは元のダウンロード時に保存されていないため、モデルファイルのbytesとSHA-256のみ固定しています。
