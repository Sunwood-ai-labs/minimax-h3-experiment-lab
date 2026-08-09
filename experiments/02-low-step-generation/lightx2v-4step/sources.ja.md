# 出典 — Kijai LightX2V 4-step LoRA

English source note: [sources.md](./sources.md)

## Hugging Face: Kijai/MiniMax-H3_comfy

- URL: https://huggingface.co/Kijai/MiniMax-H3_comfy
- 確認revision: `37ae5cbe1d6f2243484812fc511f9fa427b12a30`
- READMEで確認した事実: `4 steps`、`0.75 LoRA strength`
- READMEの例: `er_sde`、`sa_solver`
- READMEの注意点: 想定alphaは未確認で、ノイズが多い場合はLoRA強度を下げる可能性がある。
- 使用対象LoRA: `loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors`
- 軽量版LoRA: `loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy_resized_avg_rank_21_bf16.safetensors`

## X: SD_Tutorial

- URL: https://x.com/sd_tutorial/status/2085760369612783646
- 投稿者: `@SD_Tutorial`
- 公開日時: `2026-08-07T16:09:58Z`
- 投稿から確認した内容: KijaiによるLightX2V H3 turbo LoRAのComfyUI対応版。
- 公開メディアの情報: 1344×768、6.583秒。配信版をffprobeで確認すると630×360、158 frames、24 fps、6.656秒だった。
- GPU、prompt、seed、sampler、scheduler、frame数、VAE、offload設定は投稿から確認できない。

## Upstream LightX2V

- URL: https://huggingface.co/lightx2v/Minimax-h3-Turbo/tree/main
- 確認revision: `b65e359c0d128b3c5e08e0f5bf2791b794378588`
- ファイル: `minimax_h3_fl2v_turbo_4step_v0.1.safetensors`
- 再現用情報: READMEは https://github.com/ModelTC/Minimax-H3-Turbo を案内している。

## 解釈の境界

4 stepsとLoRA強度0.75はKijaiのREADMEに明記された値です。解像度と長さはXの公開メディア情報から読み取った値です。GPU、prompt、seed、sampler、scheduler、frame数、VAE、offload設定は投稿にないため、ローカル実験の条件として扱い、投稿の条件とは区別します。
