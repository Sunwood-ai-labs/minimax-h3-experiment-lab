# 出典 — Kijai LightX2V シーン汎化

English source note: [sources.md](./sources.md)

## Kijai / MiniMax-H3 Comfy

- URL: https://huggingface.co/Kijai/MiniMax-H3_comfy
- 確認revision: `37ae5cbe1d6f2243484812fc511f9fa427b12a30`
- 使用した根拠: `4 steps`、LoRA強度`0.75`、`er_sde` / `sa_solver`の例。
- 使用LoRA: `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`

## Xの参照投稿

- URL: https://x.com/sd_tutorial/status/2085760369612783646
- 投稿・公開メディアから確認した内容: KijaiのComfyUI対応LightX2V H3 turbo LoRA、元メディアの目標解像度1344×768、公開メディア長6.583秒、確認した配信版158 frames / 24 fps。
- 投稿から確認できない項目: GPU、prompt、seed、sampler、scheduler、VAE、offload設定。これらは投稿の事実ではなく、ローカル実験条件として記録します。

## Upstream LightX2V

- URL: https://huggingface.co/lightx2v/Minimax-h3-Turbo/tree/main
- 確認revision: `b65e359c0d128b3c5e08e0f5bf2791b794378588`
- 位置づけ: 系譜・背景の確認用。実験workflowは上記Kijai Comfy互換LoRAを使用します。

## ImageGen開始フレーム

4枚の開始フレームは、このCodexセッションの組み込みimage_gen機能で生成し、`runtime/4090/input/`へコピーして固定入力として使用しました。プロンプト、コピー先、サイズ、SHA-256は[imagegen-prompts.md](./imagegen-prompts.md)に記録しています。

## 実験の範囲

これは車、スポーツ、イラスト、バトルの4シーンへ汎化する実験です。X投稿がこの4枚の画像やプロンプトを使ったという主張ではありません。4090のDocker/ComfyUI/model/LoRA/解像度/長さ/steps/sampler条件を固定し、シーン、開始画像、prompt、seedを変更しました。
