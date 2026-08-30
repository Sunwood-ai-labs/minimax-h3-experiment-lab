# FastH3 × ComfyUI VSA — Public Colab

This reproducibility notebook runs the FastVideo-style FastH3 four-step VSA checkpoint through the vsa branch of ComfyUI.

Open it directly in Colab:

- [Open in Google Colab](https://colab.research.google.com/github/Sunwood-ai-labs/minimax-h3-experiment-lab/blob/main/experiments/02-low-step-generation/fasth3-comfyui-colab-20260830/FastH3_ComfyUI_Colab.ipynb)
- [Notebook source on GitHub](./FastH3_ComfyUI_Colab.ipynb)
- [Standalone API workflow](./workflows/fasth3_vsa_t2v_832x480_api.json)

## Scope

This is specifically FastH3/VSA. It is not the native MiniMax-H3 checkpoint and it is not the community “MiniMax H3 Fast T2V” workflow.

- FastH3 checkpoint: minimax_h3_fastvideo_vsa_datafree_1300step_4step_int8_convrot.safetensors
- ComfyUI: Kijai/ComfyUI vsa branch at a pinned commit
- Sampler: Euler with the FastVideo four-step sigma ladder
- Audio path: audio VAE → VAEDecodeAudio → CreateVideo → SaveVideo
- Output: H.264/AAC MP4, 832×480, 124 frames, 24 fps, about 5.17 seconds

The notebook downloads public model files into the current Colab runtime. It does not use Drive, rclone, local PC paths, or credentials.

## Runtime requirements

- A100 40GB or larger is recommended. Public Colab GPU allocation is not guaranteed.
- At least 65 GiB free under /content is required. The four model files alone total about 52 GiB.
- The notebook stops before model download when CUDA is unavailable.
- Run cells from top to bottom. The ComfyUI process is stopped after the generation cell.

A previous A100-SXM4-40GB run observed 162.64 seconds in ComfyUI prompt execution and a 24,045 MiB peak VRAM sample. This is an earlier runtime observation, not a CU guarantee. Colab’s own resource meter is authoritative for Compute Units.

## Pinned public revisions

- ComfyUI VSA: 10febb01d7be73d1491cf5e5347b5ab8b6c2c09e
- FastH3 repository: Kijai/MiniMax-H3-experimental
- FastH3 revision: f4cac997f880e93cf6940af61ee8d58ef31ff7f3
- H3 text encoder and VAE repository: Comfy-Org/MiniMax-H3
- H3 revision: 4cc1d817b6184899b41293954329f576cb5ae86b

Review the license and usage terms in the upstream Hugging Face repositories before use.

## Verification state

- API graph: verified locally with the FastH3 checkpoint on the ComfyUI VSA branch.
- Public notebook: published as a GitHub-backed Colab reproduction recipe.
- MP4 output: intentionally not tracked; the notebook creates it in the active Colab runtime.

## References

- [FastVideo FastH3 preview example](https://github.com/hao-ai-lab/FastVideo/blob/main/examples/inference/basic/basic_fasth3_lora_preview.py)
- [Kijai MiniMax-H3 experimental](https://huggingface.co/Kijai/MiniMax-H3-experimental)
- [Comfy-Org MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)
- [ComfyUI VSA branch](https://github.com/kijai/ComfyUI/tree/vsa)
