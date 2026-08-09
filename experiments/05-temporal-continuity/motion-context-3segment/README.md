# MiniMax-H3 Motion Context 3セグメント実験

実施日: 2026-08-09 JST
Experiment ID: `niko-h3-motion-context-3segment`
状態: `verified`

## 結論

`ComfyUI-H3-Motion-Context` をDockerイメージへ組み込み、RTX 4090で3セグメントのT2V連鎖を実行した。セグメント2・3では、前セグメントの映像コンテキスト、音声コンテキスト、保存済みのvideo/audio latentを同時に渡した。

今回の720p相当条件（1280×704）では、3本ともComfyUIの実行履歴が`success`、OOMなし、`blackdetect`で黒画区間なし、H.264/AACで出力された。Motion Contextのログではセグメント2の音声ドリフトが`0.00ms`、セグメント3が`0.01ms`だった。最終的な連結動画は14.417秒になった。

ただし、元投稿の1920×1088条件、元投稿と同じseed・prompt・workflow、元投稿が示す速度や画質は今回検証していない。今回の目的は、まず再利用可能なDocker Compose環境でMotion Contextの3段連鎖と音声同期を再現することに置いた。

## 参照元

- 実装: [NikoDemon80/ComfyUI-H3-Motion-Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context)
- 使用した実装revision: `15fc6a7bf7b78efb27f33d7eef3818e7ed0e118a`
- 実験のきっかけになった投稿: [Photogenic WeekendのX投稿](https://x.com/photogenicweeke/status/2085848283138891926?s=46)

元投稿の本文はユーザー提供スクリーンショットで確認した。そこでは、固定seedで`seg1 5s`、`seg2 5s (+1s相代)`、`seg3 6s (+1s相代)`の3分割生成を行い、映像と音声を一貫性を保ったままマージする趣旨が示されている。投稿内の1920×1088可否や元の具体的なworkflowは、この実験では独立に再現していない。

実装READMEが推奨する、`context_length=22`、`encode_mode=video`、`anchor_mode=head`、`audio_mode=timeline`、`audio_context_length=22`、Trimの`match_tail=true`を採用した。セグメント間の音声継続に使うため、`Save Latent`/`Load Latent`によるvideo/audio latent経路も使っている。

## 実装変更

Docker build argにMotion Contextのcommit SHAを追加し、イメージbuild時にカスタムノードを導入した。

- `Dockerfile`: `H3_MOTION_CONTEXT_REF=15fc6a7bf7b78efb27f33d7eef3818e7ed0e118a`
- `compose.yaml`: 同じrevisionをbuild argとして渡す
- コンテナ内: `/opt/ComfyUI/custom_nodes/ComfyUI-H3-Motion-Context`
- 再利用用workflow generator: [`scripts/build-h3-motion-context-workflows.py`](../../../scripts/build-h3-motion-context-workflows.py)

コンテナ起動時には、次の自己検査ログを確認した。

```text
h3_motion_context: interior keyframe anchors enabled
h3_motion_context: keyframe/ref coexistence enabled
```

node smoke testも実施した。

```text
uv run --with numpy python tests/_mock_harness.py       # all checks passed
uv run --with numpy python tests/_node_smoke_test.py    # smoke test passed
```

## 再現環境

### ホスト

| 項目 | 値 |
|---|---|
| OS実行基盤 | Windowsホスト + WSL2 Ubuntu |
| WSL kernel | `6.6.114.1-microsoft-standard-WSL2` |
| Docker Engine | `29.4.3` |
| Docker Compose | `v5.1.3` |
| NVIDIA driver | `591.86` |
| 使用GPU | NVIDIA GeForce RTX 4090 |
| GPU UUID | `GPU-f877fbc1-9f24-bd97-3359-dd358eaa2caa` |
| GPUメモリ | `24564 MiB` |

### Docker / ComfyUI

| 項目 | 値 |
|---|---|
| Compose service | `h3-4090` |
| endpoint | `http://127.0.0.1:8188` |
| image | `local/minimax-h3-comfyui:v0.30.0` |
| image digest | `sha256:8611a4bdaf00f565811cde2fd9d9e04fa0ad7648ce819111ae1d1573f55bff60` |
| ComfyUI | `0.30.0` |
| Python | `3.12.3` |
| PyTorch | `2.11.0+cu130` |
| 起動引数 | `--disable-pinned-memory --disable-async-offload --fp16-intermediates --preview-method none` |
| input mount | `./runtime/4090/input:/opt/ComfyUI/input` |
| output mount | `./runtime/4090/output:/opt/ComfyUI/output` |

使用モデルはリポジトリの`models/`から読み込んだ。

- diffusion: `minimax_h3_fl2va_pruned_int8_convrot.safetensors`
- text encoder: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- video VAE: `minimax_h3_video_vae_fp16.safetensors`
- audio VAE: `minimax_h3_audio_vae_fp32.safetensors`

## 固定条件

元投稿の厳密なworkflowが公開されていないため、今回の条件を明示的に固定した。

| 項目 | 設定 |
|---|---|
| mode | T2V（リファレンス画像なし） |
| 解像度 | `1280×704` |
| FPS | `24` |
| steps | `20` |
| sampler | `res_multistep` |
| scheduler | `simple` |
| denoise | `1.0` |
| seed | `2026080909`（3セグメント共通） |
| Motion Context | `context_length=22` |
| video encode | `encode_mode=video` |
| anchor | `anchor_mode=head` |
| audio | `audio_mode=timeline`、`audio_context_length=22` |
| Trim | `match_tail=true`、`fps=24` |
| context latent | セグメント1→2→3で`Save Latent`/`Load Latent` |
| Attention | `sageattn_qk_int8_pv_fp16_cuda`、`allow_compile=false` |
| EasyCache | 無効 |
| Sol-Attn | 無効 |
| Spectrum | 無効 |

EasyCache、Sol-Attn、Spectrumは速度比較ではなくMotion Contextの連続性を分離検証するため無効にした。直前のref2va高速化実験で安定していた汎用FP16 CUDA SageAttentionだけを残した。

## セグメント設計

元投稿の「約5秒、約5秒、約6秒」と、約1秒の重複コンテキストを再現するため、セグメント2・3は生成後に22フレーム（`22/24=0.9167秒`）をTrimした。

| segment | raw frames | raw seconds | context | trimmed output | output seconds | prompt ID | ComfyUI wall time |
|---:|---:|---:|---:|---:|---:|---|---:|
| 1 | 124 | 5.1667 | 0 | 124 frames | 5.167 | `366eb6a1-61b4-4790-ada2-e47c027fa843` | 555.138 sec |
| 2 | 124 | 5.1667 | 22 frames | 102 frames | 4.250 | `c0ec519b-466d-43d8-a429-68206823879b` | 438.387 sec |
| 3 | 141 | 5.8750 | 22 frames | 119 frames | 4.959 | `58dfc329-ae61-420c-8beb-e414a1732ccb` | 493.080 sec |

生成処理時間の合計は`1486.605秒`（24分46.605秒、セグメント間のqueue投入待ち時間を除く）。3本のtrim済み出力をffmpegのconcat filterで再エンコードし、確認用の連結動画を作成した。連結結果は`345 frames / 14.4167 sec / 1280×704 / 24fps`である。

### Prompt

#### Segment 1

```text
A cinematic live-action shot in a warm Japanese cafe at night. A young woman in a floral dress walks slowly between wooden tables while the camera tracks backward at eye level. Natural cafe ambience, soft music, subtle conversations and room tone, realistic motion, consistent lighting, no dialogue, no text, no subtitles.
```

#### Segment 2

```text
Continue directly from the previous clip with the exact same woman, cafe, lighting, camera direction and soundtrack. She keeps walking forward between the tables, passing a waiter and turning slightly toward the counter. Preserve continuous body motion, tempo and audio without a reset, realistic live-action cinematography, no dialogue, no text, no subtitles.
```

#### Segment 3

```text
Continue directly from the previous clip with no visible reset. The same woman reaches the cafe counter, slows, and looks toward the warm window while the camera eases to a gentle stop. Preserve the exact motion direction, ambience, music waveform and lighting across the join, realistic live-action cinematography, no dialogue, no text, no subtitles.
```

## 生成物と検査結果

### Segment output

| segment | output | video/audio | size | SHA-256 |
|---:|---|---|---:|---|
| 1 | `runtime/4090/output/video/h3_motion_context/segment_01_00001_.mp4` | H.264 / AAC 32kHz stereo, 1280×704, 124 frames | 1,362,144 bytes | `23C3D5A200CE954080E9CB04E409FA43B30300DB84B37A2EAA44149FDEDEC7AE` |
| 2 | `runtime/4090/output/video/h3_motion_context/segment_02_00001_.mp4` | H.264 / AAC 32kHz stereo, 1280×704, 102 frames | 1,239,950 bytes | `31FEEBD5B08F1ADBA59DF41F3FDD49B0A86E237819FDE34174C6D9594528B64D` |
| 3 | `runtime/4090/output/video/h3_motion_context/segment_03_00001_.mp4` | H.264 / AAC 32kHz stereo, 1280×704, 119 frames | 1,148,458 bytes | `870788B9C68B4D80D314AB374E6348B34C63A408CEBFA7C936CFB9310E5CC93F` |

対応するlatentは次の場所に保存された。

```text
runtime/4090/output/h3_context/clip_00001.safetensors  12,556,248 bytes
runtime/4090/output/h3_context/clip_00002.safetensors  12,556,248 bytes
runtime/4090/output/h3_context/clip_00003.safetensors  14,253,016 bytes
```

### 連結確認用動画

- [3セグメント連結動画](./outputs/h3_motion_context_3segment_merged.mp4)
- ファイル: `outputs/h3_motion_context_3segment_merged.mp4`
- ffmpeg: concat filter、`libx264 -crf 18`、AAC `192k`、`+faststart`
- 出力: `1280×704 / 24fps / 345 frames / 14.4167 sec / 5,349,778 bytes`
- SHA-256: `24EAAF2B1F5F9965BD4FD887FBA1BF8CA4675A0E0EE53F6543E28996760D8598`

### 自動検査

- ComfyUI history: 3/3 `success`
- node error: なし
- OOM / CUDA runtime error: なし
- `blackdetect=d=0.25:pic_th=0.98`: 3本とも黒画区間なし
- 3本ともH.264/AACの音声付き
- Motion Contextログ: segment 2の音声ドリフト`0.00ms`、segment 3の音声ドリフト`0.01ms`
- Trimログ: segment 2で267 samples（8.34ms）を末尾調整し、102 framesと音声を一致
- 目視: 女性、花柄の服、店内照明、カメラの進行方向を維持し、segment 3ではカウンターへ到達する流れを確認

実装リポジトリ付属の`seam_probe.py`は、次セグメントのTrim前音声を別Save Audioで保存することを前提としている。今回のworkflowでは最終出力音声だけを保存したため、厳密な「Aの末尾とBのTrim前先頭」の相互相関測定は未実施とした。次回はTrim前音声を分岐保存して、READMEの`seam_probe`条件で測定する。

## 再現手順

リポジトリルートを`D:/Prj/minimax-h3-compose`とする。

```powershell
docker compose --profile 4090 build h3-4090
docker compose --profile 4090 up -d h3-4090

python scripts/build-h3-motion-context-workflows.py `
  --output-dir experiments/05-temporal-continuity/motion-context-3segment/workflows
```

各API workflowはComfyUIの`/prompt`へ、トップレベルに`prompt`を付けて投入する。

```powershell
$workflow = Get-Content -Raw experiments/05-temporal-continuity/motion-context-3segment/workflows/segment_01_api.json | ConvertFrom-Json
$body = @{ prompt = $workflow } | ConvertTo-Json -Depth 100 -Compress
Invoke-RestMethod -Uri http://127.0.0.1:8188/prompt `
  -Method Post -ContentType application/json -Body $body
```

segment 1の出力を次の名前でinputへコピーしてからsegment 2を投入する。segment 2の出力も同様にコピーしてからsegment 3を投入する。

```text
runtime/4090/input/h3_motion_context/segment_01.mp4
runtime/4090/input/h3_motion_context/segment_02.mp4
```

workflow内の`LoadVideo`はコンテナ内の`/opt/ComfyUI/input`から相対パスを解決する。`h3_context/clip_00001.safetensors`と`clip_00002.safetensors`は、同じコンテナの`/opt/ComfyUI/output`に保存されている必要がある。

## 解釈と残課題

今回の結果から、Docker Composeで再利用できる形のH3 Motion Context実装、video/audio latentの受け渡し、約1秒の重複生成とTrim、音声付き3セグメント連結は確認できた。4090ではこの条件でOOMも発生しなかった。

一方、次は未検証である。

- 元投稿と同一のprompt、seed、workflow、モデルrevision
- 1920×1088での生成可否
- 投稿にある速度向上率や、単発生成との画質差
- Trim前音声を使った`seam_probe.py`の相互相関
- 人物同一性・音声継続性の定量評価
- RTX 3060での同一3セグメント条件

したがって、今回の判定は「4090・1280×704でMotion Contextの3段連鎖が再現可能」であり、「元投稿の1920×1088や性能主張を完全再現した」ではない。
