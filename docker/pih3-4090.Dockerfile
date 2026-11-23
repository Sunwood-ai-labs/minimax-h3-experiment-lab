FROM pytorch/pytorch:2.11.0-cuda13.0-cudnn9-runtime@sha256:bfbb4a2b4fdba0fefdb428ea737e626d61bb3daf74a16e1ff935bdb03aa7c3f0

ARG COMFYUI_REF=v0.46.0
ARG PIFLOW_REF=e0ca46f7a7dcd080d8ab1d759719e8bc046617f0
ARG SOL_ATTN_REF=26d816ebd4f1e43a2c6e4d4759be3137f10a7a73
ARG SPARK_H3_ZIP_URL=https://github.com/zechengtang/Spark-H3/releases/download/comfyui-v0.2.0/ComfyUI-Spark-H3-0.2.0-linux-x86_64-sm89-cu130.zip
ARG SPARK_H3_ZIP_SHA256=ad03aef0d7adda50b059f1348c4c54c9beb23c3b4e894fe87e398fcc2346a99f
ARG SAGEATTENTION_WHEEL_URL=https://github.com/Comfy-Org/wheels/releases/download/sageattention-latest/sageattention-2.2.0%2Bcu130torch2.11-cp312-cp312-manylinux_2_34_x86_64.manylinux_2_35_x86_64.whl
ARG SAGEATTENTION_WHEEL_SHA256=988a5b510078dfef67fa0ca517321afb659a62a3ace12d7f52f3b831d2ddb58f

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    PYTHONUNBUFFERED=1 \
    PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True \
    CUDA_MODULE_LOADING=LAZY

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        ffmpeg \
        build-essential \
        git \
        libgl1 \
        libglib2.0-0 \
        unzip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt

RUN git clone --depth 1 --branch "${COMFYUI_REF}" \
        https://github.com/Comfy-Org/ComfyUI.git /opt/ComfyUI

RUN mkdir -p /opt/ComfyUI/custom_nodes \
    && curl -fsSL --retry 5 --retry-delay 3 \
        "https://github.com/Lakonik/ComfyUI-piFlow/archive/${PIFLOW_REF}.tar.gz" \
        -o /tmp/comfyui-piflow.tar.gz \
    && tar -xzf /tmp/comfyui-piflow.tar.gz -C /tmp \
    && mv "/tmp/ComfyUI-piFlow-${PIFLOW_REF}" \
        /opt/ComfyUI/custom_nodes/ComfyUI-piFlow \
    && curl -fsSL --retry 5 --retry-delay 3 \
        "https://github.com/kijai/ComfyUI-SolAttn_triton/archive/${SOL_ATTN_REF}.tar.gz" \
        -o /tmp/sol-attn.tar.gz \
    && tar -xzf /tmp/sol-attn.tar.gz -C /tmp \
    && mv "/tmp/ComfyUI-SolAttn_triton-${SOL_ATTN_REF}" \
        /opt/ComfyUI/custom_nodes/ComfyUI-SolAttn_triton \
    && curl -fsSL --retry 5 --retry-delay 3 \
        "${SPARK_H3_ZIP_URL}" \
        -o /tmp/spark-h3-sm89.zip \
    && echo "${SPARK_H3_ZIP_SHA256}  /tmp/spark-h3-sm89.zip" | sha256sum -c - \
    && unzip -q /tmp/spark-h3-sm89.zip -d /opt/ComfyUI/custom_nodes \
    && rm -f /tmp/comfyui-piflow.tar.gz /tmp/sol-attn.tar.gz /tmp/spark-h3-sm89.zip

# Fix Spark-H3 v0.2.0 Linux SM89 node registration bug (only SM120 was exposed)
RUN python - <<'PY'
from pathlib import Path

init_path = Path("/opt/ComfyUI/custom_nodes/ComfyUI-Spark-H3/__init__.py")
text = init_path.read_text(encoding="utf-8")
old = "_HIDDEN_ARCHITECTURE_NODES = ('MiniMaxH3SparkAttentionSM86', 'MiniMaxH3SparkAttentionSM89')"
new = "_HIDDEN_ARCHITECTURE_NODES = ('MiniMaxH3SparkAttentionSM86', 'MiniMaxH3SparkAttentionSM120', 'MiniMaxH3SolAttentionSM120')"
if old not in text:
    raise SystemExit(f"Expected _HIDDEN_ARCHITECTURE_NODES line not found in {init_path}")
init_path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Patched Spark-H3 __init__.py to expose MiniMaxH3SparkAttentionSM89")
PY

WORKDIR /opt/ComfyUI

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt \
    && python -m pip install -r custom_nodes/ComfyUI-Spark-H3/requirements.txt \
    && python -m pip install --no-deps --force-reinstall \
        /opt/ComfyUI/custom_nodes/ComfyUI-Spark-H3/wheelhouse/spark_h3_kitchen-0.2.37+spark.h3.sm89.cu130.1-cp312-abi3-linux_x86_64.whl \
    && sageattention_wheel=/tmp/sageattention-2.2.0+cu130torch2.11-cp312-cp312-manylinux_2_34_x86_64.manylinux_2_35_x86_64.whl \
    && curl -fsSL --retry 5 --retry-delay 3 "${SAGEATTENTION_WHEEL_URL}" -o "${sageattention_wheel}" \
    && echo "${SAGEATTENTION_WHEEL_SHA256}  ${sageattention_wheel}" | sha256sum -c - \
    && python -m pip install --no-deps "${sageattention_wheel}" \
    && rm -f "${sageattention_wheel}"

RUN mkdir -p \
    /opt/ComfyUI/input \
    /opt/ComfyUI/output \
    /opt/ComfyUI/user \
    /opt/ComfyUI/models/diffusion_models \
    /opt/ComfyUI/models/text_encoders \
    /opt/ComfyUI/models/vae \
    /opt/ComfyUI/models/loras

ENTRYPOINT ["python", "/opt/ComfyUI/main.py"]
