# MiniMax-H3 Experiment Labへの貢献

> English version: [CONTRIBUTING.md](./CONTRIBUTING.md)

このラボでは、実験結果を「再実行できる記録」として追加します。成功だけでなく、OOM、黒画、CUDAエラー、条件不一致も有用な証跡です。

## 実験を追加する

1. `experiments/`内の既存の機能カテゴリを選びます。
2. `experiments/_template/`を説明的で安定したslugへコピーします。
3. 仮説、参照URL、固定したローカル条件、GPU/runtime、workflow hash、seed、prompt、steps、dimensions、frames、wall time、出力検査、制限を記録します。
4. 生成動画・音声・モデル重みを通常のcommitへ入れません。視覚結果が必要ならcontact sheetとmanifestを追加します。
5. 次のローカルチェックを実行します。

```powershell
powershell -File .\\scripts\\validate-experiment-lab.ps1
powershell -File .\\scripts\\validate-documentation-parity.ps1
docker compose config --quiet
```

6. commit済みメタデータでは相対パスを使います。credential、`.env`、モデル重み、マシン固有の秘密情報をcommitしません。

実験READMEは英語defaultの`README.md`と日本語の`README.ja.md`を用意し、両方から`experiment.json`・workflow・タイル・X動画/参照URLへ到達できるようにします。
