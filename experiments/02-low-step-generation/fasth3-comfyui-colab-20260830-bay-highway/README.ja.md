# FastH3 × ComfyUI VSA — 湾岸高速道路シーン

FastH3 4-step VSAチェックポイントを、ComfyUIのVSAブランチで湾岸の高速道路シーンに適用する再現用ノートブックです。

- [Google Colabで開く](https://colab.research.google.com/github/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/02-low-step-generation/fasth3-comfyui-colab-20260830-bay-highway/FastH3_BayHighway_Colab.ipynb)
- [H3プロンプト本文](./prompt.h3.txt)
- [APIワークフロー](./workflows/fasth3_bay_highway_vsa_t2v_832x480_api.json)

## プロンプトの固定

プロンプトは、H3/A100運用リファレンスの構造（`integrated_multimodal_description`、Shotの時間指定、カメラ・連続性・禁止事項、`overall_soundscape`）で作成しています。実行スクリプトはworkflowを読み込んだあと、プロンプト本文を注入し、本文のSHA256をログとmetricsへ保存します。

今回の主題は、雨上がりの湾岸高架高速道路を走る銀色のスポーツクーペです。湾・夜景・港の光を背景に、広いインターチェンジのカーブで制御されたドリフトを行い、エンジン音、タイヤ音、水しぶき、風、控えめな電子音を同期させます。

生成前の状態: A100での新規生成待ち。生成後は、run ID・prompt ID・プロンプトハッシュ・MP4ハッシュを同一runとして照合し、MP4の映像・音声・尺・代表フレームを確認します。
