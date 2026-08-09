# MiniMax-H3 Experiment Lab — 運用ガイド

> English guide: [LAB.en.md](./LAB.en.md)

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
  README.md                        # タイルを並べた視覚ギャラリー
  index.md                         # 全実験の入口
  experiment.schema.json           # 機械可読メタデータの契約
  _template/                       # 新規実験の雛形
  <category>/<slug>/               # 機能カテゴリ内の個別実験
    README.md                      # 英語defaultの仮説・条件・結果・結論・制限
    README.ja.md                   # 日本語版
    experiment.json                # 機械可読な条件・run・成果物
    sources.md                     # 出典の要約（英語・必要な実験）
    sources.ja.md                  # 出典の要約（日本語・必要な実験）
    workflows/                     # 実験専用workflow
    previews/
      contact-sheet.jpg            # 動画の代表フレームを並べた公開用タイル
      contact-sheet.json           # 入力動画・時刻・SHA-256・タイル条件
    artifacts/ / outputs/          # 小さな証跡・成果物
runtime/<gpu>/
  benchmark/                       # 実行レポート（JSON/Markdown）
  input/                           # 再現用の開始画像・リファレンス
  output/                          # ローカル生成物（Git追跡外）
social/
  README.md                        # 投稿シミュレーターとpayloadの索引
```

モデル本体、runtimeのoutput、依存キャッシュはGitへ入れません。モデルは[`models/manifest.json`](./models/manifest.json)でprofile、取得元、revision、ファイルサイズ、SHA-256、配置先を固定し、download scriptで取得後に検証します。実験記録にはローカル保存先も残します。`experiment.json`のworkflow・実験内referenceは実験ディレクトリ基準、`runtime/...`やcontact-sheet manifestのsource pathはリポジトリルート基準として扱います。新しい記録では基準を混在させず、READMEリンクはREADME基準の相対パスにします。

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
cd <repo-root>
Copy-Item experiments/_template experiments/03-reference-conditioned/my-experiment -Recurse
# 例: 内容に合うカテゴリへ追加する
# README.md / README.ja.md / experiment.json / sources.mdを埋める
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

動画や画像を実験記録へ同梱する場合は、読者が実験結果を確認するのに必要なものに限定します。大きなruntime出力はGitへ追跡せず、`publicEvidence.videoStatus=local-only`としてbenchmark JSONや実験JSONへパス・bytes・SHA-256を残します。公開READMEからlocal-only MP4へ直接リンクしてはいけません。

## フレームタイルプレビュー

動画をXやREADMEへ直接添付しにくい場合は、`previews/contact-sheet.jpg`を標準成果物として作成します。1つの動画なら1ブロック、複数動画なら入力順に1ブロックずつ縦に並べ、左から右・上から下へ時間が進む構成にします。入力動画の相対パス、サンプル時刻、bytes、SHA-256は同名の`contact-sheet.json`へ保存します。

```powershell
.\scripts\make-video-contact-sheet.ps1 `
  -InputPath .\runtime\4090\output\video\h3_cat_cafe_vlog\segment_01_00001_.mp4 `
  -OutputPath .\experiments\06-production-pipelines\catcafe-vlog-5segment\previews\contact-sheet.jpg `
  -FrameCount 8 -Columns 4 -Overwrite
```

動画本体はローカル生成物として扱い、タイル画像とmanifestを再現可能な公開証跡としてGitへ残します。X投稿シミュレーターも公開表示はタイル優先とし、動画srcはローカル確認用の補助情報にします。

既存カテゴリに収まる実験は、カテゴリを増やさず`<slug>`を追加します。新しい機能系統を追加する場合だけ、`experiment.schema.json`の`category`、検証スクリプト、`experiments/index.md`の入口を同じ変更で更新し、分類理由を記録します。これにより、実験数が増えても日付・配布元・人物名が分類軸へ逆戻りしません。

投稿シミュレーターは本文・返信順・添付レイアウトを確認するための成果物です。実験記録とは分けて`social/README.ja.md` / `social/README.md`から辿れるようにし、投稿済みか未送信か、動画本体がlocal-onlyか、公開表示がタイルかをpayload内で明示します。

## 検証コマンド

```powershell
# JSON / README / experiment indexの基本検証
.\scripts\validate-experiment-lab.ps1
.\scripts\validate-public-media.ps1
.\scripts\validate-reproducibility.ps1

# Composeの展開検証（コンテナ起動はしない）
docker compose config --quiet

# 実験レポートの一覧
Get-Content runtime/3060/benchmark/index.md
Get-Content runtime/4090/benchmark/index.md
```
