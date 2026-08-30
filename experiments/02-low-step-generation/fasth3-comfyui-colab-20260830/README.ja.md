# FastH3 × ComfyUI VSA — 公開Colab

FastVideo系のFastH3 4-step checkpointを、ComfyUIのVSAブランチで実行する再現用ノートブックです。

## 開く

- [Google Colabで開く](https://colab.research.google.com/github/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/02-low-step-generation/fasth3-comfyui-colab-20260830/FastH3_ComfyUI_Colab.ipynb)
- [GitHub上のノートブック](./FastH3_ComfyUI_Colab.ipynb)
- [APIワークフローJSON](./workflows/fasth3_vsa_t2v_832x480_api.json)

## これは何か

この実験で使うFastH3は、通常のMiniMax-H3チェックポイントや、コミュニティにある「MiniMax H3 Fast T2V」ワークフローとは別物です。

- FastH3 checkpoint: minimax_h3_fastvideo_vsa_datafree_1300step_4step_int8_convrot.safetensors
- ComfyUI: Kijai/ComfyUIのvsaブランチ固定コミット
- サンプラー: Euler + FastVideo 4-step sigma ladder
- 音声経路: audio VAE → VAEDecodeAudio → CreateVideo → SaveVideo
- 出力条件: 832×480、124 frames、24 fps、H.264/AAC MP4、約5.17秒

ノートブックは、公開Hugging Faceリポジトリからモデルを各自のColabランタイムへ取得します。Drive、rclone、アクセストークン、ローカルPCのパスは使いません。

## 実行条件

- A100 40GB以上を推奨します。ColabでA100が割り当てられるかは契約・混雑状況によって変わります。
- /content に少なくとも65 GiBの空き容量が必要です。4つのモデルファイルだけで約52 GiBあります。
- GPUなしのランタイムでは、ダウンロード前のpreflightで停止します。
- セルを上から順に実行してください。ComfyUIは生成後に停止します。

過去のA100-SXM4-40GB実測では、ComfyUIのプロンプト処理は162.64秒、観測したピークVRAMは24,045 MiBでした。この値は別ランタイムの実測であり、ColabのCU消費を保証する値ではありません。CUの確定値はColab側のリソースメーターを確認してください。

## 固定した公開リビジョン

- ComfyUI VSA: 10febb01d7be73d1491cf5e5347b5ab8b6c2c09e
- FastH3 repository: Kijai/MiniMax-H3-experimental
- FastH3 revision: f4cac997f880e93cf6940af61ee8d58ef31ff7f3
- H3 text encoder / VAE repository: Comfy-Org/MiniMax-H3
- H3 revision: 4cc1d817b6184899b41293954329f576cb5ae86b

モデルの利用条件は、各Hugging Faceリポジトリのライセンスと利用規約を確認してください。

## 検証状態

- APIグラフ: ローカルのComfyUI VSA環境でFastH3 checkpointを使った実行を確認済み。
- 公開ノートブック: GitHubからColabで開ける再現手順として公開。
- MP4: 大容量成果物のため、このリポジトリには含めません。ノートブック実行時にColabランタイムへ生成します。

## 参考

- [FastVideo — FastH3 preview example](https://github.com/hao-ai-lab/FastVideo/blob/main/examples/inference/basic/basic_fasth3_lora_preview.py)
- [Kijai — MiniMax-H3 experimental](https://huggingface.co/Kijai/MiniMax-H3-experimental)
- [Comfy-Org — MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)
- [ComfyUI VSA branch](https://github.com/kijai/ComfyUI/tree/vsa)
