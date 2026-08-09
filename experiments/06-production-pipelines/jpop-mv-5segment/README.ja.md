# MiniMax-H3 日本語シンセポップMV — 音楽連動リリックモーション実験

English counterpart: [README.md](./README.md)

実施日: 2026-08-09 JST
Experiment ID: `h3-mv-jpop-5segment`
状態: `verified`

フレームタイル: [contact sheet](./previews/contact-sheet.jpg) / [manifest](./previews/contact-sheet.json)

Record: [experiment.json](./experiment.json) · [tracked frame tile](./previews/contact-sheet.jpg)

![Japanese synth-pop MV frame tile](./previews/contact-sheet.jpg)

> この追跡済みタイルで、H3生成映像とリリックモーションの時間変化を確認できます。動画本体はローカル成果物です。

## X動画・参照URL

- **完成動画投稿**: [X投稿](https://x.com/hAru_mAki_ch/status/2086334052639142176) — `uncertain`。投稿情報はあるが、公開X添付とこのローカル完成版（H3映像＋リリックモーション）の同一性・添付対応は未確認。
- **参照元**: [Motion Context実装](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context) / [3セグメント元投稿](https://x.com/photogenicweeke/status/2085848283138891926?s=46) / [HyperFrames registry](https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry) / [HyperFrames guide](https://hyperframes.heygen.com/llms.txt)
- **workflowと完成動画URLの対応**:

  | Workflow | Segment | X動画 |
  |---|---:|---|
  | [`segment_01`](./workflows/segment_01_api.json) | 1 | [完成動画のX投稿](https://x.com/hAru_mAki_ch/status/2086334052639142176)（添付対応未確認） |
  | [`segment_02`](./workflows/segment_02_api.json) | 2 | [完成動画のX投稿](https://x.com/hAru_mAki_ch/status/2086334052639142176)（添付対応未確認） |
  | [`segment_03`](./workflows/segment_03_api.json) | 3 | [完成動画のX投稿](https://x.com/hAru_mAki_ch/status/2086334052639142176)（添付対応未確認） |
  | [`segment_04`](./workflows/segment_04_api.json) | 4 | [完成動画のX投稿](https://x.com/hAru_mAki_ch/status/2086334052639142176)（添付対応未確認） |
  | [`segment_05`](./workflows/segment_05_api.json) | 5 | [完成動画のX投稿](https://x.com/hAru_mAki_ch/status/2086334052639142176)（添付対応未確認） |

## 結論

MiniMax-H3のMotion Context連鎖で、同じ歌い手・衣装・曲調を維持した5セグメントの日本語シンセポップMVを生成し、その生成音声を使ってHyperFramesでリリックモーションを重ねた。

- H3生成: 5セグメント、`1280×704 / 24fps / 20 steps`
- H3連結素材: `29.256秒`、H.264/AAC、映像702フレーム、音声32kHz stereo
- HyperFrames完成版: `1280×704 / 30fps / 878フレーム / 29.266667秒`
- 曲の音声はH3の生成音声をそのまま採用し、30fpsのRMS・16帯域FFTとビート解析をリリック演出へ利用
- 歌詞は5セグメントのプロンプトで指定した計画テキスト。音声が指定歌詞どおりかのASR照合は未実施
- 最終動画には、1文字ずつの出現、マスク・スイープ、ブラー解除、キネティックイン、拍に反応する微細なパルスを実装

完成動画:

- リリックモーション完成動画（local-only）: `hyperframes-mv-lyrics/renders/h3_jpop_mv_lyric_motion.mp4`。公開用の視覚確認は[フレームタイル](./previews/contact-sheet.jpg)を使用する。
- SHA-256: `097EBE221189EE2726319DDC555E57B813483BCA9FD48640E18E75830B179050`

H3のみの連結素材:

- H3連結素材（local-only）: `outputs/h3_jpop_mv_5segment_merged.mp4`。公開用の視覚確認は[フレームタイル](./previews/contact-sheet.jpg)を使用する。
- SHA-256: `28F1921260CF45A710E7C1BB8D64E72A91889379F0495C5BDB91217F2E6EF92E`

## 何を検証したか

今回の焦点は、単に5本の動画をつなぐことではなく、次の3つを一つのパイプラインで成立させることだった。

1. H3 Motion Contextで映像・音声・latentを次セグメントへ引き継ぐ
2. H3が生成した音声を曲のタイムラインとして解析する
3. 解析した音楽イベントに合わせて、日本語歌詞をMV風に動かす

映像のストーリーは、雨上がりの東京の屋上から階段、アンダーパス、歩道橋、夜明けの屋上へ移動する日本人女性シンガー。黒髪、銀色のヘアクリップ、黒いサテンジャケット、深紅のドレス、シルバーのイヤーカフを全セグメントで固定した。

## セグメント設計

各H3 workflowは158 raw framesで生成した。2本目以降は直前動画の先頭22フレームを映像・音声コンテキストとして渡し、`match_tail=true`で重複を除去した。

```text
158 + 4 × (158 - 22) = 702 frames
702 / 24fps = 約29.25秒
```

| Segment | シーン | 計画歌詞 | raw frames | context | 出力 frames | 出力秒数 | 生成時間 |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | 雨に濡れた屋上で歌い始める | 夜を越えて　光を探す | 158 | 0 | 158 | 6.583008 | 465.797秒 |
| 2 | ネオン階段から路地へ降りる | 君となら　まだ飛べる | 158 | 22 | 136 | 5.666667 | 553.979秒 |
| 3 | 赤と金の光が走るアンダーパス | 雨の向こう　夢が見える | 158 | 22 | 136 | 5.666667 | 553.619秒 |
| 4 | 都市を見下ろす歩道橋でパフォーマンス | この瞬間を　抱きしめて | 158 | 22 | 136 | 5.666667 | 552.608秒 |
| 5 | 雨が上がり、夜明けの屋上へ戻る | 明日へ行こう　また会おう | 158 | 22 | 136 | 5.666667 | 555.882秒 |
| **合計** |  |  |  |  | **702** | **29.256** | **2681.885秒** |

生成時間の合計はComfyUIの各segment実行時間の合算で、HyperFramesの音楽解析・レンダー時間は含めない。

## 音楽解析とリリックモーション

### H3音声

H3連結動画から音声を抽出し、HyperFramesの入力音源として使用した。

| 項目 | 値 |
|---|---|
| 音源 | H3生成音声（外部BGMへの差し替えなし） |
| 抽出ファイル | `assets/bgm.mp3` |
| duration | `29.255969秒`（入力音声） |
| sample rate | `32000Hz / stereo` |
| SHA-256 | `D2895A21CBBDA95E3D0C8C76A7B4DC302D1EA3B7D4B7AD84D50EE57033094E48` |

### 解析結果

`audiomap.json`は、音源に対してテンポ・拍・小節・イベント密度・エネルギー区間を整理したもの。`audio-data.json`は、30fpsの各フレームに対応するRMSと16帯域の正規化FFTデータである。

- 推定テンポ: `123 BPM`
- 拍子: 4/4
- 拍数: 56
- 小節数: 14
- 検出イベント: 146（kick 38 / snare 60 / hihat 42 / perc 6）
- ロール: 11
- エネルギー区間: 8
- FFT: 16 bands、30fps、877フレーム

歌詞モーションは、各フレームの音量・帯域エネルギーをCSS変数へ供給し、演出の強さだけを制御した。汎用的なイコライザーバーを画面に置くのではなく、次のようにMVの画面構成へ統合している。

| セグメント | リリック演出 | 動きの狙い |
|---:|---|---|
| 1 | typewriter + stagger + neon flicker | 最初の歌詞を一文字ずつ導入し、最初のグルーヴへ接続 |
| 2 | sideways sweep + mask reveal + overlay pop | 移動ショットに合わせて歌詞を横へ流す |
| 3 | blur resolve + kinetic letter-in + negative-space hold | 低域が残る区間で歌詞を中央に保持 |
| 4 | kinetic letter-in + stagger + overlay pop | パフォーマンスのピークに文字を強く出す |
| 5 | blur resolve + stagger + negative-space hold | 夜明けの余韻に合わせて広がりながら解決 |

## 再現環境

### ホスト

| 項目 | 値 |
|---|---|
| 実行基盤 | Windowsホスト + WSL2 Ubuntu |
| WSL distribution | Ubuntu、WSL version 2 |
| Docker Engine | `29.4.3` |
| Docker Compose | `v5.1.3` |
| GPU | NVIDIA GeForce RTX 4090 |
| GPU UUID | `GPU-f877fbc1-9f24-bd97-3359-dd358eaa2caa` |
| NVIDIA driver | `591.86` |
| VRAM | `24564 MiB` |

HyperFramesのブラウザキャプチャはホスト側のRTX 3060をhardware GPUとして使用した。H3の生成自体はDocker Composeの`h3-4090`（RTX 4090）で実行しているため、2つのGPUの役割を混同しないこと。

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
| CUDA | `13.0` |
| ComfyUI args | `--listen 0.0.0.0 --port 8188 --disable-pinned-memory --disable-async-offload --fp16-intermediates --preview-method none` |
| runtime env | `H3_MEMORY_USAGE_FACTOR=1.0`, `CUDA_MODULE_LOADING=LAZY`, `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True` |
| input mount | `./runtime/4090/input:/opt/ComfyUI/input` |
| output mount | `./runtime/4090/output:/opt/ComfyUI/output` |
| model mount | `./models:/opt/ComfyUI/models:ro` |

### 使用モデルと実装

- diffusion: `models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors`（20,970,379,616 bytes）
- text encoder: `models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`（15,687,142,551 bytes）
- video VAE: `models/vae/minimax_h3_video_vae_fp16.safetensors`（5,207,808,496 bytes）
- audio VAE: `models/vae/minimax_h3_audio_vae_fp32.safetensors`（605,254,808 bytes）
- Motion Context custom node: `ComfyUI-H3-Motion-Context` revision `15fc6a7bf7b78efb27f33d7eef3818e7ed0e118a`
- SageAttention: 汎用FP16 CUDA経路 `sageattn_qk_int8_pv_fp16_cuda`
- EasyCache: 無効
- Sol-Attn: 無効
- Spectrum: 無効

Motion Contextの出典は[NikoDemon80/ComfyUI-H3-Motion-Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context)。Dockerへの組み込みrevisionとworkflowの全グラフは`workflows/manifest.json`および`segment_01_api.json`〜`segment_05_api.json`に固定している。

## H3固定条件

| 項目 | 設定 |
|---|---|
| mode | T2V（リファレンス画像なし） |
| resolution | `1280×704`（720p相当、32の倍数） |
| fps | `24` |
| raw frames / segment | `158` |
| steps | `20` |
| sampler | `res_multistep` |
| scheduler | `simple` |
| denoise | `1.0` |
| seed | `2026080911`（全segment共通） |
| context length | `22` |
| audio context length | `22` |
| encode mode | `video` |
| anchor | `head` |
| audio mode | `timeline` |
| trim | `match_tail=true` |
| attention | generic FP16 CUDA SageAttention only |

英語の映像プロンプトへ、日本語の歌唱指示を埋め込んだ。プロンプト全文は`workflows/manifest.json`が正本で、歌詞は次の5行である。なお、生成モデルが実際に発声した内容は、今回の検証ではASRで確認していない。

```text
Female Japanese vocals singing exactly 「夜を越えて　光を探す」
Female Japanese vocals sing exactly 「君となら　まだ飛べる」
Female Japanese vocals sing exactly 「雨の向こう　夢が見える」
Female Japanese vocals sing exactly 「この瞬間を　抱きしめて」
Female Japanese vocals sing exactly 「明日へ行こう　また会おう」
```

## HyperFrames固定条件

| 項目 | 設定 |
|---|---|
| project | `hyperframes-mv-lyrics` |
| HyperFrames | `0.7.102` |
| skill | `music-to-video` |
| creative preset | `broadside` |
| canvas | `1280×704` |
| render fps | `30` |
| render quality | `high` |
| frame count | `878` |
| video plate | `assets/h3_jpop_mv_5segment_keyint30.mp4` |
| audio | `assets/bgm.mp3` |
| lyric plan | `STORYBOARD.md` |
| audio map | `audiomap.json` / `assets/audio-data.json` |

HyperFramesへの入力プレートは、元の24fps連結動画を30fps・GOP30へ再エンコードした。HyperFramesの動画抽出時にランダムシークが発生するため、長いキーフレーム間隔のまま使わないようにしている。

```powershell
ffmpeg -y -hide_banner -loglevel error `
  -i outputs/h3_jpop_mv_5segment_merged.mp4 `
  -c:v libx264 -r 30 -g 30 -keyint_min 30 -sc_threshold 0 `
  -pix_fmt yuv420p -c:a copy -movflags +faststart `
  hyperframes-mv-lyrics/assets/h3_jpop_mv_5segment_keyint30.mp4
```

この中間ファイルのSHA-256は`CB375A6C1E0D783444D6725AA2C57C7CADD0F1BB23523BE7D843F1A6C26DCAA7`。

## 実行手順

リポジトリルートは`<repo-root>`とする。

### 1. Docker Composeを起動

```powershell
cd <repo-root>
docker compose --profile 4090 up -d h3-4090
Invoke-RestMethod http://127.0.0.1:8188/system_stats
```

### 2. H3 workflowを生成して5本を実行

```powershell
python scripts/build-h3-mv-workflows.py `
  --output-dir experiments/06-production-pipelines/jpop-mv-5segment/workflows

powershell -ExecutionPolicy Bypass -File scripts/run-h3-mv.ps1 `
  -Port 8188 `
  -TimeoutSeconds 7200

powershell -ExecutionPolicy Bypass -File scripts/merge-h3-mv.ps1
```

`run-h3-mv.ps1`は、各segmentをComfyUI APIへ投入し、前segmentの動画を次segmentの`runtime/4090/input/h3_mv`へコピーする。`run-progress.json`にはPrompt ID、ComfyUI実行時間、ffprobe、blackdetect、bytes、SHA-256が保存される。

### 3. HyperFrames projectを再生成・検査

初回だけ:

```powershell
npx hyperframes init `
  experiments/06-production-pipelines/jpop-mv-5segment/hyperframes-mv-lyrics `
  --non-interactive --example=blank --skill=music-to-video
```

その後、同梱済みの`frame.md`、`BRIEF.md`、`STORYBOARD.md`、`compositions/frames/*.html`、`assets/*`を使用する。

```powershell
python scripts/build-h3-mv-lyric-frames.py `
  --output-dir experiments/06-production-pipelines/jpop-mv-5segment/hyperframes-mv-lyrics/compositions/frames `
  --audio-data experiments/06-production-pipelines/jpop-mv-5segment/audio-data.json

node scripts/patch-h3-mv-hyperframes-index.mjs `
  experiments/06-production-pipelines/jpop-mv-5segment/hyperframes-mv-lyrics

cd experiments/06-production-pipelines/jpop-mv-5segment/hyperframes-mv-lyrics
npm install
npm run check -- --snapshots
npx hyperframes@0.7.102 render . `
  --skill=music-to-video --quality high `
  --output renders/h3_jpop_mv_lyric_motion.mp4 --fps 30
```

`npm run check -- --snapshots`の結果は、Lint、Runtime、Layout、Motion、WCAG AA contrastの全項目で問題なし。テキストのコントラスト検査は`64/64` passだった。

## 出力と検査結果

### H3 segment出力

| Segment | Prompt ID | path | bytes | SHA-256 | blackdetect |
|---:|---|---|---:|---|---:|
| 1 | `3efb7532-36e0-40b4-a2ff-0cb2da0cf610` | `runtime/4090/output/video/h3_mv/segment_01_00001_.mp4` | 1,530,760 | `0E49C3F87CD955FAD2E01059AE8EC86F2386D582368A952A0A9F5223508D5D96` | 0 |
| 2 | `335aedc6-8b92-4319-b75a-40e6ec0c476f` | `runtime/4090/output/video/h3_mv/segment_02_00001_.mp4` | 1,738,920 | `517FDF145AA5D2C2A71A598957B5702C4094765F6055D207A6B74167F2A254CF` | 0 |
| 3 | `89ebf33d-0f0e-48e3-b3c1-a268d6e5cb47` | `runtime/4090/output/video/h3_mv/segment_03_00001_.mp4` | 1,232,107 | `2856C6E0E1DC7C4889DF920FFE2E4E83B25490929186222C062D2E7AD50736E4` | 0 |
| 4 | `2562fdd9-8b43-423f-b86a-ac4594281ff0` | `runtime/4090/output/video/h3_mv/segment_04_00001_.mp4` | 1,258,854 | `31A121BC62C2EFA43C3E6FB969D07EF9990BCE2C998C2DB3BFFFF232AAC1CF21` | 0 |
| 5 | `3dbe432d-cf8f-42fa-8243-212ded5df970` | `runtime/4090/output/video/h3_mv/segment_05_00001_.mp4` | 1,170,175 | `F44334ADDB5F4103BB481638763D333EF4591D8FDC2EC8DDC546E6739541823E` | 0 |

全segmentはH.264/AAC、`1280×704 / 24fps`、音声`32000Hz stereo`である。ComfyUI history上は5本とも完了し、この実行でOOMやCUDA runtime errorは発生しなかった。

### H3連結

| 項目 | 値 |
|---|---|
| path | `outputs/h3_jpop_mv_5segment_merged.mp4` |
| method | ffmpeg concat filter、libx264 CRF18、AAC 192k、faststart |
| video | H.264、`1280×704`、702 frames、24fps |
| audio | AAC、32kHz stereo |
| duration | `29.256秒` |
| bytes | `10,104,411` |
| SHA-256 | `28F1921260CF45A710E7C1BB8D64E72A91889379F0495C5BDB91217F2E6EF92E` |

### HyperFrames完成版

| 項目 | 値 |
|---|---|
| path | `hyperframes-mv-lyrics/renders/h3_jpop_mv_lyric_motion.mp4` |
| video | H.264、`1280×704`、878 frames、30fps |
| audio | AAC、48kHz stereo（レンダー時に標準化） |
| duration | `29.266667秒` |
| bytes | `19,614,049` |
| SHA-256 | `097EBE221189EE2726319DDC555E57B813483BCA9FD48640E18E75830B179050` |
| blackdetect | 検出なし |
| freezedetect | 0.50秒以上の静止区間なし |

完成版から5秒ごとにフレームを抜いた確認用コンタクトシートは[`verification/h3_mv_contact.jpg`](./hyperframes-mv-lyrics/verification/h3_mv_contact.jpg)。5シーンの背景、歌い手、衣装、歌詞パネルが表示され、黒フレームや長いフレーム凍結は確認されなかった。

## 解釈と制限

今回確認できたのは、H3が生成した音声を別トラックへ置き換えずに、映像とリリック演出の共通タイムラインとして利用できること。音楽の低域・ビート・密度に合わせて文字の出現や保持の強さを変えると、単なる字幕よりMVらしい画面になる。

一方、次の点はまだ証明していない。

- 日本語の発音・歌詞がプロンプト指定どおりかというASR照合
- セグメント間の歌声・人物同一性・音楽シームの定量スコア
- RTX 3060での同じ5セグメント・720p相当条件
- EasyCache、Sol-Attn、Spectrumを有効化した場合の速度・音質差
- 元のH3音声の著作権・公開利用条件の確認

したがって、この結果は「音楽を含むH3生成素材へ、解析済みの音量・帯域・ビートを使ってリリックモーションを同期できた」という実験結果として扱う。歌詞の正確さを主張する場合は、次回ASR確認を追加する。

## 参照ファイル

- [workflows/manifest.json](./workflows/manifest.json): 全segmentの全文プロンプト、seed、Motion Context条件
- [run-progress.json](./run-progress.json): 実行時間、Prompt ID、出力検査
- [merge.json](./merge.json): H3連結のffprobe、SHA-256、blackdetect
- [audiomap.json](./audiomap.json): BPM、拍、小節、イベント、エネルギー区間
- [audio-data.json](./audio-data.json): 30fps RMS/16-band FFT
- [STORYBOARD.md](./hyperframes-mv-lyrics/STORYBOARD.md): 5フレームのタイムラインとモーション設計
- [BRIEF.md](./hyperframes-mv-lyrics/BRIEF.md): music-to-video brief
