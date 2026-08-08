# MiniMax-H3 Docker Compose

MiniMax-H3をComfyUIで起動し、RTX 4090とRTX 3060を別コンテナ・別ポートで再利用する構成です。GPUはUUIDで固定し、モデルはホストのmodels、生成物とComfyUI状態はGPU別のruntimeに保存します。

## Experiment Lab

このリポジトリは、MiniMax-H3の実験を蓄積するラボとして運用します。過去の3060／4090実験、Kijai／LightX2Vなどの派生モデル、今後の解像度・LoRA・GPU比較を、出典・条件・workflow・生成物・検証結果と一緒に保存します。

- [ラボ運用ガイド](./LAB.md)
- [実験台帳](./experiments/index.md)
- [新規実験テンプレート](./experiments/_template/README.md)

実験結果の正本は、GPU別の`runtime/*/benchmark`レポートと、実験単位の`experiments/YYYY-MM-DD/<slug>/`メタデータです。大きなモデルや生成物はGitへ直接コミットせず、取得元・revision・SHA-256・ローカル保存先を記録します。

## Kijai / LightX2V 4-step実験（2026-08-08）

[Kijai/MiniMax-H3_comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy)のLightX2V LoRAを、既存の4090 Composeサービスへmodel-onlyで接続して検証しました。X投稿の公開動画メタデータに合わせ、1344×768・24fps・158 frames（6.583秒）を固定し、4 steps・LoRA strength 0.75でT2V/I2Vを実行しています。

- T2V: `workflows/minimax_h3_kijai_lightx2v_4step_1344x768_er_sde_api.json`
- T2V: `workflows/minimax_h3_kijai_lightx2v_4step_1344x768_sa_solver_api.json`
- I2V: `workflows/minimax_h3_kijai_lightx2v_4step_1344x768_i2v_er_sde_api.json`
- I2V: `workflows/minimax_h3_kijai_lightx2v_4step_1344x768_i2v_sa_solver_api.json`

4本とも成功、OOMなし、`blackdetect=0`、H.264/AAC出力でした。4090の推論時間はT2Vが`er_sde 362.48秒 / sa_solver 196.25秒`、I2Vが`er_sde 210.05秒 / sa_solver 193.72秒`です。詳細な出典・条件・SHA-256・Prompt ID・目視確認は[実験記録](./experiments/2026-08-08/kijai-lightx2v-4step/README.md)と[JSON](./experiments/2026-08-08/kijai-lightx2v-4step/experiment.json)に保存しています。

## 先に結論: 3060の黒動画について

最初に作った3060動画は真っ黒でした。これは確認済みで、正しい成功結果ではありません。

黒になった経路は、次の古い別条件でした。

- Turbo/full-int8 base
- Kijaiのexperimental int8 video VAE
- 8 stepsのTurbo workflow

そのMP4をblackdetectとsignalstatsで確認すると、全フレームがY=16、U=128、V=128の黒信号でした。Kijai int8 VAEを使ったA/Bも黒になったため、この経路は最終構成から除外しました。

今回採用した公開3060投稿は、[TlanoAIのRTX 3060 12GB投稿](https://x.com/TlanoAI/status/2084940455809286397)です。X SearchをGrok Buildで調査し、ログイン済みブラウザでも本文を照合しました。正しい条件で再実行した3060 MP4は黒ではありません。

## Xで確認した条件

### RTX 3060: TlanoAI投稿

投稿に明記されている条件:

| 項目 | 投稿の値 |
|---|---|
| GPU | RTX 3060 12GB |
| Driver | 591.86 |
| ComfyUI | 0.30.0 |
| Python | 3.10.10 |
| PyTorch | 2.11.0+cu130 |
| CUDA / cuDNN | 13.0 / 9.19 |
| SageAttention | 2.2.0 |
| Triton | Windows 3.7.1.post27 |
| Base | minimax_h3_fl2va_pruned_int8_convrot.safetensors |
| Text encoder | qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors |
| Video VAE | minimax_h3_video_vae_fp16.safetensors |
| Audio VAE | minimax_h3_audio_vae_fp32.safetensors |
| VRAM運用 | Dynamic VRAM + CPU offload |
| EasyCache | reuse 0.300 / start 0.200 / end 0.900 |
| Attention | SageAttention |
| Preview | 無効 |
| T2V | 864×480 |
| 生成長 | 124 frames / 24fps / audioあり |
| steps | 25 |
| 投稿実測 | 初回436.18秒、warm351.53秒 |

投稿本文にLoRA、sampler、scheduler、seed、promptは明記されていません。workflowでは公式ComfyUIの標準的なres_multistep / simpleを採用し、seedとpromptは検証用に固定しています。これらを「投稿と同じ」とは扱いません。

### RTX 4090: yume投稿とリンク先recipe

参照元は[yume_arasakiの4090投稿](https://x.com/yume_arasaki/status/2084766655331360999)と、そこからリンクされた[GitHub recipe](https://github.com/yume-arasaki/RTX-4090-3090-Minimax-H3-15s)です。

- X本文: 約842×480、20 steps、24fps、5秒約7分、aggressive CPU offload
- recipe: 832×480、124 frames、20 steps、res_multistep / simple
- recipe: pruned int8、NVFP4 text encoder、公式FP16/FP32 VAE
- recipe: memory_usage_factor=1.0、--disable-pinned-memory、--fp16-intermediates

842×480と832×480は異なるため、4090の実測は「X本文の完全再現」ではなく「リンク先recipeの再現」と記録しています。

## Docker構成

- ComfyUI: v0.30.0
- Docker base: PyTorch 2.11.0 + CUDA 13.0 + cuDNN 9
- Linux container内Python: 3.12.3
- 3060: service h3-3060、host port 8189
- 4090: service h3-4090、host port 8188
- CUDA_MODULE_LOADING: LAZY
- 3060: Dynamic VRAMを既定のまま使用、--use-sage-attention
- 4090: H3_MEMORY_USAGE_FACTOR=1.0、--disable-pinned-memory、--fp16-intermediates
- 両方とも --preview-method none
- GPUはCUDA UUIDで個別割り当て

投稿はWindows環境ですが、Docker実測はLinuxコンテナです。Python、Triton、VAE実装のプラットフォーム差は残ります。PyTorch/CUDA/SageAttentionの主要版は3060投稿に合わせました。

必要な公式ファイルは約42.5GBです。

- models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors
- models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
- models/vae/minimax_h3_video_vae_fp16.safetensors
- models/vae/minimax_h3_audio_vae_fp32.safetensors

旧Turbo LoRA、full-int8 base、Kijai int8 VAEは、正しいTlanoAI条件では不要です。既にmodelsに残っていても、最終workflowからは参照しません。

## 起動

初回:

~~~powershell
cd D:/Prj/minimax-h3-compose
Copy-Item .env.example .env
docker compose --profile 3060 build h3-3060
docker compose --profile 4090 build h3-4090
docker compose --profile download run --rm model-downloader
~~~

3060だけ:

~~~powershell
docker compose --profile 3060 up -d h3-3060
docker compose logs -f h3-3060
~~~

4090だけ:

~~~powershell
docker compose --profile 4090 up -d h3-4090
docker compose logs -f h3-4090
~~~

2枚同時:

~~~powershell
docker compose --profile 3060 --profile 4090 up -d
docker compose ps
~~~

ブラウザ:

- 3060: http://localhost:8189
- 4090: http://localhost:8188

別PCでは.envのGPU_3060_UUIDとGPU_4090_UUIDをnvidia-smi -Lの値へ変更してください。

## 検証workflow

### 3060

workflows/tlanoai_3060_api.json

- 864×480、124 frames、24fps
- 25 steps
- res_multistep / simple
- pruned int8 base
- NVFP4 text encoder
- 公式FP16 video VAE / FP32 audio VAE
- EasyCache 0.300 / 0.200 / 0.900
- SageAttention
- Dynamic VRAM + CPU offload
- LoRAなし
- seedは実行時に変更可能

### 4090

workflows/yume_4090_recipe_api.json

- 832×480、124 frames、24fps
- 20 steps
- res_multistep / simple
- pruned int8 base
- NVFP4 text encoder
- 公式FP16 video VAE / FP32 audio VAE
- memory_usage_factor=1.0相当
- pinned memory無効、fp16 intermediates

### 約720p T2V / I2V

H3のwidth/height入力は32刻みなので、720p級として1280×704を使用します。4090と3060の両方で実測済みです。

- T2V: workflows/tlanoai_t2v_1280x704_api.json
- I2V: workflows/tlanoai_i2v_1280x704_api.json
- I2V開始画像: assets/i2v_start_frame_1280x704.png
- I2VはLoadImageからMiniMaxH3ImageToVideoのfirst_frameへ接続
- 3060 I2Vの864×480: workflows/tlanoai_i2v_864x480_api.json（実測済み）
- 3060の1280×704 T2V/I2V: WSL再起動後に実測済み。両方ともOOMなしで完走

実測:

| Mode | GPU | ComfyUI | runner wall | blackdetect |
|---|---|---:|---:|---:|
| T2V 1280×704 | RTX 4090 | 288.170秒 | 290.337秒 | 0 intervals |
| I2V 1280×704 | RTX 4090 | 274.210秒 | 275.309秒 | 0 intervals |
| I2V 864×480 | RTX 3060 | 374.240秒 | 375.399秒 | 0 intervals |
| T2V 1280×704 | RTX 3060 | 961.000秒 | 961.655秒 | 0 intervals |
| I2V 1280×704 | RTX 3060 | 796.000秒 | 800.840秒 | 0 intervals |

I2Vの開始画像はimagegenで生成した後、1280×704へ整形してruntime/4090/inputとruntime/3060/inputへコピーしています。別PCでは同じPNGを各GPUのruntime/GPU/inputへ置き、workflowのLoadImage filenameとSHA-256を一致させてください。

再現コマンド:

~~~powershell
.\scripts\run-h3-post-condition.ps1 -Gpu 4090 -Port 8188 -Workflow .\workflows\tlanoai_t2v_1280x704_api.json -OutputPrefix video/MiniMax_H3_T2V_4090_1280x704_25step_easycache_sage_cu130 -LowVram $false -Seed 2026080704 -TimeoutSeconds 14400

.\scripts\run-h3-post-condition.ps1 -Gpu 4090 -Port 8188 -Workflow .\workflows\tlanoai_i2v_1280x704_api.json -OutputPrefix video/MiniMax_H3_I2V_4090_1280x704_25step_easycache_sage_cu130 -LowVram $false -Seed 2026080705 -TimeoutSeconds 14400

.\scripts\run-h3-post-condition.ps1 -Gpu 3060 -Port 8189 -Workflow .\workflows\tlanoai_i2v_864x480_api.json -OutputPrefix video/MiniMax_H3_I2V_3060_864x480_25step_easycache_sage_cu130 -LowVram $true -Seed 2026080706 -TimeoutSeconds 14400

.\scripts\run-h3-post-condition.ps1 -Gpu 3060 -Port 8189 -Workflow .\workflows\tlanoai_t2v_1280x704_api.json -OutputPrefix video/MiniMax_H3_T2V_3060_1280x704_25step_easycache_sage_cu130_wsl_restart -LowVram $true -Seed 2026080707 -TimeoutSeconds 14400

.\scripts\run-h3-post-condition.ps1 -Gpu 3060 -Port 8189 -Workflow .\workflows\tlanoai_i2v_1280x704_api.json -OutputPrefix video/MiniMax_H3_I2V_3060_1280x704_25step_easycache_sage_cu130_wsl_restart -LowVram $true -Seed 2026080708 -TimeoutSeconds 14400
~~~

API実行と時間記録:

~~~powershell
.\scripts\run-h3-post-condition.ps1 -Gpu 3060 -Port 8189 -Workflow .\workflows\tlanoai_3060_api.json -OutputPrefix video/MiniMax_H3_TlanoAI_3060_864x480_25step_easycache_sage_repeat -Seed 2026080701

.\scripts\run-h3-post-condition.ps1 -Gpu 4090 -Port 8188 -Workflow .\workflows\yume_4090_recipe_api.json -OutputPrefix video/MiniMax_H3_4090_yume_recipe_832x480_20step_repeat -Seed 7
~~~

レポートはruntime/3060/benchmarkまたはruntime/4090/benchmarkに保存されます。wall time、ComfyUIのPrompt executed、prompt ID、status、条件、出力ファイルを保存します。

実験ごとに次の2ファイルを自動生成します。

- h3-PROMPT_ID.json: 機械可読な完全レポート
- h3-PROMPT_ID.md: 人が読む詳細レポート

同じフォルダのindex.mdから全実験を辿れます。Markdownには、開始・終了・wall time、workflow条件、実行パラメータ、ホストOS/PowerShell、Docker/Compose、GPU UUID・ドライバ、コンテナのComfyUI/Python/PyTorch/CUDAと起動引数、workflow/Docker関連ファイルのSHA-256、参照モデルとI2V入力画像のサイズ・SHA-256、ComfyUI history、ffprobe、blackdetect、signalstatsを保存します。別PCで再現するときは、この環境スナップショット、モデル、I2V入力画像を揃えてください。

記録のwall timeは、API投入からComfyUI historyがsuccess/errorになるまでの生成時間です。終了後のffprobe、黒判定、環境取得、モデルSHA-256計算にかかった記録処理時間はwall timeに混ぜません。

参照モデルのSHA-256計算を省略したい場合だけ、-SkipModelHashesを付けます。その場合、レポートに省略したことが明記されるため、完全再現用の記録には付けません。

## 実測結果 2026-08-07 JST

| GPU | 測定種別 | ComfyUI | runner wall | 出力 |
|---|---|---:|---:|---|
| RTX 3060 | TlanoAI条件 cold | 424.660秒 | 425.526秒 | 395,296 bytes |
| RTX 3060 | TlanoAI条件 warm inference | 267.980秒 | 270.289秒 | 463,849 bytes |
| RTX 3060 | cache/export only | 1.310秒 | 5.062秒 | 395,296 bytes |
| RTX 4090 | yume linked recipe | 253.970秒 | 255.350秒 | 547,652 bytes |
| RTX 4090 | T2V 1280×704 | 288.170秒 | 290.337秒 | 746,645 bytes |
| RTX 4090 | I2V 1280×704 | 274.210秒 | 275.309秒 | 1,098,548 bytes |
| RTX 3060 | I2V 864×480 | 374.240秒 | 375.399秒 | 683,339 bytes |
| RTX 3060 | T2V 1280×704 after WSL restart | 961.000秒 | 961.655秒 | 927,605 bytes |
| RTX 3060 | I2V 1280×704 after WSL restart | 796.000秒 | 800.840秒 | 1,569,004 bytes |

cache/export onlyはComfyUIのノードキャッシュからSaveVideoだけを実行した時間で、warm inferenceの生成時間には数えません。

検証したファイル:

- runtime/3060/output/video/MiniMax_H3_TlanoAI_3060_864x480_25step_easycache_sage_cold_cu130_00001_.mp4
- runtime/3060/output/video/MiniMax_H3_TlanoAI_3060_864x480_25step_easycache_sage_warm_inference_cu130_00001_.mp4
- runtime/4090/output/video/MiniMax_H3_4090_yume_recipe_832x480_20step_cu130_00001_.mp4
- runtime/4090/output/video/MiniMax_H3_T2V_4090_1280x704_25step_easycache_sage_cu130_00001_.mp4
- runtime/4090/output/video/MiniMax_H3_I2V_4090_1280x704_25step_easycache_sage_cu130_00001_.mp4
- runtime/3060/output/video/MiniMax_H3_I2V_3060_864x480_25step_easycache_sage_cu130_00001_.mp4
- runtime/3060/output/video/MiniMax_H3_T2V_3060_1280x704_25step_easycache_sage_cu130_wsl_restart_00001_.mp4
- runtime/3060/output/video/MiniMax_H3_I2V_3060_1280x704_25step_easycache_sage_cu130_wsl_restart_00001_.mp4

全検証動画はffprobeでH.264、24fps、124 frames、音声AAC 32000Hz stereo、duration約5.167秒を確認しました。blackdetectで黒区間は検出されず、signalstatsも通常の映像信号でした。3060の約720p T2V/I2Vはruntime/3060/output直下のh3_t2v_1280x704_wsl_restart_frame_*.pngおよびh3_i2v_1280x704_wsl_restart_frame_*.png、4090の約720p動画はruntime/4090/output直下のh3_t2v_1280x704_frame_2.5.pngおよびh3_i2v_1280x704_frame_*.pngで確認できます。

詳細なJSONはbenchmark-results-2026-08-07.json、時系列ログはverification-log.md、X調査の根拠はresearch-notes.mdです。

## 既知の失敗と再発防止

- 旧Turbo/full-int8 + Kijai int8 VAEの3060 MP4は黒。最終条件・最終workflowから除外。
- 旧DockerのPyTorch 2.7.1 + CUDA 12.8でTlanoAI workflowを試すと3060がCUDA OOM。投稿のPyTorch 2.11.0 + CUDA 13.0へ更新して再検証。
- 3060 workflowにTurbo LoRAが無い場合、runnerの-LowVram指定は実際のgraphへ適用されない。レポートにlow_vram_requestedとlow_vram_appliedを分けて記録。
- blackdetect、signalstats、ffprobe、抽出フレーム確認を成功条件に含める。
- 投稿にない項目を別投稿や古いworkflowから補完しない。

## 管理

~~~powershell
docker compose ps
docker compose logs --no-color h3-3060 | Select-String "Prompt executed"
docker compose logs --no-color h3-4090 | Select-String "Prompt executed"
docker compose stop h3-3060 h3-4090
docker compose down
~~~

modelsは読み取り専用マウント、runtimeはホスト保存なので、コンテナを再作成してもモデルと生成物は残ります。

## 参照

- [MiniMax-H3公式モデルカード](https://huggingface.co/MiniMaxAI/MiniMax-H3)
- [MiniMax-H3公式GitHub](https://github.com/MiniMax-AI/MiniMax-H3)
- [ComfyUI MiniMax-H3 docs](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)
- [SGLang MiniMax-H3 deployment guide](https://docs.sglang.io/cookbook/diffusion/MiniMax/MiniMax-H3)
- [MiniMax-H3 Turbo custom node](https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo)
- [Kijai MiniMax-H3 Comfy LoRA](https://huggingface.co/Kijai/MiniMax-H3_comfy)
- [参照したX投稿](https://x.com/sd_tutorial/status/2085760369612783646)
- [LightX2V upstream H3 Turbo](https://huggingface.co/lightx2v/Minimax-h3-Turbo/tree/main)
