# MiniMax-H3 調査・検証メモ

調査日: 2026-08-07 JST
対象: X上のRTX 3060 / RTX 4090投稿、公式資料、Docker Composeローカル検証
プロジェクト: <repo-root>

## 結論

3060で最初に確認したMP4は真っ黒だった。旧Turbo/full-int8 + Kijai int8 video VAE経路を成功結果として扱ったのは誤りである。blackdetectとsignalstatsで全フレームが黒信号だったことを確認し、最終条件から除外した。

正しい3060の対象投稿は[TlanoAIの投稿](https://x.com/TlanoAI/status/2084940455809286397)である。Grok BuildのX Searchで調査し、ログイン済みブラウザで投稿本文を照合した。投稿の既知条件は、RTX 3060 12GB、ComfyUI 0.30.0、PyTorch 2.11.0+cu130、CUDA 13.0、SageAttention 2.2.0、pruned int8 base、NVFP4 text encoder、公式FP16 video VAE、公式FP32 audio VAE、Dynamic VRAM + CPU offload、EasyCache、SageAttention、864×480、124 frames、24fps、25 stepsである。

この条件をDocker Composeへ反映し、PyTorch 2.11.0+cu130のLinuxコンテナで3060を再実行した。coldは424.660秒、warm inferenceは267.980秒で、両方ともblackdetectの黒区間なし、正常な映像信号、音声付きMP4だった。

4090は[yume_arasakiの投稿](https://x.com/yume_arasaki/status/2084766655331360999)と、X本文からリンクされた[GitHub recipe](https://github.com/yume-arasaki/RTX-4090-3090-Minimax-H3-15s)を分けて扱った。X本文は842×480、リンク先recipeは832×480なので、ローカル実測はリンク先recipeの再現である。

## X調査の記録

### 3060: TlanoAI

参照: https://x.com/TlanoAI/status/2084940455809286397

投稿本文から確認した値:

- RTX 3060 12GB、driver 591.86
- ComfyUI 0.30.0
- Python 3.10.10
- PyTorch 2.11.0+cu130
- CUDA runtime 13.0、cuDNN 9.19
- SageAttention 2.2.0
- Triton Windows 3.7.1.post27
- base: minimax_h3_fl2va_pruned_int8_convrot.safetensors
- text: qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors
- video VAE: minimax_h3_video_vae_fp16.safetensors
- audio VAE: minimax_h3_audio_vae_fp32.safetensors
- Dynamic VRAM、CPU offload
- EasyCache: reuse_threshold 0.300、start_percent 0.200、end_percent 0.900
- SageAttention、preview disabled
- 25 sampling steps
- T2V 864×480、I2V 640×640
- 5秒、124 frames、24fps、audio enabled
- T2V first/load-inclusive 436.18秒、warm 351.53秒
- I2V first 390.72秒、warm 319.34秒

本文ではLoRA、sampler、scheduler、seed、promptが確認できない。ローカルworkflowでres_multistep / simple、検証用seed、検証用promptを使ったが、これらは投稿記載値ではない。

### 4090: yume_arasaki

参照: https://x.com/yume_arasaki/status/2084766655331360999

X本文から確認した値:

- 単体RTX 4090
- 約842×480、24fps、20 steps
- 5秒は約7分、15秒は約30分
- 24GBカードで約41GBのweightsをaggressive CPU offload
- sampling時peak約6.6GB、load後約22GB

本文にsampler、scheduler、LoRA、VAE、ComfyUI versionはない。

XからリンクされたGitHub recipeで確認した値:

- 832×480、124 frames
- pruned int8 base
- NVFP4 text encoder
- 公式FP16 video VAE / FP32 audio VAE
- 20 steps、res_multistep、simple
- memory_usage_factor=1.0
- --disable-pinned-memory、--fp16-intermediates

X本文の842×480とrecipeの832×480を混ぜず、実測のsource_classをlinked recipeとして記録した。

### 参考候補

- [lizikk_zhuの4090投稿](https://x.com/lizikk_zhu/status/2084859489115648336): 608×352、124 frames、pruned/int8、NVFP4、約71.83秒。ただしsteps、sampler、scheduler、VAE、offloadが不足。
- [thekhomaの4090投稿](https://x.com/thekhoma/status/2084504336173076800): 1344×768、124 frames、14 steps、170.3秒。ただし主要なモデル・offload条件が不足。
- [onigirikilaの3060投稿](https://x.com/onigirikila/status/2084858171462754672): 864×480、20 steps、SageAttention 2、EasyCache。baseline782.3秒、両方399.7秒。ただしexact base/LoRA/VAE/samplerが不明なのでTlanoAI条件へ混ぜなかった。

以前の記録にあったLabMike3D URLは、今回の対象条件として確認できたTlanoAI投稿とは別で、公開状態・URLの整合も取れなかった。そのため、旧LabMike3D/Turbo記録を正しい3060投稿の根拠として残さない。

## 採用したDocker条件

- ComfyUI v0.30.0
- PyTorch 2.11.0+cu130
- CUDA 13.0、cuDNN 9
- Linux container Python 3.12.3
- SageAttention 2.2.0のcu130 wheel
- CUDA_MODULE_LOADING=LAZY
- 3060: Dynamic VRAM、CPU offload、SageAttention
- 4090: memory_usage_factor=1.0、pinned memory無効、fp16 intermediates
- 3060 UUID: GPU-580ccd21-cc60-0b38-9671-7a7e8f6a9efd
- 4090 UUID: GPU-f877fbc1-9f24-bd97-3359-dd358eaa2caa

Windows投稿とLinux Dockerの差:

- 投稿のPythonはWindows 3.10.10、実測はLinux container 3.12.3
- 投稿のTritonはWindows版、実測はLinux wheel
- GPU、モデル、主要PyTorch/CUDA/SageAttention版、解像度、frames、steps、EasyCache値は意図的に合わせた
- したがって時間は投稿の数値を検算する実測であり、バイナリ完全一致の再現ではない

## 黒動画の原因切り分け

旧経路:

- Turbo/full-int8 base
- Kijai experimental int8 video VAE
- 8 steps、Turbo sampler
- 3060出力: 全フレームが黒
- signalstats: YMIN=16、YAVG=16、YMAX=16、UAVG=128、VAVG=128、SATAVG=0

Kijai int8 VAEだけを使うA/Bでも黒になった。公式FP16 video VAEへ切り替えた5フレーム確認では、湖・山・霧の映像が正常に出た。最終workflowは公式FP16/FP32 VAEへ固定し、旧Turbo/full-int8 pathは使わない。

旧DockerのPyTorch 2.7.1+cu128で正しいTlanoAI workflowを試した際は3060がCUDA OOMになった。投稿のPyTorch 2.11.0+cu130に合わせてDocker imageを更新し、その後cold/warmとも完了した。

## ローカル実測

詳細はverification-log.mdとbenchmark-results-2026-08-07.jsonに保存した。

### 3060 TlanoAI条件

- cold prompt: 8934f550-30f1-4716-8b69-e743f6fab561
- start: 2026-08-07T17:54:42.0135415+09:00
- end: 2026-08-07T18:01:47.5398389+09:00
- runner wall: 425.526秒
- ComfyUI: 424.660秒
- output: runtime/3060/output/video/MiniMax_H3_TlanoAI_3060_864x480_25step_easycache_sage_cold_cu130_00001_.mp4
- bytes: 395296
- video: H.264、864×480、24fps、124 frames、5.166667秒
- audio: AAC、32000Hz、2ch、5.167秒
- blackdetect: 黒区間なし
- VAE log: shape (1,3,124,480,864)、finite=True、min=-1、max=1

- warm inference prompt: 6983bd5f-e393-4bd7-b5e5-8a4eabdf779e
- start: 2026-08-07T18:04:04.9450969+09:00
- end: 2026-08-07T18:08:35.2341018+09:00
- runner wall: 270.289秒
- ComfyUI: 267.980秒
- output: runtime/3060/output/video/MiniMax_H3_TlanoAI_3060_864x480_25step_easycache_sage_warm_inference_cu130_00001_.mp4
- bytes: 463849
- video: H.264、864×480、24fps、124 frames、5.166667秒
- audio: AAC、32000Hz、2ch、5.167秒
- blackdetect: 黒区間なし

warmと呼んでいるのはモデル常駐後にseedを変えて実際に25 stepsを再実行したもの。別に行った5.062秒のcache/export onlyはSaveVideoだけなので、生成時間として数えない。

### 4090 linked recipe

- prompt: 342f3ad9-72f5-4efc-9910-f4614c4fecc3
- start: 2026-08-07T18:11:44.6218990+09:00
- runner wall: 255.350秒
- ComfyUI: 253.970秒
- output: runtime/4090/output/video/MiniMax_H3_4090_yume_recipe_832x480_20step_cu130_00001_.mp4
- bytes: 547652
- video: H.264、832×480、24fps、124 frames、5.166667秒
- audio: AAC、32000Hz、2ch、5.167秒
- blackdetect: 黒区間なし

## ファイル

- compose.yaml: GPU別Composeサービス
- Dockerfile: ComfyUI、PyTorch/CUDA 13.0、SageAttention
- workflows/tlanoai_3060_api.json: 3060投稿条件
- workflows/yume_4090_recipe_api.json: 4090リンク先recipe
- workflows/tlanoai_t2v_1280x704_api.json: 約720p T2V
- workflows/tlanoai_i2v_1280x704_api.json: 約720p I2V
- workflows/tlanoai_i2v_864x480_api.json: 3060 I2V比較用
- assets/i2v_start_frame_generation.md: imagegen開始フレーム生成記録
- scripts/run-h3-post-condition.ps1: API投入とwall time/report保存
- benchmark-results-2026-08-07.json: 機械可読な結果
- verification-log.md: 時系列ログ

## T2V / I2V 約720p追試

サブエージェントによる読み取り専用QAで、MiniMaxH3ImageToVideoのoptional first_frame、LoadImageのimage_upload=true、width/heightの32刻みを確認した。1280×720はheightが32刻みに合わないため、1280×704を720p級の実験解像度に採用した。

I2VはLoadImage node 16の出力をMiniMaxH3ImageToVideo node 6のfirst_frameへ接続した。VAEEncodeは追加していない。H3ノード自身が開始画像をVAE encodeし、frame 0 keyframeとして扱う実装だった。

### 4090 T2V 1280×704

- prompt: 061443d7-6d6f-43b3-8a5c-16e65c25c655
- workflow: workflows/tlanoai_t2v_1280x704_api.json
- ComfyUI: 288.170秒、runner wall: 290.337秒
- 25 steps、res_multistep / simple、EasyCache 0.3 / 0.2 / 0.9
- output: runtime/4090/output/video/MiniMax_H3_T2V_4090_1280x704_25step_easycache_sage_cu130_00001_.mp4
- 1280×704、124 frames、24fps、音声付き5.167秒
- blackdetect: 0 intervals

### 4090 I2V 1280×704

- prompt: f26da7d6-5f00-4cd0-bd18-b384e5ffa4e1
- workflow: workflows/tlanoai_i2v_1280x704_api.json
- ComfyUI: 274.210秒、runner wall: 275.309秒
- input: assets/i2v_start_frame_1280x704.png
- input SHA-256: BE63F90186D46A2860A463C70E4E3E76FDF95A19E98F9DB9E696CD7610D96CD8
- output: runtime/4090/output/video/MiniMax_H3_I2V_4090_1280x704_25step_easycache_sage_cu130_00001_.mp4
- 1280×704、124 frames、24fps、音声付き5.167秒
- blackdetect: 0 intervals
- 開始フレームの構図を維持した正常映像を目視確認

### 3060 I2V 864×480

- prompt: ee46d53f-f527-4d73-ae1d-14f9c3a0bf0f
- workflow: workflows/tlanoai_i2v_864x480_api.json
- ComfyUI: 374.240秒、runner wall: 375.399秒
- input: assets/i2v_start_frame_864x480.png
- input SHA-256: 6E075DDA3C2E5D1F7B0A9E2C1422504A11CFF353947BB10C348628F5237B7F58
- output: runtime/3060/output/video/MiniMax_H3_I2V_3060_864x480_25step_easycache_sage_cu130_00001_.mp4
- 864×480、124 frames、24fps、音声付き5.167秒
- blackdetect: 0 intervals
- frame 0.1 / 2.5を目視し、開始画像の構図を維持した正常映像を確認

### WSL再起動後 3060 T2V 1280×704

WSL再起動後に4090サービスを停止し、3060単独で約720p T2Vを実行した。

- prompt: 291fee87-c0b1-4cf3-a63c-df62f5ee6262
- workflow: workflows/tlanoai_t2v_1280x704_api.json
- ComfyUI: 961秒、runner wall: 961.655秒
- output: runtime/3060/output/video/MiniMax_H3_T2V_3060_1280x704_25step_easycache_sage_cu130_wsl_restart_00001_.mp4
- output SHA-256: BB7BC89D6279FA639165D80F1E894B43DCA3907AC2AF84BCCA3F52DA85222BB4
- 1280×704、124 frames、24fps、音声付き5.167秒
- blackdetect: 0 intervals
- OOM: 発生なし
- frame 0.1 / 2.5を目視し、黒化しない山・湖・霧の映像を確認

### WSL再起動後 3060 I2V 1280×704

- prompt: b6ab37fa-1af5-4f45-b7e3-7d92d34056a9
- workflow: workflows/tlanoai_i2v_1280x704_api.json
- ComfyUI: 796秒、runner wall: 800.840秒
- input: assets/i2v_start_frame_1280x704.png
- input SHA-256: BE63F90186D46A2860A463C70E4E3E76FDF95A19E98F9DB9E696CD7610D96CD8
- output: runtime/3060/output/video/MiniMax_H3_I2V_3060_1280x704_25step_easycache_sage_cu130_wsl_restart_00001_.mp4
- output SHA-256: 5437ADD0A093793E72DE178F0F8744A4D0539805319A8C4797E831B0C7011BC4
- 1280×704、124 frames、24fps、音声付き5.167秒
- blackdetect: 0 intervals
- OOM: 発生なし
- frame 0.1 / 2.5を目視し、imagegen開始フレームの構図を維持した正常映像を確認

結論: WSL再起動後の3060では、1280×704のT2V/I2VともOOMを起こさず生成できた。各実験の環境、モデルハッシュ、入力画像ハッシュ、ffprobe、signalstatsはGPU別benchmarkのMarkdown/JSONに保存した。
