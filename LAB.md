# MiniMax-H3 Experiment Lab — 運用ガイド

MiniMax-H3をDocker Compose + ComfyUIで検証し、GPU・解像度・LoRA・sampler・VAE・メモリ設定の差を再現可能な形で比較するための運用ルールです。

## ラボの原則

- RTX 3060とRTX 4090は別service・別port・別runtimeとして扱う。
- 出典に書かれていない条件は推測で埋めず、検証用に固定した値として明記する。
- 成功だけでなく、OOM、黒画、CUDA異常、設定不一致も削除せず記録する。
- 実験記録のwall timeはAPI投入からComfyUIのsuccess/errorまで。後処理時間を混ぜない。
- Xの投稿文より詳細な情報を、リポジトリの実験記録へ保存する。

## ディレクトリ契約

```text
experiments/
  index.md                         # 全実験の入口
  experiment.schema.json           # 機械可読メタデータの契約
  _template/                       # 新規実験の雛形
  YYYY-MM-DD/<slug>/
    README.md                      # 仮説・条件・結果・結論・制限
    experiment.json                # 機械可読な条件・run・成果物
    sources.md                     # 出典の要約（必要な実験）
    workflows/                     # 実験専用workflow
    artifacts/ / outputs/          # 小さな証跡・成果物
runtime/<gpu>/
  benchmark/                       # 実行レポート（JSON/Markdown）
  input/                           # 再現用の開始画像・リファレンス
  output/                          # ローカル生成物（Git追跡外）
social/
  README.md                        # 投稿シミュレーターとpayloadの索引
```

モデル本体、runtimeのoutput、依存キャッシュはGitへ入れません。実験記録には取得元、revision、ファイルサイズ、SHA-256、ローカル保存先を残します。

## 1実験の必須項目

1. 仮説、比較対象、再現範囲
2. 出典URLと、出典に書かれていた条件／書かれていない条件
3. GPU、VRAM、driver、Docker image、ComfyUI、PyTorch、CUDA
4. workflow SHA-256、model/LoRA SHA-256、seed、prompt、解像度、frames、steps
5. 実行開始・終了・runner wall time、OOM/errorの有無
6. ffprobe、blackdetect、signalstats、必要に応じた目視確認
7. 生成物の相対パス、サイズ、SHA-256
8. 完全再現・部分一致・未検証を明示した結論

## 実験追加の標準手順

```powershell
cd D:/Prj/minimax-h3-compose
Copy-Item experiments/_template experiments/2026-08-09/my-experiment -Recurse
# README.md / experiment.json / sources.mdを埋める
# workflowを実験ディレクトリへ保存する（共有workflowを使う場合は相対パスを記録）
# .\scripts\run-h3-post-condition.ps1で実行する
# runtime/<GPU>/benchmarkのJSON/Markdownを確認する
.\scripts\validate-experiment-lab.ps1
```

## 条件と結果の書き分け

### 出典から確認した値

投稿本文、GitHub、Hugging Face、公式ドキュメントに明記されている値。URLと、出典に記載がなかった項目を記録します。

### ローカルで固定した値

prompt、seed、scheduler、sampler、attention、EasyCache閾値など、比較のために追加した値。`投稿と同じ`とは書かず、検証用の固定値として扱います。

### 結論の表現

- `verified`: 実行成功と出力検査、条件記録まで完了
- `partial`: 一部の条件・解像度・GPUのみ確認
- `failed`: 失敗経路を再現し、原因または現時点の仮説を記録
- 速度差にはGPU、解像度、frames、steps、sampler、キャッシュ、出力後処理の差がないかを併記

## 生成物の扱い

動画や画像を実験記録へ同梱する場合は、読者が実験結果を確認するのに必要なものに限定します。大きなruntime出力はGitへ追跡せず、benchmark JSONや実験JSONから相対パスを参照します。

投稿シミュレーターは実際の添付動画・本文・返信順を確認するための成果物です。実験記録とは分けて`social/README.md`から辿れるようにし、投稿済みか未送信かをpayload内で明示します。

## 検証コマンド

```powershell
# JSON / README / experiment indexの基本検証
.\scripts\validate-experiment-lab.ps1

# Composeの展開検証（コンテナ起動はしない）
docker compose config --quiet

# 実験レポートの一覧
Get-Content runtime/3060/benchmark/index.md
Get-Content runtime/4090/benchmark/index.md
```
