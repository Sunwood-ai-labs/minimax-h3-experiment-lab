# X投稿シミュレーション（未投稿）

## 本文案

MiniMax-H3をDocker Composeで検証。

RTX 3060 12GBでWSL再起動後、約720p（1280×704）を生成してみた。

T2V：25 steps / 16分01秒  
I2V：25 steps / 13分16秒

どちらもOOMなし、blackdetectも0。I2Vはimagegenで作った開始フレームから生成。

3060でも約720pいけた。

#ONIZUKA_AGI

## 返信・補足案

条件はpruned int8 base、NVFP4 text encoder、公式FP16 video VAE / FP32 audio VAE、res_multistep / simple、EasyCache 0.3 / 0.2 / 0.9、124 frames / 24fps。

T2Vはrunner wall 961.655秒、I2Vは800.840秒。実験ログと生成動画はDocker Composeプロジェクトに保存済み。

## 根拠ファイル

- `runtime/3060/benchmark/h3-291fee87-c0b1-4cf3-a63c-df62f5ee6262.md`
- `runtime/3060/benchmark/h3-b6ab37fa-1af5-4f45-b7e3-7d92d34056a9.md`
- `benchmark-results-2026-08-07.json`
- `verification-log.md`

投稿状態: 未投稿。実際に投稿する場合は、本文と添付動画を確認してから実行する。
