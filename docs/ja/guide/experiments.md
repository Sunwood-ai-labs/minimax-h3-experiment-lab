# 実験一覧

実験台帳は、調べた機能ごとに整理しています。実施日は機械可読な記録に残しますが、ナビゲーションの分類軸にはしません。

## カテゴリ

- [01 — 基準条件・GPU比較](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/01-baseline)
- [02 — 低ステップ生成](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/02-low-step-generation)
- [03 — 参照条件付き生成](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/03-reference-conditioned)
- [04 — 高速化](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/04-acceleration)
- [05 — 時間連続性](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/05-temporal-continuity)
- [06 — 制作パイプライン](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/06-production-pipelines)

## 最初に見る実験

1. [GPU基準](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/01-baseline/gpu-baseline) — T2V/I2Vの基準条件。
2. [3060黒画失敗](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/01-baseline/3060-black-output) — 失敗経路と診断。
3. [ref2va 6 vs 20 steps](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/03-reference-conditioned/ref2va-6v20) — 速度・画質比較と限界。
4. [複数リファレンスR2V](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/03-reference-conditioned/multi-reference-r2v-4scenes-7s) — 背景＋人物2人を4シーンで使用。
5. [猫カフェVlog](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/tree/master/experiments/06-production-pipelines/catcafe-vlog-5segment) — 日本語セリフの約30秒パイプライン。

視覚結果がある実験のREADMEから`previews/contact-sheet.jpg`を開けます。タイルは挙動の早見用、条件と結論の正本はREADMEと`experiment.json`です。
