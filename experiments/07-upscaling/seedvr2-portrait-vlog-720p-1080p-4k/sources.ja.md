# 出典とImage Genプロンプト

## モデル・続編の参照

- SeedVR2公式配布元: <https://huggingface.co/Comfy-Org/SeedVR2>
- 前回の実験記録: [`../seedvr2-4k-rtx4090/experiment.json`](../seedvr2-4k-rtx4090/experiment.json)
- 前回参照投稿: <https://x.com/aihonobono2023/status/2086281213334213104?s=46>

前回記録を直接の続編コンテキストとした。今回はH3動画workflowを再実行せず、縦長の1枚画像に対するアップスケールだけを切り出している。

## 生成素材

- ツール: built-in `image_gen` tool mode
- 素材: `runtime/4090/input/seedvr2_portrait_vlog_imagegen_source.png`
- 生成時解像度: `1024×1536`
- SHA-256: `5B80668C03FD2FF362849B7255E279171BABF6DC041AF3BFCEE5599288516980`
- 役割: アップスケール比較用の架空の成人自撮りVlog素材

### 使用プロンプト

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

## 固定した変換

生成した1024×1536画像を`workflows/prepare_portrait_720p_api.json`で中央crop＋Lanczosにより720×1280へ変換した。その720p PNGをComfyUIのinput mountへコピーし、1080pと4Kの両方で同じ入力を再利用した。1080p／4K workflowはtarget canvasへLanczos resizeした後にSeedVR2を1 pass実行している。
