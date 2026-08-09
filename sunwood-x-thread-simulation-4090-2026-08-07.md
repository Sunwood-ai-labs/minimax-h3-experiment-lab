# Sunwood X投稿シミュレーション — MiniMax-H3 RTX 4090 続編

作成日: 2026-08-07 JST  
対象: `@hAru_mAki_ch`  ���目的: 前回のRTX 3060投稿に続く、RTX 4090のT2V/I2V実験投稿

## 状態

`posted_after_approval`。ユーザー承認後、4090編のX API書き込みと実投稿検証まで完了した。  
確認画面: `https://madesk.tail8be30.ts.net:8880/`

## 投稿単位

動画を1本ずつメイン投稿に添付し、T2VとI2Vを別スレッドにする。

### Thread A — RTX 4090 T2V

メイン投稿（URLなし）:

```text
MiniMax-H3 × Docker Compose、RTX 4090で約720p T2Vやってみた！！！

3060編と同じ1280×704・25 steps・124 framesで生成。
実測wall 4分50秒、OOMなし、blackdetectも0。

4090、約720pでも4分台。これは速い🔥
```

添付動画:

- 実体: `<repo-root>\runtime\4090\output\video\MiniMax_H3_T2V_4090_1280x704_25step_easycache_sage_cu130_00001_.mp4`
- サイズ: 746,645 bytes
- SHA-256: `368E54C5FFD22EBD6DD901BC1C3800AA1470AA83EBC43EDBAA529C3B4C223D90`
- 1280×704 / 24 fps / 124 frames / 5.167秒
- 実測wall: 290.337秒（約4分50秒）
- `blackdetect` interval_count: 0

返信1（3060編への継続リンク）:

```text
3060の約720p T2Vから続けて、4090でも同じ解像度・フレーム数を確認したぞ。
https://x.com/hAru_mAki_ch/status/2085730512677855266
```

返信2（成果物リンク）:

```text
4090のComfyUI実験ログ。workflow、Compose環境、処理時間、出力SHA-256まで記録しているぞ。
https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo
```

### Thread B — RTX 4090 I2V

メイン投稿（URLなし）:

```text
MiniMax-H3 × imagegen、RTX 4090で約720p I2Vやってみた！！！

3060編と同じ開始フレームで、1280×704・25 steps・124 framesを生成。
実測wall 4分35秒、OOMなし、blackdetectも0。

I2Vも4分台。4090強い🔥
```

添付動画:

- 実体: `<repo-root>\runtime\4090\output\video\MiniMax_H3_I2V_4090_1280x704_25step_easycache_sage_cu130_00001_.mp4`
- サイズ: 1,098,548 bytes
- SHA-256: `8D99CA9A3ABD3B836AED8E694DA0D7B885C1770BC208241CD33B13637E60A39B`
- 1280×704 / 24 fps / 124 frames / 5.167秒
- 実測wall: 275.309秒（約4分35秒）
- `blackdetect` interval_count: 0
- 開始フレーム: `<repo-root>\runtime\4090\input\MiniMax_H3_I2V_1280x704_start.png`
- 開始フレームSHA-256: `BE63F90186D46A2860A463C70E4E3E76FDF95A19E98F9DB9E696CD7610D96CD8`

返信1（3060編への継続リンク）:

```text
3060の約720p I2Vから続けて、同じ開始フレームで4090も確認したぞ。
https://x.com/hAru_mAki_ch/status/2085731260169953315
```

返信2（成果物リンク）:

```text
4090のI2V実験ログ。workflow、Compose環境、処理時間、出力SHA-256まで記録しているぞ。
https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo
```

## 再現環境の要約

- OS: Windows 11 Pro, build 26200
- Docker Desktop: 29.4.3
- Docker Compose: 5.1.3
- Compose service: `h3-4090`
- Image: `local/minimax-h3-comfyui:v0.30.0`
- ComfyUI: 0.30.0
- PyTorch: 2.11.0+cu130
- GPU: NVIDIA GeForce RTX 4090, 24,564 MiB
- 解像度: 1280×704
- frames: 124
- steps: 25
- sampler: `res_multistep`
- scheduler: `simple`
- low VRAM: false
- dynamic VRAM: false
- SageAttention requested: false
- CUDA module loading: `LAZY`
- T2V workflow: `<repo-root>\workflows\tlanoai_t2v_1280x704_api.json`
- I2V workflow: `<repo-root>\workflows\tlanoai_i2v_1280x704_api.json`

詳細な環境スナップショットとモデルSHA-256は、各実験レポートに保存済み。

- T2V: `<repo-root>\runtime\4090\benchmark\h3-061443d7-6d6f-43b3-8a5c-16e65c25c655.md`
- I2V: `<repo-root>\runtime\4090\benchmark\h3-f26da7d6-5f00-4cd0-bd18-b384e5ffa4e1.md`

## 投稿結果

- 対象アカウントは `@hAru_mAki_ch` 固定
- メイン投稿はURLなし
- 各メイン投稿の動画は1本だけ
- 返信は直前の投稿へ線形に接続
- 各返信のURLは1個だけ
- 3060編の実投稿履歴6件をローカル履歴で照合済み
- 4090編の実投稿6件をローカル履歴へ保存済み
- T2Vメインの動画メディアキーは1個、I2Vメインの動画メディアキーは1個
- X APIのinspectで、各返信が直前の投稿へ線形接続されていることを確認済み

### RTX 4090 T2V

- [メイン投稿](https://x.com/hAru_mAki_ch/status/2085738947553185852)
- [継続返信](https://x.com/hAru_mAki_ch/status/2085738954297671742)
- [成果物返信](https://x.com/hAru_mAki_ch/status/2085738961922838758)

### RTX 4090 I2V

- [メイン投稿](https://x.com/hAru_mAki_ch/status/2085738981866811714)
- [継続返信](https://x.com/hAru_mAki_ch/status/2085739613822554370)
- [成果物返信](https://x.com/hAru_mAki_ch/status/2085739628112597447)

## preflight・実投稿検証

2026-08-07 JST、Tailscale公開URLを指定して実行済み。

- T2V: `ok: true` — メイン154文字、返信98/113文字、動画1280×704・H.264・124 frames
- I2V: `ok: true` — メイン149文字、返信94/109文字、動画1280×704・H.264・124 frames
- Simulator: `https://madesk.tail8be30.ts.net:8880/` — HTTP 200
- T2V動画の公開コピーSHA-256: `368E54C5FFD22EBD6DD901BC1C3800AA1470AA83EBC43EDBAA529C3B4C223D90`
- I2V動画の公開コピーSHA-256: `8D99CA9A3ABD3B836AED8E694DA0D7B885C1770BC208241CD33B13637E60A39B`
- ペイロードSHA-256: `1DDA4A20E40C5C363B10BE2B9A26146180A75B5916D8E886CBB204B6AF1CF1C8`
- 実投稿inspect: 6件すべて取得成功
- T2Vメイン: media key 1個、継続返信の引用先は3060 T2V、成果物返信のURLはGitHub
- I2Vメイン: media key 1個、継続返信の引用先は3060 I2V、成果物返信のURLはGitHub

ペイロード: `<repo-root>\sunwood-x-thread-payload-4090-2026-08-07.json`
