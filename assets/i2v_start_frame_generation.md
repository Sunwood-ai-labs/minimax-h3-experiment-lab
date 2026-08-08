# MiniMax-H3 I2V 開始フレーム記録

用途: MiniMax-H3 I2V 1280×704
生成方式: built-in imagegen
生成元: assets/i2v_start_frame_source.png
実行用: assets/i2v_start_frame_1280x704.png
runtimeコピー: runtime/4090/input/MiniMax_H3_I2V_1280x704_start.png、runtime/3060/input/MiniMax_H3_I2V_1280x704_start.png

## imagegen prompt

Create a single photorealistic cinematic landscape image to use as the starting frame for MiniMax-H3 image-to-video. Wide 16:9 composition, approximately 720p framing: a calm Japanese mountain lake at sunrise, the sun just above a dark mountain ridge, warm golden light reflecting on still water, thin natural mist drifting over the lake, distant forest shoreline, detailed but stable geometry. No people, no animals, no buildings, no text, no logos, no watermark, no artificial lens distortion, no motion blur. Keep the scene visually coherent and easy for an image-to-video model to animate with gentle camera movement and mist.

## 1280×704整形

元画像は16:9で生成した。H3のwidth/height 32刻みに合わせ、ffmpegで1280×720へLanczos縮小した後、上下8pxずつcropして1280×704にした。

~~~powershell
ffmpeg -y -hide_banner -loglevel error -i assets/i2v_start_frame_source.png -vf "scale=1280:720:flags=lanczos,crop=1280:704:0:8" -frames:v 1 assets/i2v_start_frame_1280x704.png
~~~

実行用PNG:

- size: 1280×704
- pixel format: rgb24
- SHA-256: BE63F90186D46A2860A463C70E4E3E76FDF95A19E98F9DB9E696CD7610D96CD8
- bytes: 1081736

864×480比較用PNGも同じimagegen sourceから作成した。1280×704と同じく、元画像を864×486へLanczos縮小して上下3pxずつcropした。

~~~powershell
ffmpeg -y -hide_banner -loglevel error -i assets/i2v_start_frame_source.png -vf "scale=864:486:flags=lanczos,crop=864:480:0:3" -frames:v 1 assets/i2v_start_frame_864x480.png
~~~

- execution input: runtime/3060/input/MiniMax_H3_I2V_864x480_start.png
- SHA-256: 6E075DDA3C2E5D1F7B0A9E2C1422504A11CFF353947BB10C348628F5237B7F58

1280×704 I2V workflowのLoadImageはfilename MiniMax_H3_I2V_1280x704_start.pngをruntime/GPU/inputから読み込む。864×480比較workflowはMiniMax_H3_I2V_864x480_start.pngを読み込む。
