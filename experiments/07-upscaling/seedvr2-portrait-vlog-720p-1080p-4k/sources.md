# Sources and Image Gen prompt

## Model and continuation references

- SeedVR2 official distribution: <https://huggingface.co/Comfy-Org/SeedVR2>
- Previous experiment record: [`../seedvr2-4k-rtx4090/experiment.json`](../seedvr2-4k-rtx4090/experiment.json)
- Previous reference post: <https://x.com/aihonobono2023/status/2086281213334213104?s=46>

The previous record is the direct continuation context. Its exact H3 video workflow is not rerun here; this record isolates a single portrait image workload.

## Generated source asset

- Tool: built-in `image_gen` tool mode
- Asset: `runtime/4090/input/seedvr2_portrait_vlog_imagegen_source.png`
- Generated resolution: `1024×1536`
- SHA-256: `5B80668C03FD2FF362849B7255E279171BABF6DC041AF3BFCEE5599288516980`
- Role: fictional adult selfie-vlog source image for the upscaling comparison

### Prompt used

```text
Use case: photorealistic-natural
Asset type: source image for a vertical AI upscaling experiment
Primary request: Create one portrait-oriented, photorealistic lifestyle vlog selfie frame that feels like a candid creator's handheld smartphone capture.
Scene/backdrop: A bright contemporary Japanese neighborhood café street in late afternoon, softly blurred storefronts and greenery in the background.
Subject: A fictional adult East Asian woman in her 20s, casual neutral-toned hoodie and light jacket, holding a smartphone at arm's length for a selfie, friendly relaxed expression, natural face and skin texture.
Style/medium: Natural smartphone vlog photography, subtle wide-angle selfie perspective, realistic handheld framing, authentic social-video still, not a polished studio portrait.
Composition/framing: Vertical 2:3 portrait composition, head and shoulders in the upper-middle, one hand and a small portion of the phone visible near the edge, enough background detail for upscaling comparison, slightly imperfect selfie framing.
Lighting/mood: Soft warm late-afternoon daylight, candid, upbeat, approachable.
Color palette: Natural warm neutrals with muted greens and café tones.
Materials/textures: Realistic hair strands, skin pores, hoodie fabric, glass and foliage detail, moderate depth of field.
Text (verbatim): none.
Constraints: Keep one person only, adult subject, stable facial identity, natural anatomy, no exaggerated beauty retouching, no visible brand logos, no signs or readable text, no watermark.
Avoid: extra fingers, duplicated hands, warped phone, plastic skin, beauty-ad look, heavy bokeh that removes all background detail, collage, illustration, anime, text, subtitles, logos, watermark.
```

## Fixed local transformation

The generated 1024×1536 source was center-cropped and Lanczos-resized to a 720×1280 baseline using `workflows/prepare_portrait_720p_api.json`. That exact 720p PNG was copied into the ComfyUI input mount and reused for both SeedVR2 runs. The 1080p and 4K workflows then resize to the target canvas before the SeedVR2 pass.
