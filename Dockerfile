FROM pytorch/pytorch:2.11.0-cuda13.0-cudnn9-runtime

ARG COMFYUI_REF=v0.30.0
ARG H3_TURBO_REF=a7624b4c00626a8ae7e78860769389d706565190
ARG SAGEATTENTION_WHEEL_URL=https://github.com/Comfy-Org/wheels/releases/download/sageattention-latest/sageattention-2.2.0%2Bcu130torch2.11-cp312-cp312-manylinux_2_34_x86_64.manylinux_2_35_x86_64.whl

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PIP_BREAK_SYSTEM_PACKAGES=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        ffmpeg \
        build-essential \
        git \
        libgl1 \
        libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt

RUN git clone --depth 1 --branch "${COMFYUI_REF}" \
        https://github.com/Comfy-Org/ComfyUI.git /opt/ComfyUI

RUN mkdir -p /opt/ComfyUI/custom_nodes \
    && curl -fsSL --retry 5 --retry-delay 3 \
        "https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo/archive/${H3_TURBO_REF}.tar.gz" \
        -o /tmp/h3-turbo.tar.gz \
    && tar -xzf /tmp/h3-turbo.tar.gz -C /tmp \
    && mv "/tmp/ComfyUI-MiniMax-H3-Turbo-${H3_TURBO_REF}" \
        /opt/ComfyUI/custom_nodes/ComfyUI-MiniMax-H3-Turbo \
    && rm -f /tmp/h3-turbo.tar.gz

WORKDIR /opt/ComfyUI

RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt \
    && python -m pip install "huggingface_hub[cli]" \
    && python -m pip install --no-deps "${SAGEATTENTION_WHEEL_URL}"

COPY docker/entrypoint.sh /usr/local/bin/minimax-h3-entrypoint
COPY docker/download-h3-model.sh /usr/local/bin/download-h3-model
COPY docker/h3-runtime-patch.py /usr/local/bin/h3-runtime-patch.py

RUN chmod +x /usr/local/bin/minimax-h3-entrypoint \
    /usr/local/bin/download-h3-model \
    && mkdir -p \
        /opt/ComfyUI/input \
        /opt/ComfyUI/output \
        /opt/ComfyUI/user \
        /opt/ComfyUI/models/diffusion_models \
        /opt/ComfyUI/models/text_encoders \
        /opt/ComfyUI/models/vae

ENTRYPOINT ["/usr/local/bin/minimax-h3-entrypoint"]
