# MiniMax-H3 Experiment Lab

MiniMax-H3をDocker Compose + ComfyUIで検証し、GPU・解像度・LoRA・sampler・VAE・メモリ設定の差を再現可能な形で比較するための実験ラボです。

## 目的

- 3060／4090などGPUを混ぜず、個別条件を再現する
- X・Hugging Face・GitHubの主張を、出典付きの実測へ分解する
- 成功だけでなく黒画、OOM、設定不一致も実験として保存する
- これからの実験を同じフォーマットで追加できるようにする

## ディレクトリ契約

```text
experiments/
  index.md                         # 全実験の入口
  experiment.schema.json           # メタデータの最小スキーマ
  _template/                       # 新規実験の雛形
  YYYY-MM-DD/<slug>/
    README.md                      # 人間向け実験記録・出典・結論
    experiment.json                # 機械可読な条件・状態・成果物
    sources.md                     # X/Hugging Face/GitHub等の出典
    workflows/                     # 実験専用workflow（必要な場合）
    artifacts/                     # 小さな証跡、manifest、サムネイル等
```

GPU別の大きな生成物は既存の`runtime/3060`または`runtime/4090`へ保存し、実験レコードから絶対パスではなくプロジェクト相対パスで参照します。モデル本体・LoRA・コンテナイメージは、取得元のrevision、ファイルサイズ、SHA-256を記録し、Gitには入れません。

## 1実験の必須項目

1. 仮説と比較対象
2. 出典URLと、出典に書かれていた条件／書かれていない条件
3. GPU、VRAM、driver、Docker image、ComfyUI、PyTorch、CUDA
4. workflow SHA-256、model/LoRA SHA-256、seed、prompt、解像度、frames、steps
5. 実行開始・終了・runner wall time、OOM/errorの有無
6. ffprobe、blackdetect、signalstats、目視確認
7. 生成物の相対パス、サイズ、SHA-256
8. 「再現できた」「部分一致」「未検証」を明示した結論

## 実験の追加手順

```powershell
cd D:/Prj/minimax-h3-compose
Copy-Item experiments/_template experiments/2026-08-08/my-experiment -Recurse
# README.md / experiment.json / sources.md を埋める
# workflowを experiments/.../workflows または workflows/ に保存
# run-h3-post-condition.ps1 で実行し、runtime/<GPU>/benchmarkを記録
# ffprobe / blackdetect / SHA-256を確認してexperiments/index.mdへ追記
```

## 条件の扱い

出典にない値は推測で補完しません。ローカルで追加したprompt、seed、sampler、scheduler、Docker差分は「検証用に固定した値」として明記します。GPUや解像度が違う結果を、同一条件の速度比較として扱いません。

## 現在のラボ範囲

- 3060: TlanoAI条件、864×480、1280×704、黒画／OOM切り分け
- 4090: yume linked recipe、1280×704 T2V/I2V
- Kijai `MiniMax-H3_comfy`のLightX2V 4-step LoRA、1344×768級T2V/I2Vはverified
- 次に追加する実験も`experiments/YYYY-MM-DD/<slug>/`へ保存し、GPU・条件・実行時間・出力検査を同じ形式で残す
