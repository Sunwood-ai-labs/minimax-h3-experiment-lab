# RTX 3060 旧経路の黒画（2026-08-07）

- ID: `2026-08-07-3060-legacy-black-output`
- Status: `failed`
- GPU: RTX 3060 12GB
- Owner: `MiniMax-H3 Experiment Lab`

フレームタイル: [contact sheet](./previews/contact-sheet.jpg) / [manifest](./previews/contact-sheet.json)

## 仮説

最初に動かしたTurbo/full-int8構成が、RTX 3060のメモリ制約下でも動画を生成できるか確認した。

## 条件

- Turbo/full-int8 base
- Kijai experimental int8 video VAE
- Turbo sampler、8 steps
- RTX 3060
- Docker Compose上の旧runtime

## 結果

生成MP4は全フレームが黒信号だった。`blackdetect`と`signalstats`で黒画を確認し、Kijai int8 VAEだけを切り替えるA/Bも黒になった。

この経路は成功動画として採用せず、公式FP16 video VAE / FP32 audio VAEを使う条件へ切り替えた。切り替え後の再検証は[GPU基準比較](../gpu-baseline/README.md)に記録している。

## 証拠

- [verification-log.md](../../../verification-log.md) — 黒画の検査、CUDA OOM、復旧手順
- [research-notes.md](../../../research-notes.md) — 3060投稿の条件調査と原因切り分け
- 旧MP4がローカルruntimeに残っている場合は、生成物を再利用せず失敗証拠として扱う

## 再発防止

1. 投稿に記載されたVAEとPyTorch/CUDAの主要版を優先する。
2. 出力直後にffprobe、blackdetect、signalstats、抽出フレームを確認する。
3. 黒画やOOMを成功実験の結果表へ混ぜず、別の`failed`レコードへ分離する。
