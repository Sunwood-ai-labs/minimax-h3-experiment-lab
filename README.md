# MiniMax-H3 Experiment Lab

MiniMax-H3をDocker Compose + ComfyUIで動かし、RTX 3060とRTX 4090の条件差、LoRA、ref2va/R2V、Motion Context、音声付き動画生成を再現可能な実験記録として蓄積するラボです。

実験の正本は、実験ごとの`experiment.json`と`README.md`です。生成物の見た目だけでなく、出典、固定条件、Docker環境、workflow、処理時間、出力検査、SHA-256、未検証項目まで同じ場所に残します。

## まずここを見る

- [実験台帳](./experiments/index.md) — 2026-08-07以降の全実験への入口
- [ラボ運用ガイド](./LAB.md) — 新しい実験を追加する手順と記録契約
- [X投稿・シミュレーター一覧](./social/README.md) — 投稿用の動画・payload・シミュレーター
- [3060 benchmark](./runtime/3060/benchmark/index.md) / [4090 benchmark](./runtime/4090/benchmark/index.md)
- [調査メモ](./research-notes.md) / [検証ログ](./verification-log.md)

## ここまでの結論

| テーマ | 確認できたこと | 主な記録 |
|---|---|---|
| 3060 / 4090基準 | RTX 3060でもWSL再起動後の1280×704 T2V/I2Vを完走。RTX 4090は同条件でより短い | [benchmark台帳](./experiments/index.md#2026-08-07--基準条件) |
| 4-step LightX2V | 4 steps、1344×768、T2V/I2V、`er_sde`/`sa_solver`をRTX 4090で検証 | [実験記録](./experiments/02-low-step-generation/lightx2v-4step/README.md) |
| ref2va 6 vs 20 steps | T2V/I2Vの速度とSSIMを比較。速さだけで画質同等とは結論づけていない | [実験記録](./experiments/03-reference-conditioned/ref2va-6v20/README.md) |
| 複数リファレンスR2V | 背景＋人物2人の3リファレンスで4シーンを生成 | [実験記録](./experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s/README.md) |
| Sol-Attn + Sage + EasyCache | 同じR2V条件で平均2.092倍。参照投稿の最大3.2倍はこの条件では再現していない | [高速化記録](./experiments/04-acceleration/sol-sage-easycache-4scenes-7s/README.md) |
| Motion Context | 映像・音声コンテキストとlatentを22フレーム引き継ぐ連鎖生成をDocker上で検証 | [3セグメント](./experiments/05-temporal-continuity/motion-context-3segment/README.md) |
| 日本語猫カフェVlog | 英語プロンプト＋日本語セリフで約30秒の5セグメントを生成 | [実験記録](./experiments/06-production-pipelines/catcafe-vlog-5segment/README.md) |
| 日本語シンセポップMV | H3生成音声を解析し、HyperFramesでビート同期リリックモーションを合成 | [実験記録](./experiments/06-production-pipelines/jpop-mv-5segment/README.md) |

### 3060の黒画について

初期のTurbo/full-int8 + Kijai int8 VAE経路は全フレームが黒信号になったため、成功結果として扱っていません。その後、投稿に明記された公式FP16/FP32 VAE構成へ切り替え、WSL再起動後に約720p T2V/I2Vを再実行しました。失敗経路と再発防止は[調査メモ](./research-notes.md)と[検証ログ](./verification-log.md)に残しています。

## Docker Composeで起動

### 前提

- Windows 11 + WSL2 + Docker Desktop
- NVIDIAドライバとDockerからGPUを利用できること
- RTX 3060またはRTX 4090（両方同時起動も可）
- モデル一式。初回ダウンロードは約42.5GB

### 初回セットアップ

```powershell
cd D:/Prj/minimax-h3-compose
Copy-Item .env.example .env
nvidia-smi -L
# .envのGPU_3060_UUID / GPU_4090_UUIDを自分のUUIDへ合わせる

docker compose --profile 4090 build h3-4090
docker compose --profile 3060 build h3-3060
docker compose --profile download run --rm model-downloader
```

### 起動

```powershell
# RTX 4090: http://localhost:8188
docker compose --profile 4090 up -d h3-4090

# RTX 3060: http://localhost:8189
docker compose --profile 3060 up -d h3-3060

# 2枚同時
docker compose --profile 3060 --profile 4090 up -d
docker compose ps
```

GPUはCompose serviceごとにUUIDで固定し、モデルは読み取り専用、入出力とComfyUI状態は`runtime/3060`または`runtime/4090`へ分離します。自分のPCでは必ず`.env.example`のGPU UUIDを置き換えてください。

## 実験を再実行する

まず対応する実験記録から、workflow・seed・解像度・frames・steps・モデルrevision・Docker条件を確認します。通常のpost-condition workflowは次のように実行します。

```powershell
.\scripts\run-h3-post-condition.ps1 -Gpu 4090 -Port 8188 -Workflow .\workflows\tlanoai_t2v_1280x704_api.json -OutputPrefix video\MiniMax_H3_T2V_4090_1280x704_repeat -LowVram $false -Seed 2026080704 -TimeoutSeconds 14400
```

実行後は`runtime/<gpu>/benchmark/`に、JSONとMarkdownの実行レポートを保存します。レポートにはwall time、ComfyUI status、prompt ID、環境、workflowのSHA-256、ffprobe、blackdetect、signalstatsを記録します。`blackdetect=0`だけで画質成功とは判断せず、必要な実験では抽出フレームも確認します。

## ディレクトリ構成

```text
Dockerfile / compose.yaml       Docker Composeと固定revision
docker/                         runtime patch、entrypoint、モデル取得
workflows/                      共有API workflow
runtime/3060/benchmark/         RTX 3060の機械可読レポート
runtime/4090/benchmark/         RTX 4090の機械可読レポート
runtime/*/input/                再現に必要な開始画像・リファレンス
experiments/<category>/<slug>/  テーマ別の実験README、JSON、workflow、成果物
experiments/01-baseline/        基準条件・GPU比較・失敗経路
experiments/02-low-step-generation/ 少ないstepでの動画生成
experiments/03-reference-conditioned/ I2V・ref2va・複数リファレンスR2V
experiments/04-acceleration/    Attention・EasyCacheなどの高速化
experiments/05-temporal-continuity/ Motion Context・セグメント連鎖
experiments/06-production-pipelines/ Vlog・音楽MVなどの制作検証
social/                         X投稿シミュレーターと公開用payloadの索引
scripts/                        実行・マージ・検証ヘルパー
```

モデル本体、コンテナの出力ディレクトリ、Pythonキャッシュ、一時ログはGitの正本に含めません。必要な大容量ファイルは取得元、revision、サイズ、SHA-256、保存先を実験記録へ残します。

## 記録ルール

1. 出典に書かれていない値は推測で補完しない。
2. 投稿条件とローカルで固定した検証条件を分けて書く。
3. GPU、解像度、steps、sampler、scheduler、VAE、LoRA、attention、EasyCache、seedを固定値として残す。
4. 実行時間はAPI投入からComfyUIのsuccess/errorまでのwall timeとして記録する。
5. 出力の相対パス、bytes、SHA-256、ffprobe、黒画検査、目視確認、未検証項目を残す。
6. 失敗、OOM、黒画、CUDA異常も削除せず、`failed`または`limitations`として記録する。

新規実験は[テンプレート](./experiments/_template/README.md)をコピーし、記録後に次の検証を実行します。

```powershell
.\scripts\validate-experiment-lab.ps1
docker compose config --quiet
```

## 参照元

- [MiniMax-H3公式モデルカード](https://huggingface.co/MiniMaxAI/MiniMax-H3)
- [MiniMax-H3公式GitHub](https://github.com/MiniMax-AI/MiniMax-H3)
- [ComfyUI MiniMax-H3 docs](https://docs.comfy.org/tutorials/video/minimax/minimax-h3)
- [Kijai MiniMax-H3 Comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy)
- [H3 Motion Context](https://github.com/NikoDemon80/ComfyUI-H3-Motion-Context)

参照したX投稿、LightX2V、Sol-Attn、SageAttention、EasyCacheのURLは各実験の`README.md`または`experiment.json`に保存しています。

## ライセンスと公開状態

この作業ツリーにはまだ公開GitHub remoteが設定されていません。ライセンスは利用者の意図に合わせて決める必要があるため、未設定のままです。公開前にライセンス、GitHub repository、モデルの再配布条件を確認してください。
