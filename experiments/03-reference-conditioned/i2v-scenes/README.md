# MiniMax-H3 Kijai LightX2V — ImageGen start-frame scene generalization

- ID: `2026-08-08-reference-i2v-scenes`
- Status: `verified`
- GPU: RTX 4090
- Compose service: `h3-4090` (`http://localhost:8188`)
- Purpose: ImageGenで作成した開始フレームをMiniMax-H3 I2Vへ入力し、車・スポーツ・イラスト・バトルの4種類で同じKijai/LightX2V条件が成立するか確認する

Frame tile: [contact sheet](./previews/contact-sheet.jpg) / [manifest](./previews/contact-sheet.json)

Record: [experiment.json](./experiment.json) · [tracked frame tile](./previews/contact-sheet.jpg)

![ImageGen-started I2V frame tile](./previews/contact-sheet.jpg)

> This tracked tile is the public visual evidence; source MP4s under `runtime/*/output` remain local-only.

## 結論

4テーマすべてで生成に成功した。4本とも `1344×768 / 158 frames / 24 fps / 6.583333 sec / H.264 + AAC`、`blackdetect=0`、OOMなしだった。

| Scene | Comfy実行時間 | runner wall | 出力サイズ | 黒フレーム | 目視結果 |
|---|---:|---:|---:|---:|---|
| 車 | 209.579 sec | 210.402 sec | 2,896,740 bytes | 0 | 車体・道路・山を維持し、前進とカメラ追従 |
| スポーツ | 208.834 sec | 210.409 sec | 2,241,947 bytes | 0 | スタート姿勢から走り出す動き、追従カメラ |
| イラスト | 208.941 sec | 210.505 sec | 2,328,790 bytes | 0 | 絵柄・人物・道を維持し、雲・光・カメラが変化 |
| バトル | 210.609 sec | 215.453 sec | 2,804,264 bytes | 0 | 2人の位置・武器を維持し、押し込み・砂塵・旗が変化 |

`Comfy実行時間`はComfyUIの`execution_start`から`execution_success`まで、`runner wall`は実験runnerの開始からレポート完了まで。各値は個別のJSONレポートにも保存している。

## 今回固定した条件

今回変えたのは、シーン、ImageGen開始画像、I2V prompt、seedだけ。前回のKijai/LightX2V検証と揃え、samplerは速度確認で有利だった`sa_solver`に固定した。`er_sde`とのsampler比較ではない。

- GPU: NVIDIA GeForce RTX 4090、VRAM 24,564 MiB
- Docker Compose: service `h3-4090`、host port `8188`
- Docker image: `local/minimax-h3-comfyui:v0.30.0`
- Docker image digest: `sha256:38005038907d58cec68c163448251a5578328a57bae6bde589db306bf2ed4736`
- Docker Engine: `29.4.3`
- Docker Compose: `5.1.3`
- ComfyUI: `0.30.0`
- Container Python: `3.12.3`
- PyTorch: `2.11.0+cu130`
- NVIDIA driver: `591.86`
- `CUDA_MODULE_LOADING=LAZY`
- ComfyUI arguments: `--disable-pinned-memory --fp16-intermediates --preview-method none`
- low VRAM: `false`
- dynamic VRAM: `false`
- SageAttention: `false`（4090実験では使用していない）
- Base: `minimax_h3_fl2va_pruned_int8_convrot.safetensors`
- Text encoder: `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors`
- Video VAE: `minimax_h3_video_vae_fp16.safetensors`
- Audio VAE: `minimax_h3_audio_vae_fp32.safetensors`
- LoRA loader: `LoraLoaderModelOnly`
- LoRA: `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`
- LoRA strength: `0.75`
- Resolution: `1344×768`
- Length: `158 frames`
- FPS: `24`
- Steps: `4`
- Scheduler: `simple`
- Sampler: `sa_solver`
- EasyCache: `reuse_threshold=0.3 / start_percent=0.2 / end_percent=0.9 / verbose=false`
- Audio: 公式Audio VAEからAAC stereo
- 4 workflowの共通グラフ正規化SHA-256（scene prompt・seed・入力画像・出力prefixを除外）: `358EEAAA06B88FEC898C1A9A07FAFF05781AF6AF73FC3FC592838FB8888D9E55`

ImageGenの開始画像は各`1672×941` PNGをそのままワークフローの`LoadImage`へ渡し、生成ノードの出力指定を`1344×768`に固定した。開始画像の生成プロンプトとSHA-256は[`imagegen-prompts.md`](./imagegen-prompts.md)に保存している。

## 再現手順

```powershell
cd <repo-root>
docker compose --profile 4090 up -d h3-4090

.\scripts\run-h3-post-condition.ps1 `
  -Gpu 4090 -Port 8188 `
  -Workflow .\experiments\03-reference-conditioned\i2v-scenes\workflows\minimax_h3_kijai_lightx2v_4step_i2v_sa_solver_car_1344x768_api.json `
  -OutputPrefix video/MiniMax_H3_Kijai_LightX2V_I2V_1344x768_4step_sa_solver_scene_car `
  -LowVram $false -Seed -1 -TimeoutSeconds 14400
```

スポーツ、イラスト、バトルは同じコマンドでworkflowと`OutputPrefix`だけを、それぞれの実験表にある値へ置き換える。各workflowはAPI形式で、入力画像名とseedも埋め込み済みなので、実行時に別条件へ変わらない。

## 4本の実験詳細

### 1. 車

- ImageGen input: `runtime/4090/input/MiniMax_H3_I2V_scene_car_imagegen_start.png`
- Video prompt: `Animate the supplied sports car start frame into a cinematic high-speed mountain-road shot. Preserve the car design, road composition, and mountain background, add controlled forward camera movement, subtle wheel rotation, realistic reflections, and natural road motion, no text.`
- Seed: `2026080803`
- Workflow: [`car workflow`](./workflows/minimax_h3_kijai_lightx2v_4step_i2v_sa_solver_car_1344x768_api.json)
- Workflow SHA-256: `1416AA0642DCD91750BB35293DB78FAD43D6DFF701065D852A39A2C1DA73BA6F`
- Prompt ID: `38166d06-cdd1-4f48-94fc-4fa381cc7d32`
- Run: `2026-08-08T12:53:43.4019691+09:00` → `2026-08-08T12:57:13.8040417+09:00`
- Output: local-only MP4 at `runtime/4090/output/video/MiniMax_H3_Kijai_LightX2V_I2V_1344x768_4step_sa_solver_scene_car_00001_.mp4`; review the tracked [contact sheet](./previews/contact-sheet.jpg)
- Output SHA-256: `468D9FB859757B6AEB141950A97737D7C3F713FDD426122A40560A2920EBB062`
- Input SHA-256: `AA18AB747483D6761E897456EED5F12CFB82402CC891B64484893D1AEF5A8B0A`
- Detailed report: [`JSON`](../../../runtime/4090/benchmark/h3-38166d06-cdd1-4f48-94fc-4fa381cc7d32.json) / [`Markdown`](../../../runtime/4090/benchmark/h3-38166d06-cdd1-4f48-94fc-4fa381cc7d32.md)
- Visual check: first and middle frames both show one car, continuous road, mountain environment, and no black frame.

### 2. スポーツ

- ImageGen input: `runtime/4090/input/MiniMax_H3_I2V_scene_sports_imagegen_start.png`
- Video prompt: `Animate the supplied sprint start frame into a cinematic sports shot. Preserve the athlete's anatomy, starting pose, lane, and stadium composition, add a powerful launch into the sprint, subtle camera tracking, realistic fabric movement, and natural stadium atmosphere, no text.`
- Seed: `2026080804`
- Workflow: [`sports workflow`](./workflows/minimax_h3_kijai_lightx2v_4step_i2v_sa_solver_sports_1344x768_api.json)
- Workflow SHA-256: `AE6D5FE87B7A682C8502C23A758F5FB46CC29EEA5CCFF1E714EC9AB2B7820121`
- Prompt ID: `31b250ab-c2cf-472e-a843-118ffa7f6f98`
- Run: `2026-08-08T12:58:11.1960404+09:00` → `2026-08-08T13:01:41.6045675+09:00`
- Output: local-only MP4 at `runtime/4090/output/video/MiniMax_H3_Kijai_LightX2V_I2V_1344x768_4step_sa_solver_scene_sports_00001_.mp4`; review the tracked [contact sheet](./previews/contact-sheet.jpg)
- Output SHA-256: `0B9C76D2373473B258C9899B6127A8C22792C867714BF09FBF425360F83BB9E5`
- Input SHA-256: `33B52086889F97ADE8FB2EA8F23C3F25214498A5015881D33B9E8E42F3D3130C`
- Detailed report: [`JSON`](../../../runtime/4090/benchmark/h3-31b250ab-c2cf-472e-a843-118ffa7f6f98.json) / [`Markdown`](../../../runtime/4090/benchmark/h3-31b250ab-c2cf-472e-a843-118ffa7f6f98.md)
- Visual check: first frame preserves the crouched start pose; the middle frame shows launch and camera tracking, with no black frame.

### 3. イラスト

- ImageGen input: `runtime/4090/input/MiniMax_H3_I2V_scene_illustration_imagegen_start.png`
- Video prompt: `Animate the supplied floating-island illustration start frame while preserving its hand-painted style, character silhouette, lantern, path, and luminous ruin composition. Add gentle forward camera movement, drifting clouds, a subtle cape and lantern motion, and soft atmospheric light, no text.`
- Seed: `2026080805`
- Workflow: [`illustration workflow`](./workflows/minimax_h3_kijai_lightx2v_4step_i2v_sa_solver_illustration_1344x768_api.json)
- Workflow SHA-256: `3775C6350F6189CADB70CF7797B5C2D283672D5B17AA75481A70BD05E64D67A2`
- Prompt ID: `acec67b0-578d-4b26-9ee4-0022a399b686`
- Run: `2026-08-08T13:02:30.4564284+09:00` → `2026-08-08T13:06:00.9616352+09:00`
- Output: local-only MP4 at `runtime/4090/output/video/MiniMax_H3_Kijai_LightX2V_I2V_1344x768_4step_sa_solver_scene_illustration_00001_.mp4`; review the tracked [contact sheet](./previews/contact-sheet.jpg)
- Output SHA-256: `6ADC0B80614773902A2E2392B0965F2B9C945F086596D25523B43836349A293A`
- Input SHA-256: `09D56EF3CD1947CE66E5BC9F019FA4DED2A636A14D42947022268134546D7A6F`
- Detailed report: [`JSON`](../../../runtime/4090/benchmark/h3-acec67b0-578d-4b26-9ee4-0022a399b686.json) / [`Markdown`](../../../runtime/4090/benchmark/h3-acec67b0-578d-4b26-9ee4-0022a399b686.md)
- Visual check: the hand-painted style, adventurer silhouette, lantern, path, and ruin remain coherent; cloud and light motion are visible, with no black frame.

### 4. バトル

- ImageGen input: `runtime/4090/input/MiniMax_H3_I2V_scene_battle_imagegen_start.png`
- Video prompt: `Animate the supplied fantasy battle start frame into a cinematic pre-clash shot. Preserve both original warriors, their armor, weapons, positions, and ruined arena composition, add a slow camera push-in, controlled cape movement, drifting dust, sparks, and distant lightning, no gore and no text.`
- Seed: `2026080806`
- Workflow: [`battle workflow`](./workflows/minimax_h3_kijai_lightx2v_4step_i2v_sa_solver_battle_1344x768_api.json)
- Workflow SHA-256: `F1ED352B372B3276D27F970CE1A250B1BFCC496A0305CD010ADBF57687777553`
- Prompt ID: `1bdb13fd-e452-415c-8a69-38d795d9ae98`
- Run: `2026-08-08T13:06:48.1655644+09:00` → `2026-08-08T13:10:23.6183409+09:00`
- Output: local-only MP4 at `runtime/4090/output/video/MiniMax_H3_Kijai_LightX2V_I2V_1344x768_4step_sa_solver_scene_battle_00001_.mp4`; review the tracked [contact sheet](./previews/contact-sheet.jpg)
- Output SHA-256: `5A0BECA0A21423F86F6280AAA72ED06359423C4A878CB2BCB17543443C3A8E2D`
- Input SHA-256: `80D12E69F6E8B629D91A7E1F490C620A77D6CEC37D63B559CBADFDC497E9421A`
- Detailed report: [`JSON`](../../../runtime/4090/benchmark/h3-1bdb13fd-e452-415c-8a69-38d795d9ae98.json) / [`Markdown`](../../../runtime/4090/benchmark/h3-1bdb13fd-e452-415c-8a69-38d795d9ae98.md)
- Visual check: both original warriors remain separated with their weapons and arena composition; push-in, dust, cape/flag movement and lightning atmosphere are visible, with no gore or black frame.

## モデルファイルの再現情報

| File | Bytes | SHA-256 |
|---|---:|---|
| `models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors` | 20,970,379,616 | `E889202C41DAFB67B10D67B97F0D8541508036A6090AF23425A5C2615D03C47A` |
| `models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | 15,687,142,551 | `35A88D51044231FE332301D7A62AA81E3F2CBA62FEBEB446E2C1E3E0EF76F2C6` |
| `models/vae/minimax_h3_video_vae_fp16.safetensors` | 5,207,808,496 | `7C1F131492E7EDDACAAC9069A61B81BDD39DE5CC96561E677C5EAB1CDCE5E522` |
| `models/vae/minimax_h3_audio_vae_fp32.safetensors` | 605,254,808 | `8E505D95DD1561D47ABD43D4238FD40D9BB1AE9E147ED0A4CBA778D76AE4DB48` |
| `models/loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors` | 1,956,171,984 | `FC9B6500F0331FE925B004738BAAA31BD34104741C8BF9334816F9AC3005C8C1` |

## 目視確認と制限

- 4本とも冒頭と約3.0秒地点のフレームを抽出して確認した。
- `blackdetect`は4本とも`0`。先頭フレームのY平均も車`103.278`、スポーツ`76.4329`、イラスト`110.668`、バトル`64.2438`で、全黒信号ではない。
- 画像品質・人物／車体の長時間一貫性・音質についての定量評価は未実施。
- ImageGenの開始画像は本実験用に新規生成したローカル素材で、プロンプトとSHA-256は保存したが、ImageGen側の内部乱数・モデル版は固定していない。そのため、別環境で完全に同じPNGを再生成する実験ではなく、保存済みPNGを使うworkflow再現である。
- X投稿にGPU、prompt、seed、sampler、scheduler、workflowは明記されていない。`1344×768 / 24fps / 158 frames`とKijaiの`4 steps / strength 0.75`を出典に合わせ、`sa_solver`と各scene promptは本ラボの実験条件として明示している。

## 関連記録

- [Kijai/LightX2V 4-step基礎実験](../../02-low-step-generation/lightx2v-4step/README.md)
- [出典と解釈境界](./sources.md)
- [ImageGen開始画像プロンプト](./imagegen-prompts.md)

## X投稿シミュレーション

- Simulator: https://madesk.tail8be30.ts.net:8882/
- Payload: `sunwood-x-kijai-scenes-simulation-2026-08-08.json`
- Simulator source: `sunwood-x-simulator-kijai-scenes-2026-08-08/index.html`
- HyperFrames composition: `hyperframes-kijai-scenes-2026-08-08/index.html`
- Montage output: `hyperframes-kijai-scenes-2026-08-08/renders/MiniMax_H3_Kijai_LightX2V_scene_montage_1920x1080_24fps.mp4`
- Provenance: 親投稿の概要動画は、今回の4本の実生成MP4だけを2×2配置した証拠由来の動画。各返信の動画も同じ実生成MP4を使用している。
- Status: シミュレーションのみ。Xへは投稿していない。
