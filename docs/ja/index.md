---
layout: home

hero:
  name: MiniMax-H3 Experiment Lab
  text: 再現可能な動画生成実験
  tagline: Docker Compose、ComfyUI、GPU比較、参照条件、時間連続性、制作パイプラインを記録します。
  image:
    src: /icon.svg
    alt: MiniMax-H3 Experiment Lab
  actions:
    - theme: brand
      text: 実験を再現する
      link: /ja/guide/reproduce
    - theme: alt
      text: 実験一覧を見る
      link: /ja/guide/experiments

features:
  - icon: 🧪
    title: 証跡を中心に記録
    details: prompt、seed、workflow hash、処理時間、出力検査、未検証項目を実験ごとに保存します。
  - icon: 🐳
    title: Docker Composeランタイム
    details: RTX 3060とRTX 4090をprofile、port、GPU UUID、runtimeディレクトリで分離します。
  - icon: 🖼️
    title: 共有用フレームタイル
    details: 動画を添付しにくい場所でも、挙動の変化を一枚のcontact sheetで確認できます。
---

## 現在の範囲

基準GPU比較、4-step生成、ref2va・複数リファレンスR2V、attention/cache高速化、Motion Context、日本語Vlog/MV制作を検証しています。

実験は日付・配布元・人物名ではなく、検証した機能で分類しています。[実験台帳](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/index.md)が正本で、このサイトは導入用の短い入口です。

## 言語

- [English documentation](/)
- [日本語README](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/README.ja.md)
- [English README](https://github.com/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/README.md)
