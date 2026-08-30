# FastH3 × ComfyUI VSA — 湾岸高速道路シーン

FastH3 4-step VSAチェックポイントを、ComfyUIのVSAブランチで湾岸の高速道路シーンに適用する再現用ノートブックです。

- [Google Colabで開く](https://colab.research.google.com/github/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/02-low-step-generation/fasth3-comfyui-colab-20260830-bay-highway/FastH3_BayHighway_Colab.ipynb)
- [H3プロンプト本文](./prompt.h3.txt)
- [APIワークフロー](./workflows/fasth3_bay_highway_vsa_t2v_832x480_api.json)
- [r2実行記録](./runs/fasth3_bay_highway_a100_20260830_r2.json)
- 生成物の保存先: `MyDrive/FastH3-runs/<RUN_ID>/`（Google Driveをマウントして直接保存）

## プロンプトの固定

プロンプトは、H3/A100運用リファレンスの構造（`integrated_multimodal_description`、Shotの時間指定、カメラ・連続性・禁止事項、`overall_soundscape`）で作成しています。実行スクリプトはworkflowを読み込んだあと、プロンプト本文を注入し、本文のSHA256をログとmetricsへ保存します。

今回の主題は、雨上がりの湾岸高架高速道路を走る銀色のスポーツクーペです。湾・夜景・港の光を背景に、広いインターチェンジのカーブで制御されたドリフトを行い、エンジン音、タイヤ音、水しぶき、風、控えめな電子音を同期させます。

## r2実測結果

`fasth3-bay-highway-a100-20260830-r2` はA100-SXM4-40GB上で新規生成し、出力MP4をColabランタイムから回収して再検証しました。今回の生成はDrive直書き版へ切り替える前の実行でしたが、次回以降の公開ノートブックはDrive未マウントなら生成を開始しない構成です。

- 状態: `verified_in_this_runtime`
- prompt ID: `7c3fc04d-e549-4907-bfb1-c21a2eb060f4`
- H3プロンプトSHA256: `0a1d95053fde758bbe7d0ebd1e405729dc230ab800db1ce90db5c27c10c8a349`
- MP4 SHA256: `7d69316ce8b4f95fd3cfc93367d9b121147de2811611517488b88205b0fccdad`
- 生成時間: 210.671秒（runner観測）／203.32秒（ComfyUIログ）
- GPU: NVIDIA A100-SXM4-40GB、観測ピークVRAM: 23,652 MiB
- メディア: H.264/AAC、832×480、124 frames、24 fps、5.167秒、32 kHz stereo

MP4本体はGitへ登録せず、実行時のDrive runディレクトリとローカル検証記録で管理します。再現時は、run ID・prompt ID・プロンプトSHA256・MP4 SHA256を同一runとして照合し、MP4の映像・音声・尺・代表フレームを確認してください。
