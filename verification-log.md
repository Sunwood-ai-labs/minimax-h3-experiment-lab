# MiniMax-H3 検証ログ

検証日: 2026-08-07 JST
プロジェクト: D:/Prj/minimax-h3-compose

## 判定ルール

成功と判定するには、次をすべて確認する。

1. ComfyUI historyがsuccess
2. 出力MP4が存在
3. ffprobeで映像・音声・解像度・fps・frames・durationを確認
4. blackdetectで黒区間なし
5. signalstatsで全黒信号でないことを確認
6. 抽出フレームを目視確認
7. prompt ID、開始・終了、ComfyUI時間、runner wall timeをJSONへ保存

## 投稿条件

### 3060

参照: https://x.com/TlanoAI/status/2084940455809286397

既知値:

| 項目 | 値 |
|---|---|
| GPU | RTX 3060 12GB |
| ComfyUI | 0.30.0 |
| PyTorch / CUDA | 2.11.0+cu130 / 13.0 |
| SageAttention | 2.2.0 |
| Base | minimax_h3_fl2va_pruned_int8_convrot.safetensors |
| Text | qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors |
| Video VAE | minimax_h3_video_vae_fp16.safetensors |
| Audio VAE | minimax_h3_audio_vae_fp32.safetensors |
| 解像度 | 864×480 |
| frames / fps | 124 / 24 |
| steps | 25 |
| EasyCache | 0.300 / 0.200 / 0.900 |
| VRAM | Dynamic VRAM + CPU offload |
| Attention | SageAttention |

投稿にないsampler、scheduler、prompt、seed、LoRAは、検証側の値として別記録した。workflowではres_multistep / simple、LoRAなし、検証用promptを使用した。

### 4090

参照: https://x.com/yume_arasaki/status/2084766655331360999
recipe: https://github.com/yume-arasaki/RTX-4090-3090-Minimax-H3-15s

実測はX本文の842×480ではなく、リンク先recipeの832×480を使用した。

## 最初の3060黒動画: 失敗として確認

旧出力:

- 旧Turbo/full-int8 + Kijai int8 video VAE
- 8 steps、Turbo sampler
- 864×480、124 frames、24fps
- 生成物は黒

blackdetectとsignalstats:

- YMIN=16
- YAVG=16
- YMAX=16
- UAVG=128
- VAVG=128
- SATAVG=0

全フレームが黒信号なので、これは成功動画ではない。Kijai int8 VAEのA/Bも黒になった。公式FP16 video VAEへ切り替えたフレーム確認では映像が正常だった。

この旧経路は最終workflowと最終benchmarkから除外した。旧MP4は検証の失敗証拠としてruntime/3060/outputに残している。

## 3060正しい条件: 旧Dockerでの失敗

環境:

- PyTorch 2.7.1+cu128
- SageAttention cu128
- 正しいTlanoAI workflow
- Dynamic VRAM、SageAttention、公式FP16/FP32 VAE

prompt: 2f63426d-b983-49a4-975e-1530ff866c2f

- wall: 215.27秒
- ComfyUI: 211.64秒
- 結果: CUDA OOM
- 原因診断: 投稿のPyTorch 2.11.0+cu130と環境が不一致。ログにcu130以上が必要という警告。

この失敗後、Docker baseをPyTorch 2.11.0+CUDA 13.0+cuDNN 9へ更新した。

## 3060正しい条件: cold成功

workflow: workflows/tlanoai_3060_api.json

- prompt ID: 8934f550-30f1-4716-8b69-e743f6fab561
- start: 2026-08-07T17:54:42.0135415+09:00
- end: 2026-08-07T18:01:47.5398389+09:00
- runner wall: 425.526秒
- ComfyUI: 424.660秒
- status: success
- seed: 2026080701
- output: runtime/3060/output/video/MiniMax_H3_TlanoAI_3060_864x480_25step_easycache_sage_cold_cu130_00001_.mp4
- bytes: 395296

実行中の確認:

- 10023.80 MB usable、9312.86 MB loaded、5646.34 MB offloaded
- EasyCache: threshold 0.3、start 0.2、end 0.9
- sampler 25/25
- EasyCache: 12/25 steps skipped、1.92x speedup
- VAE output shape: (1,3,124,480,864)
- finite=True、min=-1、max=1

ffprobe:

- video: H.264、864×480、24fps、124 frames、5.166667秒
- audio: AAC、32000Hz、2ch、5.167秒

黒判定:

- blackdetect: 黒区間なし
- signalstats frame 0: YMIN10、YAVG111.41、YMAX235、UAVG118.206、VAVG133.442、SATAVG12.6579
- signalstats frame 62: YMIN14、YAVG110.377、YMAX236、UAVG119.595、VAVG132.208、SATAVG10.9856
- signalstats frame 123: YMIN10、YAVG107.996、YMAX235、UAVG121.15、VAVG130.632、SATAVG9.10696

抽出フレーム:

- runtime/3060/output/h3_3060_tlanoai_cu130_frame_0.5.png
- runtime/3060/output/h3_3060_tlanoai_cu130_frame_2.5.png
- runtime/3060/output/h3_3060_tlanoai_cu130_frame_4.5.png

湖、山、霧、朝日の映像を目視確認した。

## 3060 cache/export only

prompt ID: 19adb4fd-e0a5-43eb-96fc-a353ad91333f

- runner wall: 5.062秒
- ComfyUI: 1.310秒
- history: nodes 1-14 cached、SaveVideoだけ実行
- output: runtime/3060/output/video/MiniMax_H3_TlanoAI_3060_864x480_25step_easycache_sage_warm_cu130_00001_.mp4
- bytes: 395296

これは生成ではなくキャッシュ済み結果の書き出しなので、warm inference時間には含めない。

## 3060 warm inference成功

seedを2026080702へ変更し、モデル常駐後に25 stepsを再実行した。

- prompt ID: 6983bd5f-e393-4bd7-b5e5-8a4eabdf779e
- start: 2026-08-07T18:04:04.9450969+09:00
- end: 2026-08-07T18:08:35.2341018+09:00
- runner wall: 270.289秒
- ComfyUI: 267.980秒
- status: success
- output: runtime/3060/output/video/MiniMax_H3_TlanoAI_3060_864x480_25step_easycache_sage_warm_inference_cu130_00001_.mp4
- bytes: 463849

ffprobe:

- video: H.264、864×480、24fps、124 frames、5.166667秒
- audio: AAC、32000Hz、2ch、5.167秒

blackdetect: 黒区間なし。

signalstats:

- frame sample 1: YMIN13、YAVG108.721、YMAX197、UAVG117.302、VAVG139.324、SATAVG17.0382
- frame sample 2: YMIN16、YAVG108.314、YMAX236、UAVG110.528、VAVG144.121、SATAVG23.4019
- frame sample 3: YMIN18、YAVG118.448、YMAX242、UAVG112.21、VAVG141.579、SATAVG20.4783

runtime/3060/output/h3_3060_tlanoai_cu130_warm_frame_2.5.pngを目視し、正常な湖・山・霧・朝日の映像を確認した。

## 3060正しい条件: 自動Markdown記録の動作確認

同じTlanoAI workflowをseed 2026080703で再実行し、実験ごとのMarkdown自動保存まで確認した。

- prompt ID: 9e79a075-c9cd-495a-9d8d-80c4df520a1c
- start: 2026-08-07T18:38:14.9802680+09:00
- end: 2026-08-07T18:46:45.6504606+09:00
- runner wall: 510.670秒
- ComfyUI: 510.420秒
- status: success
- output: runtime/3060/output/video/MiniMax_H3_TlanoAI_3060_864x480_25step_easycache_sage_recorded_cu130_00001_.mp4
- bytes: 350422
- video: H.264、864×480、24fps、124 frames、5.166667秒
- audio: AAC、32000Hz、2ch、5.167秒
- blackdetect: 黒区間なし
- signalstats first frame: YMIN=19、YAVG=115.776、YMAX=220、UAVG=123.812、VAVG=130.074、SATAVG=11.9656
- Markdown: runtime/3060/benchmark/h3-9e79a075-c9cd-495a-9d8d-80c4df520a1c.md
- JSON: runtime/3060/benchmark/h3-9e79a075-c9cd-495a-9d8d-80c4df520a1c.json

Markdownには、実行条件、ホストOS/PC/RAM/PowerShell、Docker Engine/Compose、GPU UUID/driver、コンテナsystem_stats、image ID、workflow/Docker関連ファイルのSHA-256、参照4モデルのサイズとSHA-256、ComfyUI history、ffprobe、blackdetect、signalstatsを保存した。

## 4090 linked recipe成功

workflow: workflows/yume_4090_recipe_api.json

- prompt ID: 342f3ad9-72f5-4efc-9910-f4614c4fecc3
- start: 2026-08-07T18:11:44.6218990+09:00
- end: 2026-08-07T18:15:59.9718990+09:00
- runner wall: 255.350秒
- ComfyUI: 253.970秒
- status: success
- seed: 7
- output: runtime/4090/output/video/MiniMax_H3_4090_yume_recipe_832x480_20step_cu130_00001_.mp4
- bytes: 547652

ffprobe:

- video: H.264、832×480、24fps、124 frames、5.166667秒
- audio: AAC、32000Hz、2ch、5.167秒
- blackdetect: 黒区間なし

signalstats:

- sample 1: YMIN8、YAVG105.852、YMAX241、UAVG126.263、VAVG127.753、SATAVG9.73169
- sample 2: YMIN9、YAVG105.467、YMAX237、UAVG125.397、VAVG128.725、SATAVG8.90526
- sample 3: YMIN7、YAVG100.471、YMAX235、UAVG124.805、VAVG129.137、SATAVG9.23524

runtime/4090/output/h3_4090_yume_cu130_frame_2.5.pngを目視し、正常な映像を確認した。

## 4090 約720p T2V

H3のwidth/heightは32刻みなので、約720pとして1280×704を採用した。workflow: workflows/tlanoai_t2v_1280x704_api.json

- prompt ID: 061443d7-6d6f-43b3-8a5c-16e65c25c655
- start: 2026-08-07T19:01:09.1567194+09:00
- end: 2026-08-07T19:05:59.4937194+09:00
- runner wall: 290.337秒
- ComfyUI: 288.170秒
- status: success
- GPU: RTX 4090、service h3-4090、port 8188
- 解像度: 1280×704、124 frames、24fps、5.166667秒
- steps/sampler/scheduler: 25 / res_multistep / simple
- base: pruned int8、text: NVFP4、video VAE: official FP16、audio VAE: official FP32
- EasyCache: 0.300 / 0.200 / 0.900
- runtime: memory_usage_factor=1.0、--disable-pinned-memory、--fp16-intermediates
- output: runtime/4090/output/video/MiniMax_H3_T2V_4090_1280x704_25step_easycache_sage_cu130_00001_.mp4
- bytes: 746645
- ffprobe: H.264 1280×704、24fps、124 frames、AAC 32000Hz stereo
- blackdetect: 黒区間なし
- 抽出フレーム: runtime/4090/output/h3_t2v_1280x704_frame_2.5.png
- Markdown: runtime/4090/benchmark/h3-061443d7-6d6f-43b3-8a5c-16e65c25c655.md

## 4090 約720p I2V

開始フレームはimagegenで生成し、1280×704へLanczos縮小・上下クロップした。元画像と実行用画像を保存した。

- imagegen source: assets/i2v_start_frame_source.png
- execution input: runtime/4090/input/MiniMax_H3_I2V_1280x704_start.png
- execution input SHA-256: BE63F90186D46A2860A463C70E4E3E76FDF95A19E98F9DB9E696CD7610D96CD8
- workflow: workflows/tlanoai_i2v_1280x704_api.json
- graph: LoadImage node 16 outputをMiniMaxH3ImageToVideo node 6のfirst_frameへ接続
- prompt ID: f26da7d6-5f00-4cd0-bd18-b384e5ffa4e1
- start: 2026-08-07T19:06:51.8144474+09:00
- end: 2026-08-07T19:11:27.1230342+09:00
- runner wall: 275.309秒
- ComfyUI: 274.210秒
- status: success
- GPU: RTX 4090、service h3-4090、port 8188
- 解像度: 1280×704、124 frames、24fps、5.166667秒
- steps/sampler/scheduler: 25 / res_multistep / simple
- output: runtime/4090/output/video/MiniMax_H3_I2V_4090_1280x704_25step_easycache_sage_cu130_00001_.mp4
- bytes: 1098548
- ffprobe: H.264 1280×704、24fps、124 frames、AAC 32000Hz stereo
- blackdetect: 黒区間なし
- signalstats first frame: YMIN=13、YAVG=127.782、YMAX=237、UAVG=113.27、VAVG=140.254、SATAVG=23.0268
- 抽出フレーム: runtime/4090/output/h3_i2v_1280x704_frame_0.1.png、runtime/4090/output/h3_i2v_1280x704_frame_2.5.png
- 目視: 開始フレームの山・湖・朝日・霧の構図を維持し、途中で霧と光が変化する正常映像
- Markdown: runtime/4090/benchmark/h3-f26da7d6-5f00-4cd0-bd18-b384e5ffa4e1.md

## 3060 I2V 864×480

4090の約720p I2Vと同じ開始画像を864×480へ整形した入力で、3060個別のI2Vを実行した。3060の1280×704は、既存864×480でも使用可能VRAMが少ないため今回は投入していない。

- prompt ID: ee46d53f-f527-4d73-ae1d-14f9c3a0bf0f
- workflow: workflows/tlanoai_i2v_864x480_api.json
- start: 2026-08-07T19:17:30.8783046+09:00
- end: 2026-08-07T19:23:46.2775167+09:00
- runner wall: 375.399秒
- ComfyUI: 374.240秒
- status: success
- GPU: RTX 3060、service h3-3060、port 8189
- low_vram requested: true、applied: false（Compose側のDynamic VRAM/SageAttention条件を使用）
- 解像度: 864×480、124 frames、24fps、5.166667秒
- steps/sampler/scheduler: 25 / res_multistep / simple
- input: runtime/3060/input/MiniMax_H3_I2V_864x480_start.png
- input SHA-256: 6E075DDA3C2E5D1F7B0A9E2C1422504A11CFF353947BB10C348628F5237B7F58
- output: runtime/3060/output/video/MiniMax_H3_I2V_3060_864x480_25step_easycache_sage_cu130_00001_.mp4
- bytes: 683339
- ffprobe: H.264 864×480、24fps、124 frames、AAC 32000Hz stereo
- blackdetect: 黒区間なし
- signalstats first frame: YMIN=10、YAVG=127.404、YMAX=235、UAVG=113.555、VAVG=140.192、SATAVG=22.938
- 抽出フレーム: runtime/3060/output/h3_i2v_864x480_frame_0.1.png、runtime/3060/output/h3_i2v_864x480_frame_2.5.png
- 目視: imagegen開始フレームの湖・山・朝日・霧の構図を維持し、黒化せず霧と光が変化する正常映像
- Markdown: runtime/3060/benchmark/h3-ee46d53f-f527-4d73-ae1d-14f9c3a0bf0f.md
- JSON: runtime/3060/benchmark/h3-ee46d53f-f527-4d73-ae1d-14f9c3a0bf0f.json

## WSL再起動後 3060 約720p T2V / I2V

WSL再起動でモデル・PyTorchキャッシュ・GPUコンテキストを解放した後、4090サービスを停止し、3060単独で1280×704を実行した。T2V/I2VともOOMなしで完走した。

### 3060 T2V 1280×704

- prompt ID: 291fee87-c0b1-4cf3-a63c-df62f5ee6262
- workflow: workflows/tlanoai_t2v_1280x704_api.json
- start: 2026-08-07T21:55:04.6051611+09:00
- end: 2026-08-07T22:11:06.2599363+09:00
- runner wall: 961.655秒
- ComfyUI: 961秒（ログ: Prompt executed in 00:16:01）
- status: success、OOMなし
- GPU: RTX 3060、service h3-3060、port 8189
- 4090 service: 停止（3060単独実験）
- low_vram requested: true、applied: false（Dynamic VRAM/SageAttentionの低VRAM運用）
- 解像度: 1280×704、124 frames、24fps、5.166667秒
- steps/sampler/scheduler: 25 / res_multistep / simple
- output: runtime/3060/output/video/MiniMax_H3_T2V_3060_1280x704_25step_easycache_sage_cu130_wsl_restart_00001_.mp4
- bytes: 927605、SHA-256: BB7BC89D6279FA639165D80F1E894B43DCA3907AC2AF84BCCA3F52DA85222BB4
- ffprobe: H.264 1280×704、24fps、124 frames、AAC 32000Hz stereo
- blackdetect: 黒区間なし
- signalstats first frame: YMIN=15、YAVG=104.214、YMAX=191、UAVG=118.542、VAVG=141.784、SATAVG=19.8821
- 抽出フレーム: runtime/3060/output/h3_t2v_1280x704_wsl_restart_frame_0.1.png、runtime/3060/output/h3_t2v_1280x704_wsl_restart_frame_2.5.png
- 目視: 黒化なし。山・湖・霧の正常な映像を確認
- Markdown: runtime/3060/benchmark/h3-291fee87-c0b1-4cf3-a63c-df62f5ee6262.md
- JSON: runtime/3060/benchmark/h3-291fee87-c0b1-4cf3-a63c-df62f5ee6262.json

### 3060 I2V 1280×704

- prompt ID: b6ab37fa-1af5-4f45-b7e3-7d92d34056a9
- workflow: workflows/tlanoai_i2v_1280x704_api.json
- start: 2026-08-07T22:11:51.8544805+09:00
- end: 2026-08-07T22:25:12.6947561+09:00
- runner wall: 800.840秒
- ComfyUI: 796秒（ログ: Prompt executed in 00:13:16）
- status: success、OOMなし
- GPU: RTX 3060、service h3-3060、port 8189
- low_vram requested: true、applied: false（Dynamic VRAM/SageAttentionの低VRAM運用）
- 解像度: 1280×704、124 frames、24fps、5.166667秒
- steps/sampler/scheduler: 25 / res_multistep / simple
- input: runtime/3060/input/MiniMax_H3_I2V_1280x704_start.png
- input SHA-256: BE63F90186D46A2860A463C70E4E3E76FDF95A19E98F9DB9E696CD7610D96CD8
- output: runtime/3060/output/video/MiniMax_H3_I2V_3060_1280x704_25step_easycache_sage_cu130_wsl_restart_00001_.mp4
- bytes: 1569004、SHA-256: 5437ADD0A093793E72DE178F0F8744A4D0539805319A8C4797E831B0C7011BC4
- ffprobe: H.264 1280×704、24fps、124 frames、AAC 32000Hz stereo
- blackdetect: 黒区間なし
- signalstats first frame: YMIN=13、YAVG=127.447、YMAX=237、UAVG=113.425、VAVG=140.226、SATAVG=22.8895
- 抽出フレーム: runtime/3060/output/h3_i2v_1280x704_wsl_restart_frame_0.1.png、runtime/3060/output/h3_i2v_1280x704_wsl_restart_frame_2.5.png
- 目視: imagegen開始フレームの山・湖・朝日・霧を維持し、黒化せず霧が変化する正常映像
- Markdown: runtime/3060/benchmark/h3-b6ab37fa-1af5-4f45-b7e3-7d92d34056a9.md
- JSON: runtime/3060/benchmark/h3-b6ab37fa-1af5-4f45-b7e3-7d92d34056a9.json

## 4090約720p実験時のCompose状態

- h3-3060: healthy、8189
- h3-4090: healthy、8188
- 両方のimage: local/minimax-h3-comfyui:v0.30.0
- コンテナ内PyTorch: 2.11.0+cu130
- コンテナ内CUDA runtime: 13.0
- 3060 SageAttention: import成功
- CUDA module loading: LAZY

## 3060約720p追試後のCompose状態

- h3-3060: running、healthy、8189
- h3-4090: stopped（3060単独実験のため停止）
- 3060追試はWSL再起動後のDocker Desktop復帰完了後に実行

## 再現用ホスト環境スナップショット

実験を実行したホスト環境:

- OS: Microsoft Windows 11 Pro 64-bit、10.0.26200、build 26200
- PC: Micro-Star International Co., Ltd. MS-7D88
- RAM: 137270165504 bytes
- PowerShell: 5.1.26100.8875 Desktop
- Docker Engine server: 29.4.3
- Docker Compose: v5.1.3
- ffmpeg / ffprobe: Gyan.FFmpeg 8.1.1 full build
- NVIDIA driver: 591.86
- RTX 3060: UUID GPU-580ccd21-cc60-0b38-9671-7a7e8f6a9efd、12288 MiB
- RTX 4090: UUID GPU-f877fbc1-9f24-bd97-3359-dd358eaa2caa、24564 MiB

コンテナ環境:

- image: local/minimax-h3-comfyui:v0.30.0
- ComfyUI: 0.30.0
- Python: 3.12.3
- PyTorch: 2.11.0+cu130
- CUDA runtime: 13.0
- cuDNN: base imageのcuDNN 9
- CUDA_MODULE_LOADING: LAZY
- 3060 argv: --listen 0.0.0.0 --port 8188 --use-sage-attention --preview-method none
- 4090 argv: --listen 0.0.0.0 --port 8188 --disable-pinned-memory --fp16-intermediates --preview-method none

今後の各実験では、この情報をruntime/GPU/benchmark/h3-PROMPT_ID.mdへ自動保存する。workflow、Docker関連ファイル、参照モデルのSHA-256も同じレポートに記録する。

## 再現時に保存するもの

scripts/run-h3-post-condition.ps1が次をruntime/GPU/benchmark/h3-PROMPT_ID.jsonへ保存する。

- workflow path
- low_vram_requested / low_vram_applied
- GPUとCompose service
- Dynamic VRAM、SageAttention、CUDA_MODULE_LOADING
- width、height、frames、steps、sampler、scheduler
- base、VAE、EasyCache、seed
- start、end、wall_seconds
- ComfyUI log、history status
- output file path、size、LastWriteTime

同じ実験についてh3-PROMPT_ID.mdも自動生成する。MarkdownにはJSONと同じ条件に加えて、ホストOS、PowerShell、Docker/Compose、GPUドライバ、コンテナのsystem_stats、workflow/Docker関連ファイルのSHA-256、参照モデルのサイズとSHA-256、ffprobe、blackdetect、signalstatsを保存する。runtime/GPU/benchmark/index.mdから実験ごとのMarkdownとJSONへ移動できる。

## WSL再起動後のメモリ確認

2026-08-07 21:39 JST、`wsl --shutdown`を実行してWSL2を停止した。停止前後で以下の通り大幅に解放された。

| 項目 | 停止前 | WSL停止後 |
|---|---:|---:|
| ホストRAM使用量 | 126.22 / 127.84 GiB（98.7%） | 21.04 / 127.84 GiB（16.5%） |
| ホストRAM空き | 1.62 GiB | 106.81 GiB |
| RTX 3060 VRAM使用量 | 9,745 / 12,288 MiB | 861 / 12,288 MiB |
| RTX 4090 VRAM使用量 | 6,341 / 24,564 MiB | 244 / 24,564 MiB |

WSLの`Ubuntu`と`docker-desktop`は停止状態。したがって、WSL再起動でH3のモデル常駐RAM、PyTorchキャッシュ、GPUコンテキストが解放されたことを確認した。Docker ComposeのH3コンテナも停止しているため、再実験時はDocker Desktop復帰後に対象GPUだけ起動する。

## 3060約720p生成後のリソース状態

T2V/I2V生成完了後の2026-08-07 22:31 JSTの確認値。h3-3060はhealthyで稼働中、h3-4090は停止中。

- ホストRAM: 117.55 / 127.84 GiB使用（91.9%）、空き10.29 GiB
- RTX 3060: 8,479 / 12,288 MiB使用、空き3,635 MiB
- RTX 4090: 636 / 24,564 MiB使用、空き23,503 MiB

WSL再起動で空きRAMは確保できたが、3060モデルを常駐させると約117GiBまで戻る。追加実験をしない場合は`docker compose stop h3-3060`でモデルを解放できる。
