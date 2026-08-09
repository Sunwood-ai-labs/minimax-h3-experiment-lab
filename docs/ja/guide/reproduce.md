# 実験を再現する

## 1. ホストを準備する

Windows 11 + WSL2 + Docker Desktopと、DockerからNVIDIA GPUを利用できる環境を使います。Compose profileはRTX 3060とRTX 4090に対応しています。

```powershell
Copy-Item .env.example .env
nvidia-smi -L
```

ホストのUUIDが初期値と異なる場合は、`.env`の`GPU_3060_UUID`と`GPU_4090_UUID`を変更します。

## 2. buildとモデル取得

```powershell
docker compose --profile 4090 build h3-4090
docker compose --profile download run --rm model-downloader
```

モデルは`models/`へ取得します。このディレクトリはGit管理外です。`.env`の`H3_PROFILE`で`fl2va`（既定）、`ref2va`、`fl2va-lightx2v`、`ref2va-lightx2v`、`legacy-turbo`を選択できます。Git管理された[`models/manifest.json`](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/models/manifest.json)にモデル名、upstream revision、bytes、SHA-256を固定し、取得後にdownload scriptが検証します。モデルとcustom nodeのupstreamライセンスが適用されます。

## 3. GPUサービスを起動する

```powershell
# RTX 4090: http://localhost:8188
docker compose --profile 4090 up -d h3-4090

# RTX 3060: http://localhost:8189
docker compose --profile 3060 up -d h3-3060
```

2つのserviceはport、GPU UUID、input/output、ComfyUI user stateを分離します。runtime状態を共有せずにGPU比較できます。

## 4. 実験記録を選ぶ

実行前に実験READMEと`experiment.json`を開きます。記録されたworkflow、seed、解像度、frames、steps、sampler、model revision、attention/cache条件を使います。出典にない値を推測で埋めず、ローカル固定値として明記します。

再現キットの正本はGit管理されています。[`compose.yaml`](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/compose.yaml)、[`Dockerfile`](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/Dockerfile)、[`.env.example`](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/.env.example)、[`docker/download-h3-model.sh`](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/docker/download-h3-model.sh)、[`models/manifest.json`](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/models/manifest.json)、各記録のworkflow JSONを使用します。DockerfileはPyTorch base imageをdigestで固定し、SageAttention wheelのhashも検証します。Compose serviceは`workflows/`と`experiments/`を読み取り専用でcontainerへmountするため、同じグラフをhost API runnerとcontainer内の両方から参照できます。

GPU実行の前に、workflowと入力の導線を確認します。

```powershell
pwsh -File .\scripts\validate-reproducibility.ps1
```

この検査は、各記録とrootのworkflow JSON、実験用helper script、Compose／Dockerファイル、モデル固定表、追跡済み入力が、記録されたパスから解決できるかを確認します。外部モデル重みやGPUで生成したMP4がclone直後から存在することまでは保証しません。source revisionを固定しても、build時のpackage indexの変化によるbit単位のimage再現までは保証しません。

## 5. 検証する

```powershell
pwsh -File .\scripts\validate-experiment-lab.ps1
docker compose config --quiet
```

新しい結果にはComfyUI status、API投入からsuccessまでのwall time、`ffprobe`、黒画検査、signal統計、出力SHA-256、未検証の映像・音声特性を記録します。

## フレームタイル

動画を添付しづらい場合は、Git管理するタイルを生成します。

```powershell
pwsh -File .\scripts\make-video-contact-sheet.ps1 `
  -InputPath .\runtime\4090\output\video\example.mp4 `
  -OutputPath .\experiments\03-reference-conditioned\my-experiment\previews\contact-sheet.jpg `
  -FrameCount 8 -Columns 4 -Overwrite
```

同名の`contact-sheet.json`に入力動画のリポジトリ相対パス、hash、解像度、fps、duration、サンプル時刻を保存します。フレームは左から右、次に上から下へ進み、複数動画はブロックを縦積みします。
