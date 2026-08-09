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

モデルは`models/`へ取得します。このディレクトリはGit管理外です。モデルとcustom nodeのupstreamライセンスが適用されます。

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
