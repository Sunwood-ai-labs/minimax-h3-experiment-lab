# MiniMax-H3 I2V start-frame record

> 日本語版: [i2v_start_frame_generation.md](./i2v_start_frame_generation.md)

- Use: MiniMax-H3 I2V at 1280×704
- Generation: built-in image generation tool
- Source: `assets/i2v_start_frame_source.png`
- Runtime copies: `runtime/4090/input/MiniMax_H3_I2V_1280x704_start.png` and `runtime/3060/input/MiniMax_H3_I2V_1280x704_start.png`

## Image-generation prompt

The prompt is intentionally kept in English because it is the model input:

> Create a single photorealistic cinematic landscape image to use as the starting frame for MiniMax-H3 image-to-video. Wide 16:9 composition, approximately 720p framing: a calm Japanese mountain lake at sunrise, the sun just above a dark mountain ridge, warm golden light reflecting on still water, thin natural mist drifting over the lake, distant forest shoreline, detailed but stable geometry. No people, no animals, no buildings, no text, no logos, no watermark, no artificial lens distortion, no motion blur. Keep the scene visually coherent and easy for an image-to-video model to animate with gentle camera movement and mist.

## 1280×704 normalization

The source image was generated at 16:9, resized to 1280×720 with Lanczos, and cropped by 8 pixels at the top and bottom to satisfy the H3 32-pixel dimension alignment.

```powershell
ffmpeg -y -hide_banner -loglevel error -i assets/i2v_start_frame_source.png -vf "scale=1280:720:flags=lanczos,crop=1280:704:0:8" -frames:v 1 assets/i2v_start_frame_1280x704.png
```
