# MiniMax-H3 ref2va R2V — Sol-Attn + SageAttention + EasyCache

[English version](./README.md)

- Experiment ID: '2026-08-08-acceleration-sol-sage-easycache-4scenes-7s'
- Status: verified
- Scope: the existing 3-reference R2V experiment, four scenes, approximately seven seconds each
- GPU: RTX 4090, Docker Compose service 'h3-4090', port 8188

Frame tile: [contact sheet](./previews/contact-sheet.jpg) / [manifest](./previews/contact-sheet.json)

Record: [experiment.json](./experiment.json) · [tracked frame tile](./previews/contact-sheet.jpg)

![Attention and cache acceleration frame tile](./previews/contact-sheet.jpg)

> This tracked tile is the public visual evidence; the four optimized MP4s remain local-only capture artifacts.

## X動画・参照URL

- **生成動画投稿**: [X投稿](https://x.com/hAru_mAki_ch/status/2086051398735847471) — `uncertain`。投稿シミュレーションのURLで、4シーンの最適化済みMP4との添付対応は未確認。
- **参照元**: [公式R2V workflow](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json) / [SolAttn](https://github.com/kijai/ComfyUI-SolAttn_triton) / [KJNodes](https://github.com/kijai/ComfyUI-KJNodes) / [SageAttention](https://github.com/thu-ml/SageAttention) / [比較元のX投稿](https://x.com/sunbaolong_2001/status/2085689404031672372?s=46)
- **workflowと動画URLの対応**:

  | Workflow | Scene | X動画 |
  |---|---|---|
  | [`scene-01`](./workflows/scene-01-sunset-meeting_api.json) | sunset meeting | [X投稿](https://x.com/hAru_mAki_ch/status/2086051398735847471)（添付対応未確認） |
  | [`scene-02`](./workflows/scene-02-rainy-stairs_api.json) | rainy stairs | [X投稿](https://x.com/hAru_mAki_ch/status/2086051398735847471)（添付対応未確認） |
  | [`scene-03`](./workflows/scene-03-glasshouse-orbit_api.json) | glasshouse orbit | [X投稿](https://x.com/hAru_mAki_ch/status/2086051398735847471)（添付対応未確認） |
  | [`scene-04`](./workflows/scene-04-rooftop-pullback_api.json) | rooftop pull-back | [X投稿](https://x.com/hAru_mAki_ch/status/2086051398735847471)（添付対応未確認） |

## Conclusion

The working combination was integrated into the same MiniMaxH3ReferenceToVideo ref2va graph:

UNETLoader → EasyCache → PathchSageAttentionKJ (FP16 CUDA) → SolAttnPatch → BasicGuider/BasicScheduler

All four scenes completed at 1280×704, 175 frames, 24 fps, 20 steps, with the same three reference sheets and the same seeds as the baseline. The measured average was **353.145 seconds**, versus **738.794 seconds** for the baseline: **2.092× faster on average**. The best measured scene speedup was **2.141×**. The advertised 3.2× maximum was not reproduced under these exact ref2va conditions.

All four MP4 files are valid H.264 + AAC, 175 frames, 7.292 seconds, and had blackdetect interval count 0. No OOM or CUDA failure occurred in the final configuration.

## Result summary

| Configuration | Runs | Average time | Relative speed |
|---|---:|---:|---:|
| Baseline ref2va, no optimizer | 4 | 738.794 sec | 1.000× |
| EasyCache only diagnostic | 1 | 591.541 sec | 1.249× |
| Generic Sage FP16 CUDA + EasyCache diagnostic | 1 | 580.269 sec | 1.273× |
| Sol-Attn + generic Sage FP16 CUDA + EasyCache | 4 | 353.145 sec | **2.092×** |

The Sol-Attn timing includes the per-prompt autotune overhead. EasyCache skipped 7 or 8 of the 20 sampling steps depending on the scene.

## Optimizer settings

| Node | Parameters |
|---|---|
| EasyCache | reuse_threshold=0.3, start_percent=0.2, end_percent=0.9 |
| PathchSageAttentionKJ | sage_attention=sageattn_qk_int8_pv_fp16_cuda, allow_compile=false |
| SolAttnPatch | tau=1.3, start_percent=0.2, end_percent=0.9, min_tokens=4096, int8_qk=true, sink_conditioning=exact_kv_and_rows, int8_pv=true, morton=false, use_tma=false |

The 4090 service does not use ComfyUI's global --use-sage-attention flag. SageAttention is attached explicitly in each workflow to avoid an incompatible global patch on the H3 ref2va path.

## Four scene results

The baseline values are from [the previous verified 4-scene experiment](../../03-reference-conditioned/multi-reference-r2v-4scenes-7s/README.ja.md). The optimized values are from the saved reports.

| Scene | Description | Seed | Prompt ID | Baseline | Optimized | Speedup | EasyCache | Media |
|---:|---|---:|---|---:|---:|---:|---|---|
| 1 | Sunset rooftop meeting / dolly-in | 2026080813 | c89dcb38-d2ad-496b-8409-f204694d7406 | 738.494 sec | 349.394 sec | 2.114× | 7/20 | 1280×704, 175 frames, black 0 |
| 2 | Rainy exterior stairs / tracking shot | 2026080814 | d20498fe-66fc-4550-a14a-ca86987f4d2e | 738.442 sec | 365.705 sec | 2.019× | 7/20 | 1280×704, 175 frames, black 0 |
| 3 | Glasshouse conversation / half-orbit | 2026080815 | 4b4b201a-9502-497b-8b80-defd4c8667a1 | 739.257 sec | 352.304 sec | 2.098× | 8/20 | 1280×704, 175 frames, black 0 |
| 4 | Rooftop skyline / pull-back | 2026080816 | f9903bb3-52aa-442b-82c9-da2d4e5d1c04 | 738.981 sec | 345.178 sec | 2.141× | 8/20 | 1280×704, 175 frames, black 0 |

### Videos

- Scene 1 MP4 (local-only): `runtime/4090/output/video/MiniMax_H3_R2V_sol_fp16_scene_01_sunset_meeting_00001_.mp4` — 2,029,750 bytes, SHA-256 B1497DF7FBBD50FE4558A8EECE0B611EABBAD4FC35340497A1FCF4B921D07D8A
- Scene 2 MP4 (local-only): `runtime/4090/output/video/MiniMax_H3_R2V_sol_fp16_scene_02_rainy_stairs_00001_.mp4` — 2,255,836 bytes, SHA-256 054E3E26EE9819CA163FDDCF92C63F091A27F993645A85BE695B2A845C8212C8
- Scene 3 MP4 (local-only): `runtime/4090/output/video/MiniMax_H3_R2V_sol_fp16_scene_03_glasshouse_orbit_00001_.mp4` — 2,473,041 bytes, SHA-256 951DF63B8E7F0AF9DBA14C6FE15B0B0C09D10080CBA4EC9BCAD2D12EEC719C39
- Scene 4 MP4 (local-only): `runtime/4090/output/video/MiniMax_H3_R2V_sol_fp16_scene_04_rooftop_pullback_00001_.mp4` — 2,691,547 bytes, SHA-256 9C2297798EF326B114703E969E4F5CE6BC63D6554C8D6E53BC6E234712D110B7

Scene 1's official timing report is the independent diagnostic prompt c89dcb38... The later normalized-filename submission had the identical graph and seed and was served from ComfyUI's node cache in 3.137 seconds, so that cache replay is not used as a generation-performance result.

## Exact generation inputs

All four workflows use the same references in the same order:

1. Picture 1: rooftop greenhouse/background reference sheet
2. Picture 2: Mina character reference sheet
3. Picture 3: Ren character reference sheet

The full prompts are embedded in the API workflows. Scene prompt summary:

- Scene 1: sunset rooftop meeting, Ren enters from the greenhouse, slow dolly-in, preserve identities and wardrobe.
- Scene 2: sudden rain, Mina leads Ren down exterior stairs, backward tracking camera, wet reflections and realistic footwork.
- Scene 3: blue-hour greenhouse conversation, Mina removes a glove, Ren steps closer, slow half-orbit.
- Scene 4: night rooftop pull-back through the greenhouse doorway, the pair looks over the glowing city after rain.

## Reference assets

The stored PNGs are the reproducibility inputs; regenerating them would not be byte-identical.

| Order | Role | File | SHA-256 | Size |
|---:|---|---|---|---:|
| 1 | Background/location | [background reference sheet](../../03-reference-conditioned/multi-reference-r2v-4scenes-7s/references/MiniMax_H3_R2V_background_reference_sheet.png) | 5DA392A5655261637B1932CA5A6D6762A2ECF5682A01F1409063831981221038 | 1672×941, 2,545,156 bytes |
| 2 | Mina | [Mina reference sheet](../../03-reference-conditioned/multi-reference-r2v-4scenes-7s/references/MiniMax_H3_R2V_mina_reference_sheet.png) | 0D46C441160B8E7768F55D65926EB859D3500C21FD6472182FAEEB8AE09D4D6B | 1672×941, 2,180,477 bytes |
| 3 | Ren | [Ren reference sheet](../../03-reference-conditioned/multi-reference-r2v-4scenes-7s/references/MiniMax_H3_R2V_ren_reference_sheet.png) | 3449B9DEF4C05694ACC7C84EDF6DFD06A08F625CE7D094CBC8B195128A90FF36 | 1672×941, 1,967,565 bytes |

## Exact execution environment

### Host and GPU

| Item | Value |
|---|---|
| Host OS | Windows 11 Pro build 26200 |
| Host RAM | 137,270,165,504 bytes |
| WSL | WSL2 through Docker Desktop |
| Docker Engine | 29.4.3 |
| Docker Compose | 5.1.3 |
| NVIDIA driver | 591.86 |
| GPU | NVIDIA GeForce RTX 4090 |
| GPU UUID | GPU-f877fbc1-9f24-bd97-3359-dd358eaa2caa |
| VRAM | 24,564 MiB |
| Compose service | h3-4090 |
| Host port | 8188 |

### Container and runtime

| Item | Value |
|---|---|
| Image | local/minimax-h3-comfyui:v0.30.0 |
| Image digest | sha256:5bdcdbbe1c193f224739a10e186fbfc7ada5cb69e15e0f8399c6624ec1ce02c0 |
| ComfyUI | 0.30.0 |
| Python | 3.12.3 |
| PyTorch | 2.11.0+cu130 |
| CUDA base | 13.0 |
| cuDNN | 9 |
| CUDA module loading | LAZY |
| CUDA_LAUNCH_BLOCKING | 0 for the final run |
| H3_DEBUG_KJ_SAGE | 0 for the final run |
| Memory allocator | PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True |
| Shared memory | 16 GB |
| Model volume | ./models:/opt/ComfyUI/models:ro |
| Input/output volumes | runtime/4090/input and runtime/4090/output |
| ComfyUI arguments | --listen 0.0.0.0 --port 8188 --disable-pinned-memory --disable-async-offload --fp16-intermediates --preview-method none |

### Model and generation parameters

| Item | Value |
|---|---|
| Base model | minimax_h3_ref2va_pruned_int8_convrot.safetensors |
| Base model SHA-256 | 9255F52B6677845AD238F20DFAAFA94727053694127AB7F255C048F0F9365779 |
| Text encoder | qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors |
| Video VAE | minimax_h3_video_vae_fp16.safetensors |
| Audio VAE | minimax_h3_audio_vae_fp32.safetensors |
| LoRA | none |
| R2V node | MiniMaxH3ReferenceToVideo |
| Reference sizing | match |
| Resolution | 1280×704 |
| Frames / FPS | 175 / 24 fps |
| Duration | 7.292 seconds |
| Steps | 20 |
| Sampler | res_multistep |
| Scheduler | simple |
| Denoise | 1.0 |
| Audio | generated by H3 and encoded into MP4 |

### Pinned optimizer sources

- [ComfyUI-SolAttn_triton](https://github.com/kijai/ComfyUI-SolAttn_triton), pinned ref 0e334dc981cfe3b0ed926ee13ad43f64914b7f5b
- [ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes), pinned ref 60cd6bc1870db94c6eeb05fbe455147a8e91c4e9
- [SageAttention](https://github.com/thu-ml/SageAttention), installed wheel 2.2.0+cu130torch2.11

The Docker integration is recorded in [Dockerfile](../../../Dockerfile), [compose.yaml](../../../compose.yaml), and [patch-ref2va-optimizations.ps1](../../../scripts/patch-ref2va-optimizations.ps1).

## Reproduction

~~~powershell
cd <repo-root>
docker compose --profile 4090 build h3-4090
docker compose --profile 4090 up -d h3-4090

$base = '.\experiments\03-reference-conditioned\multi-reference-r2v-4scenes-7s'
Copy-Item -LiteralPath "$base\references\*.png" -Destination '.\runtime\4090\input' -Force
$exp = '.\experiments\04-acceleration\sol-sage-easycache-4scenes-7s'
$workflow = Get-Content "$exp\workflows\scene-02-rainy-stairs_api.json" -Raw | ConvertFrom-Json
$body = @{ prompt = $workflow; client_id = ([guid]::NewGuid().ToString()) } | ConvertTo-Json -Depth 100
$run = Invoke-RestMethod -Uri 'http://127.0.0.1:8188/prompt' -Method Post -ContentType 'application/json' -Body $body
$run.prompt_id
Invoke-RestMethod "http://127.0.0.1:8188/history/$($run.prompt_id)"
~~~

The helper used to create these workflows is [patch-ref2va-optimizations.ps1](../../../scripts/patch-ref2va-optimizations.ps1). A clean baseline workflow can be patched with SageMode generic and SageAttentionMode sageattn_qk_int8_pv_fp16_cuda.

Validate one MP4:

~~~powershell
$video = '.\runtime\4090\output\video\MiniMax_H3_R2V_sol_fp16_scene_02_rainy_stairs_00001_.mp4'
ffprobe -v error -show_entries format=duration,size $video
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,nb_frames,r_frame_rate,codec_name $video
ffmpeg -i $video -vf blackdetect=d=0.1:pix_th=0.10 -an -f null NUL
~~~

## Rejected optimizer variants

| Variant | Result |
|---|---|
| MiniMaxH3MemoryEfficientSageAttentionPatch + EasyCache | CUDA unspecified launch failure at the KJ H3 Sage out_proj path |
| H3-specific Sage with CUDA_LAUNCH_BLOCKING=1 | Same CUDA launch failure |
| H3-specific Sage + MiniMaxLowVRAMAttention(head_chunks=4) | CUDA failure at the KJ grouped assignment path |
| Generic PathchSageAttentionKJ with auto | Same CUDA launch failure on this H3 ref2va shape |
| Generic FP8 Sage modes | Not selected after the same context-specific failure pattern |
| Generic sageattn_qk_int8_pv_fp16_cuda + EasyCache | Successful, 580.269 seconds |
| Sol-Attn + generic FP16 CUDA Sage + EasyCache | Successful for all four final scenes |

The failing H3-specific route was separately tested with random and exact H3-shaped tensors successfully. The final choice is therefore the stable generic FP16 CUDA path, with the limitation that it is not the H3-specific FP8 implementation.

## Validation and limitations

- Final run: 4/4 successful.
- OOM: none.
- CUDA launch failures in final run: none.
- blackdetect: 0 intervals for all four MP4s.
- VAE runtime patch logged finite audio/video tensors for all four final outputs.
- signalstats first-frame values were non-black for all four outputs.
- No blind human preference score or identity-preservation score was measured.
- Sol-Attn is approximate attention; visually compare the outputs with the baseline before claiming no quality loss.
- The advertised 3.2× figure was not reproduced here; the maximum observed was 2.141× and the four-scene mean was 2.092×.
- Re-running the identical graph and seed immediately can hit ComfyUI node cache. Use the saved report and prompt ID, or restart the service before timing a fresh generation.

## Evidence files

- [experiment.json](./experiment.json)
- [submitted.json](./submitted.json)
- [Scene 1 workflow](./workflows/scene-01-sunset-meeting_api.json)
- [Scene 2 workflow](./workflows/scene-02-rainy-stairs_api.json)
- [Scene 3 workflow](./workflows/scene-03-glasshouse-orbit_api.json)
- [Scene 4 workflow](./workflows/scene-04-rooftop-pullback_api.json)
- [Scene 1 timing/media report](../../../runtime/4090/benchmark/h3-c89dcb38-d2ad-496b-8409-f204694d7406.md)
- [Scene 2 timing/media report](../../../runtime/4090/benchmark/h3-d20498fe-66fc-4550-a14a-ca86987f4d2e.md)
- [Scene 3 timing/media report](../../../runtime/4090/benchmark/h3-4b4b201a-9502-497b-8b80-defd4c8667a1.md)
- [Scene 4 timing/media report](../../../runtime/4090/benchmark/h3-f9903bb3-52aa-442b-82c9-da2d4e5d1c04.md)

## Source links

- [Official ComfyUI MiniMax-H3 R2V workflow](https://github.com/Comfy-Org/workflow_templates/blob/main/templates/video_minimax_h3_r2v.json)
- [Comfy-Org MiniMax-H3 model files](https://huggingface.co/Comfy-Org/MiniMax-H3)
- [Kijai MiniMax-H3 Comfy repository](https://huggingface.co/Kijai/MiniMax-H3_comfy)
- [Kijai ComfyUI-SolAttn_triton](https://github.com/kijai/ComfyUI-SolAttn_triton)
- [Kijai ComfyUI-KJNodes](https://github.com/kijai/ComfyUI-KJNodes)
- [Official SageAttention repository](https://github.com/thu-ml/SageAttention)
- [参考元Xポスト: Sol-Attn + SageAttention + EasyCacheによるMiniMax-H3高速化報告](https://x.com/sunbaolong_2001/status/2085689404031672372?s=46)
