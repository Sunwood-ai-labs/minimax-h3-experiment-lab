# 外部モデル一覧

> English version: [README.md](./README.md)

モデル重みは意図的にGitへ含めません。追跡対象の`manifest.json`が、workflowで参照する各外部ファイルについて、Hugging Faceリポジトリ、固定revision、配置先、bytes、SHA-256を記録します。

## profile

| Profile | 用途 | おおよその取得量 |
|---|---|---:|
| `fl2va` | baseline、Motion Context、猫カフェVlog、MV | 42.5 GB |
| `ref2va` | 複数リファレンスR2V | 42.5 GB |
| `fl2va-lightx2v` | 4-step / ImageGen開始I2V | 44.5 GB |
| `ref2va-lightx2v` | ref2va 6 vs 20 steps、高速化 | 44.5 GB |
| `legacy-turbo` | 旧Turbo診断workflow | 56.3 GB |

```powershell
Copy-Item .env.example .env
(Get-Content .env) -replace '^H3_PROFILE=.*', 'H3_PROFILE=ref2va-lightx2v' | Set-Content .env
docker compose --profile download run --rm model-downloader
```

downloaderは各ファイルのサイズとSHA-256を確認します。生成MP4やMotion Contextのlatent cacheは取得せず、各実験workflowで生成する実行成果物です。

出典: [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)、[Kijai/MiniMax-H3_comfy](https://huggingface.co/Kijai/MiniMax-H3_comfy)、[larryvrh/MiniMax-H3-Turbo-Lora](https://huggingface.co/larryvrh/MiniMax-H3-Turbo-Lora)。
