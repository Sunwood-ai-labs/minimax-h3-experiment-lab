# Sources and evidence

English source note: [sources.en.md](./sources.en.md)

## Direct references

1. [Kijai/MiniMax-H3_comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy) — KijaiのComfyUI向けMiniMax-H3配布物。今回のLoRAファイルは `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`。
2. [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) — `minimax_h3_ref2va_pruned_int8_convrot.safetensors`の取得元。
3. [関連するX参照](https://x.com/sd_tutorial/status/2085760369612783646) — リポジトリ全体で参照しているKijai/LightX2V関連投稿。今回の添付スクリーンショットと同一投稿であることは、スクリーンショットだけからは断定していない。

## User-provided screenshot

実験の直接のきっかけは、ユーザーが添付したXのスクリーンショット。画面から読み取れる主張を次のように転記した。

- `ref2va`モデル
- LightX2V turbo LoRA
- LoRA weight `0.8`
- sampler `er_sde`
- `6` stepsで、通常の`20` stepsと「あまり遜色ない」旨

添付画像自体には元ポストのURL、GPU、seed、prompt、scheduler、VAE、EasyCache、workflow全体が含まれていない。そのため本実験では、見えている条件は固定し、見えていない条件をREADME/JSONで明示的に定義した。これは「投稿と同じ条件を完全再現した」とは扱わない。

## Model verification

- ref2va: `20,970,379,616 bytes`
- ref2va SHA-256: `9255F52B6677845AD238F20DFAAFA94727053694127AB7F255C048F0F9365779`
- Kijai LoRA: `1,956,171,984 bytes`
- Kijai LoRA SHA-256: `FC9B6500F0331FE925B004738BAAA31BD34104741C8BF9334816F9AC3005C8C1`

ref2vaは標準の`hf download`が0 byteで停止したため、同じDocker imageのPython HTTPS downloaderでRange取得・再構成した。既存prefixを再利用し、期待サイズとSHA-256を確認してから対象ファイルへatomic installした。インストール後に4090 Compose serviceを再起動し、ComfyUIのモデル一覧、実行ログの`model_type FLOW`、4本のsuccess historyを確認した。
