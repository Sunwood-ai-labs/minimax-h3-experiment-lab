# MiniMax-H3 Experiment Lab — 実験台帳

更新日: 2026-08-09 JST
プロジェクト: `D:/Prj/minimax-h3-compose`

このページは「何を、どの条件で、どこまで確認したか」を時系列で追う入口です。詳細な条件・prompt・workflow・出力SHA-256・処理時間は各実験ディレクトリの`README.md`と`experiment.json`を正本とします。

## テーマ別の入口

- [基準条件とGPU比較](#2026-08-07--基準条件)
- [Kijai / LightX2V / ref2va](#2026-08-08--kijai--lightx2v--ref2va)
- [複数リファレンスR2Vと高速化](#2026-08-08--複数リファレンスr2vと高速化)
- [Motion Contextと動画連鎖](#2026-08-09--motion-contextと動画連鎖)
- [日本語Vlogと音楽MV](#2026-08-09--日本語vlogと音楽mv)

## ステータス定義

- `planned`: 条件と目的を定義済み、未実行
- `running`: 実行中または結果整理中
- `verified`: 実行成功、出力検査、条件記録が完了
- `partial`: 一部条件のみ実行、差分を明記
- `failed`: OOM、黒画、node errorなどを再現し原因を記録

## 2026-08-07 — 基準条件

この日の初期実験は、GPU別benchmark台帳と時系列ログを中心に保存しています。

| ID | GPU | 条件 | 結果 | 記録 |
|---|---|---|---|---|
| `3060-tlanoai-864x480` | RTX 3060 | 864×480、25 steps、EasyCache、SageAttention | verified | [基準記録](./2026-08-07/minimax-h3-baseline/README.md) / [benchmark](../runtime/3060/benchmark/index.md) |
| `3060-720p-t2v` | RTX 3060 | 1280×704、25 steps、WSL再起動後 | verified | [基準記録](./2026-08-07/minimax-h3-baseline/README.md) |
| `3060-720p-i2v` | RTX 3060 | 1280×704、25 steps、ImageGen開始フレーム | verified | [基準記録](./2026-08-07/minimax-h3-baseline/README.md) |
| `4090-yume-832x480` | RTX 4090 | linked recipe、20 steps | verified | [基準記録](./2026-08-07/minimax-h3-baseline/README.md) / [benchmark](../runtime/4090/benchmark/index.md) |
| `4090-720p-t2v` | RTX 4090 | 1280×704、25 steps | verified | [基準記録](./2026-08-07/minimax-h3-baseline/README.md) |
| `4090-720p-i2v` | RTX 4090 | 1280×704、25 steps、同じ開始フレーム | verified | [基準記録](./2026-08-07/minimax-h3-baseline/README.md) |
| `3060-legacy-black-output` | RTX 3060 | 旧Turbo/full-int8 + Kijai int8 VAE | failed | [失敗記録](./2026-08-07/legacy-3060-black-output/README.md) |

### 主要な基準時間

| GPU | Mode | 解像度 | steps | runner wall |
|---|---|---:|---:|---:|
| RTX 3060 | T2V | 1280×704 | 25 | 961.655 sec |
| RTX 3060 | I2V | 1280×704 | 25 | 800.840 sec |
| RTX 4090 | T2V | 1280×704 | 25 | 290.337 sec |
| RTX 4090 | I2V | 1280×704 | 25 | 275.309 sec |

最初の3060黒画は正しい成功結果ではありません。旧経路を除外し、投稿条件に合わせた公式FP16/FP32 VAEで再検証しました。

## 2026-08-08 — Kijai / LightX2V / ref2va

| ID | GPU | 条件 | 状態 | 記録 |
|---|---|---|---|---|
| `kijai-lightx2v-4step` | RTX 4090 | Kijai LightX2V LoRA、strength 0.75、4 steps、1344×768、T2V/I2V | verified | [実験記録](./2026-08-08/kijai-lightx2v-4step/README.md) |
| `kijai-scenes-i2v` | RTX 4090 | ImageGen開始フレームの車・スポーツ・イラスト・バトル、4 steps | verified | [実験記録](./2026-08-08/kijai-scenes/README.md) |
| `kijai-ref2va-6v20` | RTX 4090 | ref2va、LoRA strength 0.8、6/20 steps、T2V/I2V、1344×768 | verified | [実験記録](./2026-08-08/kijai-ref2va-6v20/README.md) |

6/20 stepsのSSIMはT2V `0.683275`、I2V `0.684799`です。これはシーン成立の確認であり、画質同等の証明ではありません。

## 2026-08-08 — 複数リファレンスR2Vと高速化

| ID | GPU | 条件 | 状態 | 記録 |
|---|---|---|---|---|
| `kijai-r2v-multi-reference-4scenes-7s` | RTX 4090 | 背景＋人物2人の3リファレンス、4シーン、約7秒 | verified | [ベースライン](./2026-08-08/kijai-r2v-multi-reference-4scenes-7s/README.md) |
| `kijai-r2v-sol-generic-fp16-sage-easycache-4scenes-7s` | RTX 4090 | Sol-Attn + 汎用FP16 CUDA SageAttention + EasyCache | verified | [高速化](./2026-08-08/kijai-r2v-sol-generic-fp16-sage-easycache-4scenes-7s/README.md) |

高速化実験は、同条件の4シーンで平均`738.7935 → 353.14525 sec`、平均`2.092倍`でした。参照投稿の最大3.2倍は、このDocker・RTX 4090・ref2va条件では再現していません。H3専用FP8/auto経路などの失敗診断も同じJSONに残しています。

## 2026-08-09 — Motion Contextと動画連鎖

| ID | GPU | 条件 | 状態 | 記録 |
|---|---|---|---|---|
| `niko-h3-motion-context-3segment` | RTX 4090 | 固定seed、映像＋音声latent、22フレーム引き継ぎ、3セグメント | verified | [実験記録](./2026-08-09/niko-h3-motion-context-3segment/README.md) |
| `h3-japanese-catcafe-vlog-5segment` | RTX 4090 | 英語prompt＋日本語セリフ、5セグメント、約30秒 | verified | [実験記録](./2026-08-09/h3-japanese-catcafe-vlog-5segment/README.md) |
| `h3-mv-jpop-5segment` | RTX 4090 | H3生成音声、123 BPM解析、HyperFramesリリックモーション、約29秒 | verified | [実験記録](./2026-08-09/h3-mv-jpop-5segment/README.md) |

Motion Contextの実装元は[ComfyUI-H3-Motion-Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context)、実験に使用したrevisionは各JSONに固定しています。

## 成果物・再現入口

- GPU別の詳細レポート: [runtime/3060](../runtime/3060/benchmark/index.md)、[runtime/4090](../runtime/4090/benchmark/index.md)
- 共有workflow: [workflows](../workflows)
- 実験テンプレート: [experiments/_template](./_template/README.md)
- X用の動画・投稿payload: [social/README](../social/README.md)

## 次の実験を追加するとき

```powershell
Copy-Item experiments/_template experiments/2026-08-09/my-experiment -Recurse
# README.md / experiment.json / sources.md / workflow / 成果物を記録
.\scripts\validate-experiment-lab.ps1
```

実験の結論には、完全再現・部分一致・未検証を明示します。GPUや解像度が違う結果は、同一条件の速度比較として扱いません。
