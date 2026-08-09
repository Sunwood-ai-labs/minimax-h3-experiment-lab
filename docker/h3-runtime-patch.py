"""Runtime fixes for MiniMax-H3 VAE offload under ComfyUI --novram.

ComfyUI can report an H3 VAE as fully loaded while leaving a direct parameter
or buffer (notably ViT3DDecoder.register_tokens) on the CPU. The next decode
then mixes CUDA activations with CPU tensors. H3's 3060 fallback needs --novram
for the DiT, but its 9.9 GB video VAE fits on the GPU by itself, so normalize
all H3 VAE tensors after the normal model-loader pass.
"""

import logging
import os
import types
from pathlib import Path

import torch
import comfy.sd
import comfy.model_management


_H3_VAE_NAMES = {"MiniMaxH3VideoVAE", "MiniMaxH3AudioVAE"}
_original_load_models_gpu = comfy.model_management.load_models_gpu


def _h3_vae_model(patcher):
    model = getattr(patcher, "model", None)
    if model is None or type(model).__name__ not in _H3_VAE_NAMES:
        return None
    return model


def _normalize_h3_vae(patcher):
    model = _h3_vae_model(patcher)
    device = getattr(patcher, "load_device", None)
    if model is None or device is None or getattr(device, "type", None) != "cuda":
        return

    mismatched = []
    for name, value in list(model.named_parameters()) + list(model.named_buffers()):
        if getattr(value, "device", None) != device:
            mismatched.append(name)
    if mismatched:
        model.to(device)
        logging.warning(
            "[H3RuntimePatch] moved %s H3 VAE tensors to %s: %s",
            len(mismatched), device, ", ".join(mismatched[:5]),
        )


def _normalize_h3_vae_model(model, device):
    if model is None or device is None or getattr(device, "type", None) != "cuda":
        return
    mismatched = [
        name
        for name, value in list(model.named_parameters()) + list(model.named_buffers())
        if getattr(value, "device", None) != device
    ]
    if mismatched:
        model.to(device)
        logging.warning(
            "[H3RuntimePatch] decode moved %s H3 VAE tensors to %s: %s",
            len(mismatched), device, ", ".join(mismatched[:5]),
        )


def _install_decode_fix(vae):
    model = getattr(vae, "first_stage_model", None)
    if model is None or type(model).__name__ not in _H3_VAE_NAMES:
        return
    if getattr(model, "_h3_runtime_decode_fix", False):
        return

    device = getattr(vae, "device", None)
    original_decode = model.decode

    def decode_with_h3_device_fix(_model, *args, **kwargs):
        _normalize_h3_vae_model(model, device)
        output = original_decode(*args, **kwargs)
        values = output.detach().float()
        logging.warning(
            "[H3RuntimePatch] %s decode output shape=%s finite=%s min=%.6f max=%.6f mean=%.6f rms=%.6f",
            type(model).__name__,
            tuple(values.shape),
            bool(torch.isfinite(values).all()),
            float(values.min()),
            float(values.max()),
            float(values.mean()),
            float(values.square().mean().sqrt()),
        )
        return output

    model.decode = types.MethodType(decode_with_h3_device_fix, model)

    if hasattr(model, "decode_tiled"):
        original_decode_tiled = model.decode_tiled

        def decode_tiled_with_h3_device_fix(_model, *args, **kwargs):
            _normalize_h3_vae_model(model, device)
            return original_decode_tiled(*args, **kwargs)

        model.decode_tiled = types.MethodType(decode_tiled_with_h3_device_fix, model)

    model._h3_runtime_decode_fix = True
    logging.warning("[H3RuntimePatch] installed decode hook for %s on %s", type(model).__name__, device)


_original_vae_init = comfy.sd.VAE.__init__


def _vae_init_with_h3_decode_fix(self, *args, **kwargs):
    result = _original_vae_init(self, *args, **kwargs)
    _install_decode_fix(self)
    return result


def _load_models_gpu_with_h3_vae_fix(models, *args, **kwargs):
    result = _original_load_models_gpu(models, *args, **kwargs)
    for patcher in models:
        _normalize_h3_vae(patcher)
    return result


comfy.model_management.load_models_gpu = _load_models_gpu_with_h3_vae_fix
comfy.sd.VAE.__init__ = _vae_init_with_h3_decode_fix
logging.warning("[H3RuntimePatch] installed for MiniMax-H3 Video/Audio VAE")


def _install_kj_sage_debug():
    if os.environ.get("H3_DEBUG_KJ_SAGE", "0").lower() not in {"1", "true", "yes"}:
        return
    path = Path("/opt/ComfyUI/custom_nodes/ComfyUI-KJNodes/nodes/ltxv_nodes.py")
    if not path.exists():
        logging.warning("[H3RuntimePatch] KJNodes source not found; Sage debug skipped")
        return
    source = path.read_text(encoding="utf-8")
    marker = "[H3RuntimePatch] KJ Sage input"
    if marker in source:
        return
    needle = "    q, k, v = qkv\n    qkv.clear()"
    replacement = (
        "    q, k, v = qkv\n"
        "    logging.warning(\"[H3RuntimePatch] KJ Sage input shape=%s dtype=%s strides=%s finite=%s qabs=%.5g kabs=%.5g vabs=%.5g\", "
        "tuple(q.shape), q.dtype, q.stride(), bool(torch.isfinite(q).all()), "
        "float(q.detach().float().abs().amax()), float(k.detach().float().abs().amax()), "
        "float(v.detach().float().abs().amax()))\n"
        "    qkv.clear()"
    )
    if needle not in source:
        logging.warning("[H3RuntimePatch] KJ Sage function marker not found; debug skipped")
        return
    path.write_text(source.replace(needle, replacement, 1), encoding="utf-8")
    logging.warning("[H3RuntimePatch] KJ Sage input diagnostics enabled")


_install_kj_sage_debug()
