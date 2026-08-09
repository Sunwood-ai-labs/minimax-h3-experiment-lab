# MiniMax-H3 Kijai LightX2V — ImageGen start-frame scene generalization

[Japanese detailed record: README.ja.md](./README.ja.md)

- Experiment ID: `2026-08-08-reference-i2v-scenes`
- Status: `verified`
- GPU: RTX 4090
- Compose service: `h3-4090` (`http://localhost:8188`)
- Purpose: feed ImageGen-created start frames into MiniMax-H3 I2V and verify that the same Kijai/LightX2V conditions work for four scene types: car, sports, illustration, and battle.

Frame tile: [contact sheet](./previews/contact-sheet.jpg) / [manifest](./previews/contact-sheet.json)

Record: [experiment.json](./experiment.json) · [tracked frame tile](./previews/contact-sheet.jpg)

![ImageGen-started I2V frame tile](./previews/contact-sheet.jpg)

> The tracked tile is the public visual evidence. The source MP4s under `runtime/*/output` are local-only artifacts.

## X video and reference URLs

- **Generated video post**: none (not posted / `local-only`). The four generated MP4s are recorded as local outputs of this experiment.
- **Reference sources**: [sd_tutorial post](https://x.com/sd_tutorial/status/2085760369612783646) / [Kijai MiniMax-H3 Comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy) / [LightX2V upstream](https://huggingface.co/lightx2v/Minimax-h3-Turbo/tree/main)
- **Workflow-to-video mapping**:

  | Workflow | Scene | X video |
  |---|---|---|
  | [`car`](./workflows/minimax_h3_kijai_lightx2v_4step_i2v_sa_solver_car_1344x768_api.json) | car | — (not posted / local-only) |
  | [`sports`](./workflows/minimax_h3_kijai_lightx2v_4step_i2v_sa_solver_sports_1344x768_api.json) | sports | — (not posted / local-only) |
  | [`illustration`](./workflows/minimax_h3_kijai_lightx2v_4step_i2v_sa_solver_illustration_1344x768_api.json) | illustration | — (not posted / local-only) |
  | [`battle`](./workflows/minimax_h3_kijai_lightx2v_4step_i2v_sa_solver_battle_1344x768_api.json) | battle | — (not posted / local-only) |

## Conclusion and measured results

All four themes generated successfully. Each output is `1344×768 / 158 frames / 24 fps / 6.583333 sec / H.264 + AAC`, with `blackdetect=0` and no OOM.

| Scene | Comfy execution | Runner wall | Output size | Black frames | Visual result |
|---|---:|---:|---:|---:|---|
| Car | 209.579 sec | 210.402 sec | 2,896,740 bytes | 0 | Preserved the car, road, and mountains; forward motion and camera tracking are visible. |
| Sports | 208.834 sec | 210.409 sec | 2,241,947 bytes | 0 | The athlete launches from the starting pose with a tracking camera. |
| Illustration | 208.941 sec | 210.505 sec | 2,328,790 bytes | 0 | Preserved the style, character, and path while clouds, light, and camera change. |
| Battle | 210.609 sec | 215.453 sec | 2,804,264 bytes | 0 | Preserved the two characters' positions and weapons while push-in, dust, and flag motion change. |

`Comfy execution` is measured from ComfyUI `execution_start` to `execution_success`. `Runner wall` is from the experiment runner start through report completion. Each value is also stored in its individual JSON report.

## Fixed conditions and runtime

Only the scene, ImageGen start image, I2V prompt, and seed changed between runs. The sampler was fixed to `sa_solver`, which was favorable in the earlier speed check; this is not a comparison against `er_sde`.

- GPU: NVIDIA GeForce RTX 4090, 24,564 MiB VRAM
- Docker Compose: service `h3-4090`, host port `8188`
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
- Low VRAM: `false`
- Dynamic VRAM: `false`
- SageAttention: `false` (not used in this 4090 experiment)
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
- Audio: AAC stereo from the official Audio VAE
- Normalized common graph SHA-256 for the four workflows (excluding scene prompt, seed, input image, and output prefix): `358EEAAA06B88FEC898C1A9A07FAFF05781AF6AF73FC3FC592838FB8888D9E55`

Each ImageGen start image is a `1672×941` PNG passed unchanged to the workflow's `LoadImage` node; the generation output is fixed at `1344×768`. The start-image prompts and SHA-256 values are saved in [`imagegen-prompts.md`](./imagegen-prompts.md).

## Reproduction

Run from the repository root:

```powershell
cd <repo-root>
docker compose --profile 4090 up -d h3-4090

.\scripts\run-h3-post-condition.ps1 `
  -Gpu 4090 -Port 8188 `
  -Workflow .\experiments\03-reference-conditioned\i2v-scenes\workflows\minimax_h3_kijai_lightx2v_4step_i2v_sa_solver_car_1344x768_api.json `
  -OutputPrefix video/MiniMax_H3_Kijai_LightX2V_I2V_1344x768_4step_sa_solver_scene_car `
  -LowVram $false -Seed -1 -TimeoutSeconds 14400
```

For sports, illustration, and battle, use the corresponding workflow and replace `OutputPrefix` with the value for that scene. The API workflows already contain the input image name and seed, so the run conditions do not change at invocation time. The machine-readable record is [`experiment.json`](./experiment.json).

## Four run records

### 1. Car

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
- Visual check: the first and middle frames both show one car, a continuous road, the mountain environment, and no black frame.

### 2. Sports

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
- Visual check: the first frame preserves the crouched starting pose; the middle frame shows launch and camera tracking, with no black frame.

### 3. Illustration

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

### 4. Battle

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
- Visual check: both original warriors remain separated with their weapons and arena composition; push-in, dust, cape/flag movement, and lightning atmosphere are visible, with no gore or black frame.

## Model reproducibility information

| File | Bytes | SHA-256 |
|---|---:|---|
| `models/diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors` | 20,970,379,616 | `E889202C41DAFB67B10D67B97F0D8541508036A6090AF23425A5C2615D03C47A` |
| `models/text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | 15,687,142,551 | `35A88D51044231FE332301D7A62AA81E3F2CBA62FEBEB446E2C1E3E0EF76F2C6` |
| `models/vae/minimax_h3_video_vae_fp16.safetensors` | 5,207,808,496 | `7C1F131492E7EDDACAAC9069A61B81BDD39DE5CC96561E677C5EAB1CDCE5E522` |
| `models/vae/minimax_h3_audio_vae_fp32.safetensors` | 605,254,808 | `8E505D95DD1561D47ABD43D4238FD40D9BB1AE9E147ED0A4CBA778D76AE4DB48` |
| `models/loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors` | 1,956,171,984 | `FC9B6500F0331FE925B004738BAAA31BD34104741C8BF9334816F9AC3005C8C1` |

## Visual checks and limitations

- The opening frame and a frame around 3.0 seconds were checked for all four outputs.
- `blackdetect` was `0` for all four. First-frame Y means were Car `103.278`, Sports `76.4329`, Illustration `110.668`, and Battle `64.2438`; none indicates an all-black signal.
- No quantitative evaluation was performed for image quality, long-term character/car consistency, or audio quality.
- The ImageGen start images are new local assets. Their prompts and SHA-256 values are stored, but ImageGen's internal randomness and model version were not fixed. This is therefore workflow reproduction using the stored PNGs, not an experiment that regenerates byte-identical PNGs in another environment.
- The X post does not specify the GPU, prompt, seed, sampler, scheduler, or workflow. `1344×768 / 24 fps / 158 frames` and Kijai's `4 steps / strength 0.75` were taken from the cited source; `sa_solver` and the scene prompts are explicitly this lab's conditions.

## Related records and public-evidence simulation

- [Kijai/LightX2V 4-step baseline experiment](../../02-low-step-generation/lightx2v-4step/README.md)
- [Sources and interpretation boundary](./sources.md) / [日本語](./sources.ja.md)
- [ImageGen start-image prompts](./imagegen-prompts.md) / [日本語 metadata](./imagegen-prompts.ja.md)

The X post simulation used these resources:

- Simulator: https://madesk.tail8be30.ts.net:8882/
- Payload: `sunwood-x-kijai-scenes-simulation-2026-08-08.json`
- Simulator source: `sunwood-x-simulator-kijai-scenes-2026-08-08/index.html`
- HyperFrames composition: `hyperframes-kijai-scenes-2026-08-08/index.html`
- Montage output: `hyperframes-kijai-scenes-2026-08-08/renders/MiniMax_H3_Kijai_LightX2V_scene_montage_1920x1080_24fps.mp4`
- Provenance: the parent overview video is evidence derived only from the four real generated MP4s arranged as a 2×2 montage. The reply videos use those same generated MP4s.
- Status: simulation only; nothing was posted to X.

The Japanese record is [`README.ja.md`](./README.ja.md), and the structured machine-readable record is [`experiment.json`](./experiment.json).
