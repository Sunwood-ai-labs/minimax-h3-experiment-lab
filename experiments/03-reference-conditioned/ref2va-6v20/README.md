# MiniMax-H3 ref2va + Kijai LightX2V — 6 vs 20 steps

[English version](./README.en.md)

- 実験ID: `2026-08-08-reference-ref2va-6v20`
- 実施日: `2026-08-08 JST`
- GPU: `RTX 4090`
- 状態: `verified`
- 目的: ユーザー提供スクリーンショットに見える `ref2va`、Kijai/LightX2V LoRA、LoRA strength `0.8`、`er_sde`、`6 steps` と `20 steps` を、T2V/I2Vの両方で同じDocker Compose環境から検証する

フレームタイル: [contact sheet](./previews/contact-sheet.jpg) / [manifest](./previews/contact-sheet.json)

Record: [experiment.json](./experiment.json) · [tracked frame tile](./previews/contact-sheet.jpg)

![ref2va frame tile](./previews/contact-sheet.jpg)

> この追跡済みタイルが公開用の視覚証跡です。生成元MP4は`runtime/*/output`のローカル成果物として扱います。

## X動画・参照URL

- **生成動画投稿**: [X投稿](https://x.com/hAru_mAki_ch/status/2085955887575990468) — `uncertain`。投稿シミュレーションのURLで、T2V/I2V・6/20 stepsの各添付対応は未確認。
- **参照元**: [sd_tutorialの投稿](https://x.com/sd_tutorial/status/2085760369612783646) / [Kijai MiniMax-H3 Comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy) / [公式Comfy-Org MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)
- **workflowと動画URLの対応**:

  | Workflow | Run | X動画 |
  |---|---|---|
  | [`T2V 6-step`](./workflows/minimax_h3_ref2va_lora080_t2v_er_sde_6step_1344x768_api.json) | T2V / 6 steps | [X投稿](https://x.com/hAru_mAki_ch/status/2085955887575990468)（添付対応未確認） |
  | [`T2V 20-step`](./workflows/minimax_h3_ref2va_lora080_t2v_er_sde_20step_1344x768_api.json) | T2V / 20 steps | [X投稿](https://x.com/hAru_mAki_ch/status/2085955887575990468)（添付対応未確認） |
  | [`I2V 6-step`](./workflows/minimax_h3_ref2va_lora080_i2v_er_sde_6step_1344x768_api.json) | I2V / 6 steps | [X投稿](https://x.com/hAru_mAki_ch/status/2085955887575990468)（添付対応未確認） |
  | [`I2V 20-step`](./workflows/minimax_h3_ref2va_lora080_i2v_er_sde_20step_1344x768_api.json) | I2V / 20 steps | [X投稿](https://x.com/hAru_mAki_ch/status/2085955887575990468)（添付対応未確認） |

## 結論

4本すべて生成成功。`1344×768 / 158 frames / 24fps / 6.583333秒`のH.264/AAC動画になり、`blackdetect=0`、OOMなしだった。

6 stepsは20 stepsより明確に短いが、6 stepsと20 stepsは同じseedでも同一フレームにはならない。今回の画素比較ではT2V SSIM `0.683275`、I2V SSIM `0.684799`であり、「大枠のシーンが成立する」という意味では比較できる一方、「20 stepsとほぼ同じ画質」とまでは定量的に証明していない。

| Mode | Steps | ComfyUI実測 | runner wall | 結果 |
|---|---:|---:|---:|---|
| T2V | 6 | 459.42 sec | 460.953 sec | 成功・黒画なし・OOMなし |
| T2V | 20 | 00:10:59 | 661.217 sec | 成功・黒画なし・OOMなし |
| I2V | 6 | 294.42 sec | 295.606 sec | 成功・黒画なし・OOMなし |
| I2V | 20 | 00:11:31 | 696.292 sec | 成功・黒画なし・OOMなし |

20-stepのComfyUI時間はDockerログの`Prompt executed in 00:10:59` / `00:11:31`から記録した。runner wallはAPI投入からComfyUI historyのsuccess確認までの時間で、後処理のffprobeやSHA-256計算は含めていない。

## 再現対象と出典の境界

ユーザー提供スクリーンショットから読み取れる条件は、次の4点を再現対象にした。

- `ref2va`モデル
- Kijai/LightX2V turbo LoRA
- LoRA weight `0.8`
- `er_sde`、`6 steps`と通常の`20 steps`の比較

スクリーンショットにはGPU、prompt、seed、scheduler、EasyCache、VAE、workflow全体は写っていない。したがって、以下の実験は「見えている条件を固定したローカル検証」であり、元投稿の完全再現とは呼ばない。prompt・seed・解像度・VAEなど、写っていない項目は再現可能性のため本リポジトリで明示的に固定した。

また、LoRAファイル名には`4step`が含まれるが、今回の依頼に合わせて同じLoRAを6 stepsと20 stepsにも適用した。これは比較実験であり、LoRA配布元が6/20 stepsを公式保証しているという意味ではない。

出典と調査メモは[`sources.md`](./sources.md)に分離している。

## 実験マトリクス

steps以外を揃え、T2V/I2Vとstepsだけを変えた。

| Run | Mode | Steps | Seed | Workflow | Prompt ID |
|---|---|---:|---:|---|---|
| 1 | T2V | 6 | `2026080807` | [`t2v…6step`](./workflows/minimax_h3_ref2va_lora080_t2v_er_sde_6step_1344x768_api.json) | `976ed634-fad0-41be-bb2b-865637bb2758` |
| 2 | T2V | 20 | `2026080807` | [`t2v…20step`](./workflows/minimax_h3_ref2va_lora080_t2v_er_sde_20step_1344x768_api.json) | `23229ad1-a1da-4aa3-83e6-1d04eb74b926` |
| 3 | I2V | 6 | `2026080808` | [`i2v…6step`](./workflows/minimax_h3_ref2va_lora080_i2v_er_sde_6step_1344x768_api.json) | `40c56bb7-d5a3-489b-ad4a-08b59db84175` |
| 4 | I2V | 20 | `2026080808` | [`i2v…20step`](./workflows/minimax_h3_ref2va_lora080_i2v_er_sde_20step_1344x768_api.json) | `e6a6708a-0e2e-418d-9f5f-21709cc2e5cf` |

### 固定prompt

T2V:

```text
A calm cinematic sunrise over a quiet Japanese mountain lake, gentle mist drifting across the water, slow camera movement, natural ambient birds and soft wind, no text, five seconds.
```

I2V:

```text
Animate the supplied sunrise lake start frame into a calm cinematic shot. Preserve the mountain silhouette and composition, add gentle camera movement, natural mist drifting over the water, subtle ripples and ambient birds and soft wind, no text.
```

I2Vの開始フレームは、同じ画像を6/20 stepsで共有した。画像は[`MiniMax_H3_I2V_1344x768_start.png`](../../../runtime/4090/input/MiniMax_H3_I2V_1344x768_start.png)、`1344×768`、`1,187,835 bytes`、SHA-256は`9E5893D7C5A9919726E7E60FF2BF4F19E77F746342D38E5FE3217FD2288A3D0F`。

## 固定した推論条件

| 項目 | 値 |
|---|---|
| GPU | NVIDIA GeForce RTX 4090、24,564 MiB |
| GPU UUID | `GPU-f877fbc1-9f24-bd97-3359-dd358eaa2caa` |
| Driver | `591.86` |
| Compose service | `h3-4090`、host `8188` |
| Base | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` |
| Base size | `20,970,379,616 bytes` |
| Base SHA-256 | `9255F52B6677845AD238F20DFAAFA94727053694127AB7F255C048F0F9365779` |
| Text encoder | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` |
| Video VAE | `minimax_h3_video_vae_fp16.safetensors` |
| Audio VAE | `minimax_h3_audio_vae_fp32.safetensors` |
| LoRA | `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors` |
| LoRA size | `1,956,171,984 bytes` |
| LoRA SHA-256 | `FC9B6500F0331FE925B004738BAAA31BD34104741C8BF9334816F9AC3005C8C1` |
| LoRA loader | `LoraLoaderModelOnly` |
| LoRA strength | `0.8` |
| Sampler | `er_sde` |
| Scheduler | `simple` |
| EasyCache | reuse `0.3` / start `0.2` / end `0.9` |
| 解像度 | `1344×768`（32の倍数。前回の公開動画条件に寄せた約720p級） |
| 長さ | `158 frames`、`24fps` |
| 出力 | MP4、H.264 video、AAC stereo `32000Hz` |
| Comfy起動引数 | `--disable-pinned-memory --fp16-intermediates --preview-method none` |
| H3 memory factor | `1.0` |
| Low VRAM | requested/appliedともに`false` |
| SageAttention | 使用なし |
| CUDA module loading | `LAZY` |

ref2vaの20GBモデルは、公式Comfy-Orgファイルをchunked HTTPS downloaderで取得し、期待サイズとSHA-256を照合してからatomic installした。インストール後に`h3-4090`を再起動し、ComfyUIの`UNETLoader`でref2vaファイルが候補に出ることと、実行ログに`model_type FLOW`が出ることを確認した。

## ホスト/Docker環境

| 項目 | 値 |
|---|---|
| Host OS | Windows 11 Pro、build `26200` |
| Host RAM | `137,270,165,504 bytes` |
| PowerShell | `5.1.26100.8875` |
| Locale / timezone | `ja-JP` / `Asia/Tokyo` |
| Docker Engine | `29.4.3` |
| Docker Compose | `5.1.3` |
| Image | `local/minimax-h3-comfyui:v0.30.0` |
| ComfyUI | `0.30.0` |
| Container Python | `3.12.3` |
| PyTorch / CUDA | `2.11.0+cu130` / `13.0` |
| CUDA base | cuDNN 9 |
| Volume | `./models:/opt/ComfyUI/models:ro`、`./runtime/4090/{input,output,user}` |

## 実測結果

| Mode | Steps | Prompt ID | ComfyUI | runner wall | Output | Bytes | SHA-256 |
|---|---:|---|---:|---:|---|---:|---|
| T2V | 6 | `976ed634-fad0-41be-bb2b-865637bb2758` | 459.42 sec | 460.953 sec | local-only MP4 | 1,574,128 | `3A8B7EDA3B2F01EB3DC8635A1D7CFFBC7A7F8C9B3DE2D240BBC1145984075551` |
| T2V | 20 | `23229ad1-a1da-4aa3-83e6-1d04eb74b926` | 659 sec | 661.217 sec | local-only MP4 | 1,700,321 | `A9B8DA655BE3EB76660C034EBA04AA6A499845EABC1B877743404AF23975F39E` |
| I2V | 6 | `40c56bb7-d5a3-489b-ad4a-08b59db84175` | 294.42 sec | 295.606 sec | local-only MP4 | 2,467,722 | `228B82712E1849EA8E06CD90753F7E378515166EBF24A1711BB34C7A4C29BDEA` |
| I2V | 20 | `e6a6708a-0e2e-418d-9f5f-21709cc2e5cf` | 691 sec | 696.292 sec | local-only MP4 | 1,950,512 | `8952D5E1D639C58A9FE35F52BA94AB10E341F43EE2F4E0EE40104DE2432666E6` |

4本共通でffprobeは次を返した。

- video: `1344×768`, H.264, `24/1 fps`, `158 frames`, `6.583333 sec`
- audio: AAC-LC, stereo, `32000 Hz`, `6.575000 sec`
- `blackdetect.interval_count=0`
- ComfyUI history: `success`, `completed=true`
- Dockerログ検索: OOM/CUDA out of memory/Traceback/Errorなし

ログには起動時のTorch import順序に関するWARNINGがあるが、4本のprompt実行失敗とは関係しない。生成中は4090のGPU utilization 100%と`model_type FLOW`を確認した。

## 6 stepsと20 stepsの比較

6/20の動画を同じmode内でFFmpegのSSIM/PSNRにかけた。seedは同じだが、stepsが異なるため出力は同一フレームではない。

| 比較 | SSIM | PSNR average | 解釈 |
|---|---:|---:|---|
| T2V 6 vs 20 | `0.683275` | `14.406153 dB` | 画素一致は中程度。画質スコアではない |
| I2V 6 vs 20 | `0.684799` | `14.455215 dB` | 画素一致は中程度。画質スコアではない |

目視用ポスターは[`posters/ref2va-6v20-contact.jpg`](./posters/ref2va-6v20-contact.jpg)に保存した。並びは左上T2V 6、右上T2V 20、左下I2V 6、右下I2V 20。4本とも朝日の湖・山・霧の映像として成立している。

比較ログ:

- [`t2v-6-vs-20.ssim-ffmpeg.log`](./quality/t2v-6-vs-20.ssim-ffmpeg.log)
- [`t2v-6-vs-20.psnr-ffmpeg.log`](./quality/t2v-6-vs-20.psnr-ffmpeg.log)
- [`i2v-6-vs-20.ssim-ffmpeg.log`](./quality/i2v-6-vs-20.ssim-ffmpeg.log)
- [`i2v-6-vs-20.psnr-ffmpeg.log`](./quality/i2v-6-vs-20.psnr-ffmpeg.log)

## 再現手順

リポジトリルートで実行する。`h3-4090`を起動し、healthcheckが通った状態にする。

```powershell
cd <repo-root>
docker compose --profile 4090 up -d h3-4090
docker compose ps

.\scripts\run-h3-post-condition.ps1 -Gpu 4090 -Port 8188 -Workflow .\experiments\03-reference-conditioned\ref2va-6v20\workflows\minimax_h3_ref2va_lora080_t2v_er_sde_6step_1344x768_api.json -OutputPrefix video/MiniMax_H3_Kijai_LightX2V_Ref2VA_T2V_1344x768_6step_er_sde_lora080 -LowVram $false -Seed 2026080807 -TimeoutSeconds 1800 -SkipModelHashes

.\scripts\run-h3-post-condition.ps1 -Gpu 4090 -Port 8188 -Workflow .\experiments\03-reference-conditioned\ref2va-6v20\workflows\minimax_h3_ref2va_lora080_t2v_er_sde_20step_1344x768_api.json -OutputPrefix video/MiniMax_H3_Kijai_LightX2V_Ref2VA_T2V_1344x768_20step_er_sde_lora080 -LowVram $false -Seed 2026080807 -TimeoutSeconds 1800 -SkipModelHashes

.\scripts\run-h3-post-condition.ps1 -Gpu 4090 -Port 8188 -Workflow .\experiments\03-reference-conditioned\ref2va-6v20\workflows\minimax_h3_ref2va_lora080_i2v_er_sde_6step_1344x768_api.json -OutputPrefix video/MiniMax_H3_Kijai_LightX2V_Ref2VA_I2V_1344x768_6step_er_sde_lora080 -LowVram $false -Seed 2026080808 -TimeoutSeconds 1800 -SkipModelHashes

.\scripts\run-h3-post-condition.ps1 -Gpu 4090 -Port 8188 -Workflow .\experiments\03-reference-conditioned\ref2va-6v20\workflows\minimax_h3_ref2va_lora080_i2v_er_sde_20step_1344x768_api.json -OutputPrefix video/MiniMax_H3_Kijai_LightX2V_Ref2VA_I2V_1344x768_20step_er_sde_lora080 -LowVram $false -Seed 2026080808 -TimeoutSeconds 1800 -SkipModelHashes
```

I2Vの入力画像は、別環境でも同じ相対ファイル名`MiniMax_H3_I2V_1344x768_start.png`で`runtime/4090/input`へ配置し、上記SHA-256と一致させる。workflowと各SHA-256は[`experiment.json`](./experiment.json)にまとめた。

`-SkipModelHashes`は20GB級モデルの再ハッシュを各runで繰り返さないための指定で、runnerレポートには省略が明記される。ref2va本体については、ダウンロード時に別途期待SHA-256を照合済みである。完全な再現記録では、モデル取得元・サイズ・SHA-256を必ず確認する。

## 保存物

- 4つのAPI workflow: [`workflows/`](./workflows/)
- 機械可読な実験記録: [`experiment.json`](./experiment.json)
- 出典・スクリーンショットの制約: [`sources.md`](./sources.md)
- ComfyUI run report: `runtime/4090/benchmark/h3-<prompt_id>.json` / `.md`
- 目視ポスター: [`posters/`](./posters/)
- SSIM/PSNRログ: [`quality/`](./quality/)
