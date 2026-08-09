# 実験記録の契約

各実験は`experiments/<category>/<slug>/`に置き、元の会話がなくても再現条件が分かる状態にします。

## 必須の証跡

- 仮説、目的、範囲、結論
- 出典URL、出典記載値とローカル固定値の区別
- GPU、VRAM、driver、Docker image、ComfyUI、PyTorch、CUDA、起動引数
- workflow/model/LoRAのrevisionまたはSHA-256
- prompt、negative prompt、seed、sampler、scheduler、VAE、attention/cache設定
- 解像度、frames、fps、steps、開始・終了、API投入からsuccessまでのwall time
- `ffprobe`、黒画・signal検査、映像・音声確認、未検証項目
- 出力の相対パス、bytes、SHA-256

パスの基準: workflow、リファレンス入力、実験内成果物は各実験ディレクトリ基準です。`runtime/...`とcontact-sheet manifestのsource pathはリポジトリルート基準です。`../`で始まる値は実験ディレクトリから解決し、`<repo-root>`は保存時のホストを示す説明用placeholderで、そのまま実行するコマンドではありません。

## status

| status | 意味 |
|---|---|
| `planned` | 条件と目的を定義済み、未実行。 |
| `running` | 実行または整理中。 |
| `verified` | 実行、出力検査、条件記録が完了。 |
| `partial` | 意図した条件の一部だけ確認。 |
| `failed` | 失敗経路を再現して記録。 |

## 分類を拡張する場合

同じ機能の条件違いは既存カテゴリにslugを追加します。新しい機能でカテゴリを増やすときは、JSON schema、PowerShell validator、実験台帳を同じ変更で更新します。

## 大きな成果物

モデル本体、runtime出力動画、依存キャッシュ、一時ログは通常のGit管理外です。公開証跡にはフレームタイル、poster、hash、benchmark JSON、Markdown記録を使います。

fresh cloneで必ず開けるものはREADME、`experiment.json`、追跡済みタイル、manifestです。無視対象のMP4へREADMEから直接リンクせず、動画のパス・media情報・SHA-256は記録へ残し、`publicEvidence.videoStatus`で`local-only`を明示します。
