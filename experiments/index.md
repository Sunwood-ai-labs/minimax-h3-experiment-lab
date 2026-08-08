# MiniMax-H3 Experiment Lab — Index

更新日: 2026-08-08 JST  
プロジェクト: `D:/Prj/minimax-h3-compose`

## 実験一覧

| 日付 | ID | GPU | 条件 | 状態 | 記録 |
|---|---|---|---|---|---|
| 2026-08-07 | `3060-tlanoai-864x480` | RTX 3060 | TlanoAI相当、25 steps、EasyCache、SageAttention | verified | [benchmark](../runtime/3060/benchmark/index.md) |
| 2026-08-07 | `3060-720p-t2v` | RTX 3060 | 1280×704、25 steps、WSL再起動後 | verified | [verification log](../verification-log.md) |
| 2026-08-07 | `3060-720p-i2v` | RTX 3060 | 1280×704、25 steps、imagegen開始フレーム | verified | [verification log](../verification-log.md) |
| 2026-08-07 | `4090-yume-832x480` | RTX 4090 | linked recipe、20 steps | verified | [benchmark](../runtime/4090/benchmark/index.md) |
| 2026-08-07 | `4090-720p-t2v` | RTX 4090 | 1280×704、25 steps | verified | [benchmark](../runtime/4090/benchmark/index.md) |
| 2026-08-07 | `4090-720p-i2v` | RTX 4090 | 1280×704、25 steps、同じ開始フレーム | verified | [benchmark](../runtime/4090/benchmark/index.md) |
| 2026-08-08 | `kijai-lightx2v-4step` | RTX 4090 | Kijai LightX2V LoRA、4 steps、strength 0.75、1344×768、T2V/I2V、er_sde/sa_solver | verified | [experiment](./2026-08-08/kijai-lightx2v-4step/README.md) |

## 既存結果の比較入口

| GPU | Mode | 解像度 | steps | runner wall | blackdetect |
|---|---|---:|---:|---:|---:|
| RTX 3060 | T2V | 1280×704 | 25 | 961.655 sec | 0 |
| RTX 3060 | I2V | 1280×704 | 25 | 800.840 sec | 0 |
| RTX 4090 | T2V | 1280×704 | 25 | 290.337 sec | 0 |
| RTX 4090 | I2V | 1280×704 | 25 | 275.309 sec | 0 |
| RTX 4090 | T2V Kijai | 1344×768 | 4 | 365.71 sec (`er_sde`) / 200.39 sec (`sa_solver`) | 0 |
| RTX 4090 | I2V Kijai | 1344×768 | 4 | 210.457 sec (`er_sde`) / 195.417 sec (`sa_solver`) | 0 |

この表は通常の25-step基準です。Kijai／LightX2V 4-stepは、画質・音声・samplerの互換性を別実験として比較します。

## ステータス定義

- `planned`: 条件と目的を定義済み、未実行
- `running`: 実行中または結果整理中
- `verified`: 実行成功、出力検査、条件記録が完了
- `partial`: 一部条件のみ実行、差分を明記
- `failed`: OOM、黒画、node errorなどを再現し原因を記録
