# MiniMax-H3 GPU基準比較（2026-08-07）

English: [README.md](./README.md)

- ID: `2026-08-07-gpu-baseline`
- Status: `verified`
- GPU: RTX 3060 / RTX 4090
- Owner: `MiniMax-H3 Experiment Lab`

フレームタイル: [contact sheet](./previews/contact-sheet.jpg) / [manifest](./previews/contact-sheet.json)

Record: [experiment.json](./experiment.json) · [tracked frame tile](./previews/contact-sheet.jpg)

![GPU baseline frame tile](./previews/contact-sheet.jpg)

> This tracked tile is the public visual evidence; source MP4s under `runtime/*/output` remain local-only.

## X動画・参照URL

- **生成動画**: [3060 T2V](https://x.com/hAru_mAki_ch/status/2085730512677855266) / [3060 I2V](https://x.com/hAru_mAki_ch/status/2085731260169953315) / [4090 T2V](https://x.com/hAru_mAki_ch/status/2085738947553185852) / [4090 I2V](https://x.com/hAru_mAki_ch/status/2085738981866811714)
- **参照元**: [TlanoAIの3060投稿](https://x.com/TlanoAI/status/2084940455809286397) / [yume_arasakiの4090投稿](https://x.com/yume_arasaki/status/2084766655331360999) / [4090 recipe](https://github.com/yume-arasaki/RTX-4090-3090-Minimax-H3-15s)
- **調査候補（条件不足のため採用せず）**: [lizikk_zhu](https://x.com/lizikk_zhu/status/2084859489115648336) / [thekhoma](https://x.com/thekhoma/status/2084504336173076800) / [onigirikila](https://x.com/onigirikila/status/2084858171462754672)
- **runと動画URLの対応**:

  | Run | X動画 | 状態 |
  |---|---|---|
  | RTX 3060 T2V 1280×704（WSL再起動後） | [X動画](https://x.com/hAru_mAki_ch/status/2085730512677855266) | 投稿済み |
  | RTX 3060 I2V 1280×704（WSL再起動後） | [X動画](https://x.com/hAru_mAki_ch/status/2085731260169953315) | 投稿済み |
  | RTX 4090 T2V 1280×704 | [X動画](https://x.com/hAru_mAki_ch/status/2085738947553185852) | 投稿済み |
  | RTX 4090 I2V 1280×704 | [X動画](https://x.com/hAru_mAki_ch/status/2085738981866811714) | 投稿済み |
  | 3060/4090のその他のbaseline run | — | local-only |

  この実験は個別workflow READMEではなく、run単位で記録しているため、URLは上表で実測runへ直接対応づけている。

## 目的

RTX 3060とRTX 4090を別Compose serviceで動かし、投稿・linked recipeに対応する基準条件と、約720p級のT2V/I2Vを比較する。

## 出典

- RTX 3060: [TlanoAIの投稿](https://x.com/TlanoAI/status/2084940455809286397)
- RTX 4090: [yume_arasakiの投稿](https://x.com/yume_arasaki/status/2084766655331360999)
- RTX 4090 recipe: [RTX-4090-3090-Minimax-H3-15s](https://github.com/yume-arasaki/RTX-4090-3090-Minimax-H3-15s)
- 詳細な時系列: [verification-log.md](../../../verification-log.md)
- X調査の根拠: [research-notes.md](../../../research-notes.md)

## 実験条件

- Docker Compose service: `h3-3060` / `h3-4090`
- Host: Windows 11 + WSL2 + Docker Desktop
- Container: PyTorch 2.11.0 + CUDA 13.0 + cuDNN 9
- 3060投稿相当: 864×480、124 frames、24fps、25 steps
- 4090 linked recipe: 832×480、124 frames、24fps、20 steps
- 約720p級: 1280×704、124 frames、24fps、25 steps
- 3060: Dynamic VRAM / CPU offload / SageAttention / EasyCache
- 4090: `memory_usage_factor=1.0` / pinned memory無効 / fp16 intermediates
- 3060と4090は同一時刻の速度比較ではなく、各条件の実測記録として扱う

## 実行結果

| Run | Status | runner wall | 出力検査 |
|---|---|---:|---|
| RTX 3060 TlanoAI cold 864×480 | success | 425.526 sec | blackdetectなし、正常信号 |
| RTX 3060 TlanoAI warm inference 864×480 | success | 270.289 sec | blackdetectなし、正常信号 |
| RTX 4090 linked recipe 832×480 | success | 255.350 sec | blackdetectなし、正常信号 |
| RTX 4090 T2V 1280×704 | success | 290.337 sec | blackdetectなし、目視確認 |
| RTX 4090 I2V 1280×704 | success | 275.309 sec | blackdetectなし、目視確認 |
| RTX 3060 I2V 864×480 | success | 375.399 sec | blackdetectなし、目視確認 |
| RTX 3060 T2V 1280×704（WSL再起動後） | success | 961.655 sec | blackdetectなし、OOMなし |
| RTX 3060 I2V 1280×704（WSL再起動後） | success | 800.840 sec | blackdetectなし、OOMなし |

## 結論と制限

- RTX 3060は、正しいVAEとPyTorch/CUDA条件へ切り替えた後、1280×704 T2V/I2Vを完走した。
- RTX 4090は同じ1280×704級で3060より短いが、GPU・条件が異なるため単純な倍率では結論づけない。
- 842×480のX本文と832×480の4090 recipeは異なるため、4090はrecipe再現として記録する。
- 旧Turbo/full-int8の黒画は別の`failed`レコードに分離した。
