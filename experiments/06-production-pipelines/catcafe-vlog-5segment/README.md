# MiniMax-H3 日本語猫カフェVlog — 5セグメント Motion Context実験

実施日: 2026-08-09 JST
Experiment ID: `h3-japanese-catcafe-vlog-5segment`
状態: `verified`

## 結論

英語の生成プロンプトに、日本語で話すセリフを直接含めてMiniMax-H3を実行した。猫カフェを訪れる日本人インフルエンサー風のVlogを5セグメントに分け、`ComfyUI-H3-Motion-Context`で映像・音声コンテキストとlatentを引き継いで連結した。

- 5/5セグメントがComfyUI history `success`
- 連結結果: `1280×704`、`24fps`、`702 frames`、`29.256秒`
- 各セグメントにAAC音声あり（`32kHz / stereo`）
- `blackdetect`で黒画区間なし
- この実行ではOOM・CUDA runtime errorなし
- 生成処理時間合計: `2687.899秒`（44分47.899秒）

最終動画:

- [h3_cat_cafe_vlog_5segment_merged.mp4](./outputs/h3_cat_cafe_vlog_5segment_merged.mp4)
- SHA-256: `73200CA4577C710BCADB41FD23451EBE01BDDE3E30D8E4E3A734F5A9A88E10DC`

今回の要件は「セリフを日本語、プロンプトは英語」と解釈した。プロンプトのHTTP送信はUTF-8 bytesで行い、日本語文字が`?`へ置換されないことも確認した。なお、音声の日本語発音・内容をASRで文字起こしして照合する検査はまだ実施していない。目視したサンプルでは、プロンプトに「字幕なし」と書いたにもかかわらず、日本語のキャプション風テキストが一部フレームに自動生成された。この点はモデル側の副作用として記録する。

## 実験目的と構成

### 目的

日本語のセリフを含む、約30秒の猫カフェVlogを、5本の短い生成結果から自然につなげられるか確認する。人物・服装・声・猫・店内をプロンプトで固定し、2本目以降は直前セグメントの映像コンテキスト、音声コンテキスト、保存済みlatentを渡した。

### セグメント設計

各セグメントは158フレーム（`158 / 24 = 6.583秒`）で生成した。セグメント2〜5は先頭22フレーム（`22 / 24 = 0.9167秒`）をコンテキストとして重複させ、生成後にTrimした。したがって、出力の合計は次の計算になる。

```text
158 + 4 × (158 - 22) = 702 frames
702 / 24 = 29.25 seconds（実測29.256秒）
```

| segment | 内容 | raw frames | context | 出力frames | 出力秒数 | 処理時間 |
|---:|---|---:|---:|---:|---:|---:|
| 1 | 入店前の導入 | 158 | 0 | 158 | 6.583 | 464.903秒 |
| 2 | 猫が出迎える | 158 | 22 | 136 | 5.667 | 556.262秒 |
| 3 | 猫を撫でる・ゴロゴロ音 | 158 | 22 | 136 | 5.667 | 555.960秒 |
| 4 | おやつタイム | 158 | 22 | 136 | 5.667 | 556.361秒 |
| 5 | 退店前の締め | 158 | 22 | 136 | 5.667 | 554.413秒 |
| **合計** |  |  |  | **702** | **29.256** | **2687.899秒** |

## 再現環境

### ホスト

| 項目 | 値 |
|---|---|
| OS実行基盤 | Windowsホスト + WSL2 Ubuntu |
| WSL kernel | `6.6.114.1-microsoft-standard-WSL2` |
| Docker Engine | `29.4.3` |
| Docker Compose | `v5.1.3` |
| GPU | NVIDIA GeForce RTX 4090 |
| GPU UUID | `GPU-f877fbc1-9f24-bd97-3359-dd358eaa2caa` |
| NVIDIA driver | `591.86` |
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

### 使用モデル

- diffusion: `minimax_h3_fl2va_pruned_int8_convrot.safetensors`
- text encoder: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- video VAE: `minimax_h3_video_vae_fp16.safetensors`
- audio VAE: `minimax_h3_audio_vae_fp32.safetensors`

### 実装revision

- Motion Context: `15fc6a7bf7b78efb27f33d7eef3818e7ed0e118a`
- 元実験: [`niko-h3-motion-context-3segment`](../../05-temporal-continuity/motion-context-3segment/README.md)
- workflow生成: [`scripts/build-h3-catcafe-vlog-workflows.py`](../../../scripts/build-h3-catcafe-vlog-workflows.py)
- 実行runner: [`scripts/run-h3-catcafe-vlog.ps1`](../../../scripts/run-h3-catcafe-vlog.ps1)
- 連結・検査: [`scripts/merge-h3-catcafe-vlog.ps1`](../../../scripts/merge-h3-catcafe-vlog.ps1)

## 固定条件

| 項目 | 設定 |
|---|---|
| mode | T2V（リファレンス画像なし） |
| 解像度 | `1280×704`（約720p相当） |
| FPS | `24` |
| steps | `20` |
| sampler | `res_multistep` |
| scheduler | `simple` |
| denoise | `1.0` |
| seed | `2026080910`（全セグメント共通） |
| Motion Context | `context_length=22` |
| audio context | `audio_context_length=22`、`audio_mode=timeline` |
| video encode | `encode_mode=video` |
| anchor | `anchor_mode=head` |
| Trim | `match_tail=true`、`fps=24` |
| Attention | `sageattn_qk_int8_pv_fp16_cuda`、`allow_compile=false` |
| EasyCache | 無効 |
| Sol-Attn | 無効 |
| Spectrum | 無効 |

今回はMotion Contextの連続性を単独で確認するため、EasyCache・Sol-Attn・Spectrumは有効化していない。SageAttentionも汎用FP16 CUDA設定だけに固定した。

## プロンプト（英語）と日本語セリフ

下記がAPIへ渡した全文である。実験の再現時は、`segment_01_api.json`〜`segment_05_api.json`をそのまま使用できる。

### Segment 1

```text
A realistic handheld Japanese lifestyle vlog at a cozy Tokyo cat cafe in the late afternoon. A cheerful Japanese woman in her mid-20s is a non-specific social-media influencer, with shoulder-length warm brown hair, a cream cardigan over a pastel blue T-shirt, a small cat-shaped tote bag, and natural makeup. Keep her identity, outfit, voice, camera style and color grade consistent across every segment. She films herself at arm's length with a phone-sized vlog camera, then turns toward the cafe entrance. Warm wood, soft window light, several calm cats, realistic handheld motion, natural room tone, soft royalty-free acoustic background music. She smiles and speaks naturally in Japanese: 「今日は東京の猫カフェに来ました！たっぷり癒やされてきます」. Preserve clear Japanese speech, no subtitles, no on-screen text, no logos.
```

### Segment 2

```text
Continue directly from the previous cat-cafe vlog clip with the exact same Japanese woman, warm brown hair, cream cardigan, pastel blue T-shirt, tote bag, voice, handheld camera and late-afternoon lighting. She enters the same Tokyo cat cafe, sanitizes her hands, and a friendly orange tabby cat with white paws and a small blue collar walks up to greet her. The camera follows from selfie view to a gentle over-the-shoulder view. Keep the same room layout, acoustic music, cafe ambience and natural handheld rhythm with no visible reset. She speaks naturally in Japanese: 「入ってすぐ、この子が来てくれた！めちゃくちゃ人懐っこい」. Include soft cat meows and purring, clear Japanese speech, no subtitles, no on-screen text, no logos.
```

### Segment 3

```text
Continue directly from the previous clip with no reset. The same Japanese influencer, outfit, voice, orange tabby cat with white paws and blue collar, Tokyo cat cafe, warm wood interior, window light, handheld phone-vlog camera and acoustic background music remain consistent. She sits on a low sofa and slowly pets the tabby while the camera moves into a close but natural selfie-and-cat shot. The cat relaxes and purrs, its tail moving gently. Preserve continuous body motion, realistic fur, stable face and matching room tone. She whispers happily in Japanese: 「見て、このゴロゴロ音。かわいすぎて動けない」. Keep Japanese speech understandable, include purring and soft cafe ambience, no subtitles, no on-screen text, no logos.
```

### Segment 4

```text
Continue seamlessly from the previous cat-cafe vlog segment with the same Japanese woman, same clothes, same voice, same orange tabby cat with white paws and blue collar, same warm Tokyo cafe and handheld camera. A staff member offers a small cat treat. The influencer holds it carefully and the tabby eats from her hand; she laughs softly while the camera makes a small playful push-in. Keep the background music, lighting, room tone, cat behavior and vlog color grade continuous, with realistic hands and natural motion. She says in Japanese: 「おやつタイムです。食べ方までかわいいんだけど！」. Include a quiet laugh, tiny cat sounds and clear Japanese speech, no subtitles, no on-screen text, no logos.
```

### Segment 5

```text
Continue directly from the previous clip and finish the same Japanese influencer cat-cafe vlog without a visible reset. Keep the exact same woman, warm brown hair, cream cardigan, pastel blue T-shirt, tote bag, voice, orange tabby cat with white paws and blue collar, warm window light, cafe ambience and handheld phone camera. She plays briefly with a feather toy, then returns to selfie view near the entrance as the cat sits beside her. She waves to the camera, smiles with a relaxed satisfied expression, and the camera gently pulls back. Preserve continuous acoustic music and natural room tone. She gives a friendly Japanese outro: 「今日は本当に癒やされました。またこの子に会いに来ます！」. End with soft purring and a natural handheld stop, clear Japanese speech, no subtitles, no on-screen text, no logos.
```

## 実行手順

リポジトリルートは `D:/Prj/minimax-h3-compose` とする。

### 1. Docker Composeを起動

```powershell
cd D:/Prj/minimax-h3-compose
docker compose --profile 4090 up -d --build h3-4090
```

ヘルスチェック確認:

```powershell
Invoke-RestMethod http://127.0.0.1:8188/system_stats
```

### 2. API workflowを生成

```powershell
uv run python scripts/build-h3-catcafe-vlog-workflows.py `
  --output-dir experiments/06-production-pipelines/catcafe-vlog-5segment
```

生成物は `segment_01_api.json`〜`segment_05_api.json` と `manifest.json` である。

### 3. 5セグメントを順番に実行

```powershell
.\scripts\run-h3-catcafe-vlog.ps1 `
  -Port 8188 `
  -StartSegment 1 `
  -TimeoutSeconds 7200
```

runnerは各segmentをComfyUI `/prompt`へ投入し、前segmentの出力を次segmentのinputへコピーする。HTTP bodyはUTF-8 bytesで送信するため、日本語セリフを含むプロンプトをWindows PowerShellから再現できる。途中からの再開は `-StartSegment 2`〜`-StartSegment 5` を指定する。処理時間・prompt ID・ffprobe・blackdetect・SHA-256は、実験ディレクトリの `run-progress.json` に保存される。

### 4. 連結と検査

```powershell
.\scripts\merge-h3-catcafe-vlog.ps1
```

出力先は `outputs/h3_cat_cafe_vlog_5segment_merged.mp4`、連結結果の検査記録は `merge.json` である。

## 出力と検査結果

### セグメント出力

| segment | ComfyUI prompt ID | 出力 | frames / duration | bytes | SHA-256 | blackdetect |
|---:|---|---|---:|---:|---|---:|
| 1 | `40bc8f28-fcf9-41ec-9f5c-a98f71ad7b3d` | `runtime/4090/output/video/h3_cat_cafe_vlog/segment_01_00001_.mp4` | 158 / 6.583008秒 | 1,813,877 | `3111BD6478094C1015C01691D7C485C0A59E42E1B244E838075BA0E9BB74D4F8` | 0 |
| 2 | `9ea36b47-769b-45d1-a38b-8d412509e69b` | `runtime/4090/output/video/h3_cat_cafe_vlog/segment_02_00001_.mp4` | 136 / 5.666667秒 | 1,866,529 | `F093788DD228F68802F8AD3F86F5EF0243EC4E91B63C7514CB11F483FBDF5A24` | 0 |
| 3 | `6095947a-5701-443c-9ceb-184e38a992fb` | `runtime/4090/output/video/h3_cat_cafe_vlog/segment_03_00001_.mp4` | 136 / 5.666667秒 | 1,413,609 | `D013D2D26EBD9AFC585139D0DB918BC42187F2F0296A5EBA391615E6D01BB97C` | 0 |
| 4 | `28ac5017-3a0e-468f-a6b1-3b5d07d1d8b2` | `runtime/4090/output/video/h3_cat_cafe_vlog/segment_04_00001_.mp4` | 136 / 5.666667秒 | 1,282,981 | `F741DAA70C7FE69B399026EB353F8115057D30E002284C41AC9DD32AD5918761` | 0 |
| 5 | `32ecf88e-b487-45bc-a762-aac7486ded7f` | `runtime/4090/output/video/h3_cat_cafe_vlog/segment_05_00001_.mp4` | 136 / 5.666667秒 | 1,252,937 | `E271965D47915F2868172E69AF326DCE6F497D45BB253B885A8C5983E0C7F4E9` | 0 |

全セグメントが `H.264 / AAC`、`1280×704 / 24fps`、音声 `32kHz stereo` である。

### 連結出力

| 項目 | 値 |
|---|---|
| path | `outputs/h3_cat_cafe_vlog_5segment_merged.mp4` |
| method | ffmpeg concat filter; `libx264 -crf 18`; AAC `192k`; `+faststart` |
| video | H.264、`1280×704`、`702 frames`、`24fps` |
| audio | AAC、`32kHz stereo` |
| duration | `29.256秒` |
| bytes | `11,404,834` |
| SHA-256 | `73200CA4577C710BCADB41FD23451EBE01BDDE3E30D8E4E3A734F5A9A88E10DC` |
| blackdetect | 0 interval |

### 目視確認

抽出フレームは `frames/frame-00.png`、`frame-07.png`、`frame-14.png`、`frame-21.png`、`frame-28.png` に保存した。女性の服装・髪色・猫カフェの暖色系の雰囲気は全体を通して維持され、猫との接触、撫でる、おやつ、締めの自撮りという流れを確認した。

一方、`frame-14`、`frame-21`、`frame-28`では、プロンプトの「no subtitles / no on-screen text」に反して、セリフに対応する日本語キャプション風文字が生成された。これは字幕を意図した追加編集ではなく、H3生成結果に含まれたものとして記録する。

## 限界と次の確認

- 日本語の音声が指定セリフどおり発話されたかは、ASRによる独立照合が未実施。
- 生成モデルが出した日本語文字の誤字・文脈整合性は、字幕品質としては未評価。
- 連結のフレーム数・音声ストリーム・黒画は検査済みだが、人物同一性や音声継続性の定量スコアは未取得。
- 今回はRTX 4090での実験。RTX 3060で同じ5セグメント・720p相当条件を実行した結果ではない。
- EasyCache、Sol-Attn、Spectrumの高速化比較は分離しており、今回の生成時間はMotion Context＋汎用SageAttentionの基準値。
