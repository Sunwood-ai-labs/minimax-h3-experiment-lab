# セキュリティポリシー

> English version: [SECURITY.md](./SECURITY.md)

## 対象範囲

このリポジトリにはDocker設定、ComfyUI workflow、実験記録、ドキュメントが含まれます。設計上、モデルの認証情報やモデル重みは含めません。

## 脆弱性の報告

秘密情報、アクセストークン、悪用可能な詳細を公開issueへ投稿しないでください。利用可能な場合は[GitHubの非公開脆弱性報告](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/security/advisories/new)を使ってください。フォームが利用できない場合は、内容を含めず非公開の連絡経路を求める最小限のissueを作成してください。

報告前に、問題がこのリポジトリ由来か、upstreamのモデル・ComfyUI・custom node・取得済みasset由来かを確認してください。影響を受けるcommit、環境、再現手順、安全な影響概要を含めます。

## ドキュメント依存関係

静的ドキュメントbuildで使用している安定版VitePressは、推移依存するVite/esbuild開発依存関係について`npm audit`の警告対象になる場合があります。現在の安定版系列では利用可能な修正がないため、互換性のある安定版が出た時点で再確認します。Pages workflowは静的buildを実行し、Vite開発サーバーを公開しません。
