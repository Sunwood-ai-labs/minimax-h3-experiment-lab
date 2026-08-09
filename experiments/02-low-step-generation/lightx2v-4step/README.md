# MiniMax-H3 Kijai LightX2V 4-step LoRA

- ID: `2026-08-08-low-step-lightx2v-4step`
- Status: `verified`
- Purpose: KijaiのComfyUI向けLightX2V LoRAを、既存のMiniMax-H3 Docker Compose環境で検証する

Frame tile: [contact sheet](./previews/contact-sheet.jpg) / [manifest](./previews/contact-sheet.json)

Record: [experiment.json](./experiment.json) · [tracked frame tile](./previews/contact-sheet.jpg)

![Low-step generation frame tile](./previews/contact-sheet.jpg)

> This tracked tile is the public visual evidence; source MP4s under `runtime/*/output` remain local-only.

## X動画・参照URL

- **生成動画投稿**: [X投稿](https://x.com/hAru_mAki_ch/status/2085926432086307010) — `uncertain`。投稿シミュレーションに使ったURLで、4本のMP4添付と各runの対応は原投稿の添付情報を再確認するまで未確定。
- **参照元**: [sd_tutorialの投稿](https://x.com/sd_tutorial/status/2085760369612783646) / [Kijai MiniMax-H3 Comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy) / [LightX2V upstream](https://huggingface.co/lightx2v/Minimax-h3-Turbo/tree/main) / [LightX2V reproduction repository](https://github.com/ModelTC/Minimax-H3-Turbo)
- **workflowと動画URLの対応**:

  | Workflow | Run | X動画 |
  |---|---|---|
  | [`er_sde`](../../../workflows/minimax_h3_kijai_lightx2v_4step_1344x768_er_sde_api.json) | T2V / `b87755af...` | [X投稿](https://x.com/hAru_mAki_ch/status/2085926432086307010)（添付対応未確認） |
  | [`sa_solver`](../../../workflows/minimax_h3_kijai_lightx2v_4step_1344x768_sa_solver_api.json) | T2V / `405a78d2...` | [X投稿](https://x.com/hAru_mAki_ch/status/2085926432086307010)（添付対応未確認） |
  | [`i2v_er_sde`](../../../workflows/minimax_h3_kijai_lightx2v_4step_1344x768_i2v_er_sde_api.json) | I2V / `0734b9d9...` | [X投稿](https://x.com/hAru_mAki_ch/status/2085926432086307010)（添付対応未確認） |
  | [`i2v_sa_solver`](../../../workflows/minimax_h3_kijai_lightx2v_4step_1344x768_i2v_sa_solver_api.json) | I2V / `c56359c6...` | [X投稿](https://x.com/hAru_mAki_ch/status/2085926432086307010)（添付対応未確認） |

  URLは中央一覧だけに置かず、この実験のworkflow一覧の横に直接記載している。添付の確度が未確認のため、投稿URLを個別MP4の確定証跡とは表現しない。

## 現時点の一次情報

KijaiのHugging Faceリポジトリは、MiniMax-H3本体ではなくLoRAを配布している。READMEの記載は、`4 steps`、`0.75 LoRA strength`、`er_sde`および`sa_solver`の例である。LoRAのalphaはKijai自身が確定値としていないため、ノイズが出る場合は低いstrengthを試す注意書きがある。

X投稿の添付動画はXの公開メタデータ上、1344×768、6.583秒。公開MP4をffprobeした結果は630×360の配信用variant、24fps、158 video frames、6.656秒だった。投稿本文は「Kija's repacked Lightx2v's H3 turbo lora for Comfy support」で、Kijai版とLightX2V元配布へのリンクを含む。投稿本文にGPU、seed、prompt、sampler、schedulerは書かれていない。

## 検証方針

1. まずRTX 4090で、既存の公式FP16 video VAE / FP32 audio VAE、pruned int8 base、NVFP4 text encoderを維持する
2. Kijai full Comfy LoRAをmodel-onlyのLoRA loaderへ接続し、strength 0.75、4 stepsでT2Vを実行する
3. X動画に合わせた1344×768級・24fps・158 framesを第一候補にする。これはX公開MP4の実測値であり、元workflowの完全な再現条件ではない
4. `res_multistep / simple`と、READMEの`er_sde`または`sa_solver`の対応関係を分けて記録する。sampler名は出典にないため、推測で「同条件」と呼ばない
5. T2V成功後に、同じLoRA条件でI2Vを実行する

## 実験条件（固定予定）

- GPU: RTX 4090 first
- Compose service: `h3-4090`
- Base: `minimax_h3_fl2va_pruned_int8_convrot.safetensors`
- Text encoder: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- VAE: official FP16 video + FP32 audio
- LoRA: `models/loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`
- LoRA strength: `0.75`
- Steps: `4`
- Resolution: `1344×768` target, 32-aligned
- Frames: first run `158` (X公開MP4の実測video frame数。H3 nodeの17k+5 gridに適合)
- FPS: `24`
- Seed: T2V `2026080801`; I2V `2026080802`
- Prompt: T2Vは既存25-step baselineと同じsunrise lake prompt。I2Vは開始フレームを説明する固定prompt
- blackdetect / signalstats / ffprobe: required

## 実行結果

4本ともRTX 4090の`h3-4090`で成功した。4 steps、LoRA strength 0.75、1344×768、158 frames、24fps、`simple` scheduler、公式FP16 video VAE / FP32 audio VAEを固定し、samplerとT2V/I2Vだけを分けた。

| Mode | Sampler | Prompt ID | Inference | Runner wall | Output | blackdetect | SHA-256 |
|---|---|---|---:|---:|---|---:|---|
| T2V | `er_sde` | `b87755af-c053-42c3-8c49-6c628013b124` | 362.48 sec | 365.71 sec | local-only MP4 | 0 | `B0540FE30DC549ABA6E14B3A36270BFE7068CC76F81B2763C0949CEDD92E233E` |
| T2V | `sa_solver` | `405a78d2-9999-42b7-ab3b-759771760416` | 196.25 sec | 200.39 sec | local-only MP4 | 0 | `DFB59D2BF85A1AFDAEB4C8B3EFABDD2909E91EBD46991F2DB7933F8B96C2C682` |
| I2V | `er_sde` | `0734b9d9-105b-47b3-a562-ba4bb8e2f3b5` | 210.05 sec | 210.457 sec | local-only MP4 | 0 | `CB7A683AF4A9864CA6A1EDAB1C3F350019FF88E9329E12823601772E03791787` |
| I2V | `sa_solver` | `c56359c6-d7ca-4a64-bc30-b8add8ce5c7d` | 193.72 sec | 195.417 sec | local-only MP4 | 0 | `EB6487E54E1C8412A8BAAD2628CB25D24238E901B8939C8BF502B95C4E5F17B6` |

全出力はffprobeで`1344×768 / 24fps / 158 frames / 6.583333 sec / H.264 / AAC stereo`を確認した。先頭・中間フレームを目視し、T2Vは湖・山・霧・朝日、I2Vは開始フレーム由来の湖・山・霧・反射が成立していることを確認した。OOMは発生していない。

同一条件のT2Vでは、この環境で`sa_solver`が`er_sde`より推論時間で約45.8%短かった。ただし、この2本はsampler以外を固定した速度比較であり、画質の優劣は定量評価していない。

## 再現用ファイル

- T2V `er_sde`: `workflows/minimax_h3_kijai_lightx2v_4step_1344x768_er_sde_api.json`、SHA-256 `C7680D1756F710D114219E819303295055EEC10ABF39AD52D1920CC3617C4B42`
- T2V `sa_solver`: `workflows/minimax_h3_kijai_lightx2v_4step_1344x768_sa_solver_api.json`、SHA-256 `5AE470B6EB816C4FFC71C74FD435549B3C4F8B74C8BA868CCC0E87463D63FC7C`
- I2V `er_sde`: `workflows/minimax_h3_kijai_lightx2v_4step_1344x768_i2v_er_sde_api.json`、SHA-256 `6BD295F8EFE7D643D8D4794284955A164C73D98E3996675509102830CE59C397`
- I2V `sa_solver`: `workflows/minimax_h3_kijai_lightx2v_4step_1344x768_i2v_sa_solver_api.json`、SHA-256 `2B8AF00CB840E6E777D4B79D3B2501C81DF340BDAD672CD5AF976A959D56AA09`
- I2V開始画像: `runtime/4090/input/MiniMax_H3_I2V_1344x768_start.png`、1344×768、SHA-256 `9E5893D7C5A9919726E7E60FF2BF4F19E77F746342D38E5FE3217FD2288A3D0F`
- 変換元画像: `runtime/4090/input/MiniMax_H3_I2V_1280x704_start.png`、1280×704、SHA-256 `BE63F90186D46A2860A463C70E4E3E76FDF95A19E98F9DB9E696CD7610D96CD8`
- Kijai full LoRA: 1,956,171,984 bytes、SHA-256 `FC9B6500F0331FE925B004738BAAA31BD34104741C8BF9334816F9AC3005C8C1`
- 詳細report: `runtime/4090/benchmark/h3-<prompt_id>.md` / `.json`

## 結果

完了。X動画の解像度・長さに寄せたローカル再現としては、Kijai LoRAをDocker ComposeのMiniMax-H3へ接続し、T2V/I2Vの両方で4-step生成できた。X投稿にないGPU、prompt、seed、sampler、schedulerを含む完全一致ではなく、出典条件に対する実験室内の部分一致である。

## X親投稿用の概要動画

4本の実生成MP4をHyperFramesで2×2に同期配置し、下部に共通条件・各samplerの実測時間・OOM結果を表示した比較モンタージュを作成した。親投稿にはこの概要動画を添付し、返信には各実験の元動画と詳細情報を添付する構成にしている。

- Composition: [`hyperframes-kijai-parent-montage-2026-08-08/index.html`](../../../hyperframes-kijai-parent-montage-2026-08-08/index.html)
- Design: [`DESIGN.md`](../../../DESIGN.md)
- Output: [`MiniMax_H3_Kijai_LightX2V_parent_montage_1920x1080_24fps.mp4`](../../../sunwood-x-simulator-kijai-2026-08-08/assets/MiniMax_H3_Kijai_LightX2V_parent_montage_1920x1080_24fps.mp4)
- Format: `1920×1080 / 24fps / 158 frames / 6.583333 sec / H.264 + AAC stereo`
- Output bytes: `14,134,491`
- Output SHA-256: `77DD8806E45F8885F30A8C1528E40AED73DF819316C132D28DEAB60BF27F9F11`
- Source media: 実験1〜4の4本のみ。AIによる差し替え素材は使用していない

再現コマンド（Compositionディレクトリで実行）:

```powershell
npx hyperframes lint . --json
npx hyperframes validate .
npx hyperframes inspect . --json --samples 15
npx hyperframes render . --output renders/MiniMax_H3_Kijai_LightX2V_parent_montage_1920x1080_24fps.mp4 --fps 24 --quality standard
```

検証結果: lint `ok`、WCAG AA `35 text elements pass`、inspect `0 issues`、render `158/158 frames`。
