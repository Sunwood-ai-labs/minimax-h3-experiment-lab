# Attention/cache diagnostics

This directory contains diagnostic workflows used while selecting the stable acceleration chain for the canonical [Sol-Attn + SageAttention + EasyCache experiment](../sol-sage-easycache-4scenes-7s/README.md).

診断用workflowの置き場です。ここは独立した生成実験ではなく、同条件の比較・失敗切り分けを親実験へ紐づける補助資料です。正式な結果、4シーンのタイル、処理時間、採用理由は親実験のREADMEと`experiment.json`を正本にします。

## Diagnostic variants

| Variant | Workflow | Recorded outcome |
|---|---|---|
| EasyCache only | [easycache-only](./solattn-kjnodes-easycache-4scenes-7s/diagnostics/easycache-only_scene-01_api.json) | 591.541 sec; 1.2488× vs baseline scene 1 |
| Generic Sage + EasyCache | [sage-generic-fp16-easycache](./solattn-kjnodes-easycache-4scenes-7s/diagnostics/sage-generic-fp16-easycache_scene-01_api.json) | 580.269 sec; 1.2726× vs baseline scene 1 |
| Sol-Attn + Sage + EasyCache | [selected chain](./solattn-kjnodes-easycache-4scenes-7s/diagnostics/sol-sage-easycache-start0_scene-01_api.json) | Stable path used by the parent experiment |
| H3 memory-efficient Sage + EasyCache | [rejected path](./solattn-kjnodes-easycache-4scenes-7s/diagnostics/sage-easycache-headchunks4_scene-01_api.json) | CUDA failure; retained as compatibility evidence |
| Generic Sage auto/FP8 | [rejected path](./solattn-kjnodes-easycache-4scenes-7s/diagnostics/sage-generic-easycache_scene-01_api.json) | CUDA launch failure; retained as compatibility evidence |

The parent record also lists the remaining rejected variants and their prompt IDs under `diagnostics.rejected`. Diagnostic outputs are local-only; the tracked parent contact sheet is the public visual evidence.

## Reproduction boundary

These API workflows assume the Docker Compose runtime, downloaded model weights, custom nodes, and reference sheets described by the parent record. A fresh clone contains the workflow JSON and the parent frame tile, but not generated MP4s or model weights.
