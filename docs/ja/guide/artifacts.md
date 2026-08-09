# 公開成果物と動画の境界

このリポジトリでは、長期保存する公開証跡と、大容量のローカル生成物を分けています。fresh cloneで開けないMP4を、あたかも公開済みのようにリンクしないための境界です。

## fresh cloneに含まれるもの

| 成果物 | 公開clone | 入口 |
|---|---:|---|
| 実験README | あり | `README.md`（英語default）＋`README.ja.md`（日本語） |
| 機械可読レコード | あり | `experiment.json` |
| フレームタイル | あり | `previews/contact-sheet.jpg` |
| タイルmanifest | あり | `previews/contact-sheet.json` |
| リファレンスシート・workflow | 実験で使用したものはあり | 各実験ディレクトリ |
| 生成MP4・音声 | 通常なし（`local-only`） | パス、media情報、SHA-256は記録に残す |
| モデル重み・依存キャッシュ | なし | 起動・ダウンロード手順で取得 |

まず挙動を見るなら[実験ギャラリー](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/master/experiments/README.md)、全件を辿るなら[実験台帳](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/master/experiments/index.md)を使います。

## なぜタイルを正本にするのか

タイルは実際に生成した動画を、manifestに保存した時刻でサンプリングしたものです。別生成や手作業のイメージではありません。入力動画のパス、bytes、SHA-256、解像度、fps、duration、サンプリング順をmanifestに残すため、GitHubとXスレッドで動画本体なしに時間変化を確認できます。

## シミュレーターの挙動

`sunwood-x-simulator-*`は長いスレッドの構成を確認するための投稿シミュレーターで、元のprompt、処理時間、hashは`payload.json`に残します。大容量動画はlocal-onlyです。fresh cloneで動画が読めない場合は、追跡済みposterまたは実験タイルを表示し、何が利用できないかをprovenanceへ記載します。

## fresh cloneでの確認

```powershell
git clone https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab.git
cd minimax-h3-experiment-lab
pwsh -File .\scripts\validate-experiment-lab.ps1
pwsh -File .\scripts\validate-public-media.ps1
docker compose config --quiet
```

検証が通ることは、公開レコード、追跡済みタイル、manifest、Markdownの動画リンクが整合していることを示します。モデル重みやlocal-only動画まで同梱されていることは示しません。
