"""Start ComfyUI with the stable L4 flags used by the recorded run."""

from __future__ import annotations

import json
import os
import runpy
import subprocess
import sys
import time
import urllib.request
from pathlib import Path


COMFY = Path("/content/ComfyUI")
LOG_PATH = Path("/content/comfyui.log")
PATCH_PATH = Path("/content/h3-runtime-patch.py")
FLAGS = [
    "--listen", "0.0.0.0",
    "--port", "8188",
    "--disable-pinned-memory",
    "--disable-async-offload",
    "--disable-dynamic-vram",
    "--novram",
    "--fp16-intermediates",
    "--preview-method", "none",
]


def ready() -> bool:
    try:
        with urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=3):
            return True
    except Exception:
        return False


if ready():
    print({"ready": True, "reused": True, "port": 8188}, flush=True)
    raise SystemExit(0)

if not COMFY.exists():
    raise FileNotFoundError(COMFY)
if not PATCH_PATH.exists():
    raise FileNotFoundError(PATCH_PATH)

wrapper = Path("/content/launch_h3.py")
wrapper.write_text(
    "import runpy\n"
    "import sys\n"
    "sys.argv = " + repr([str(COMFY / "main.py"), *FLAGS]) + "\n"
    "sys.path.insert(0, " + repr(str(COMFY)) + ")\n"
    "import comfy.options\n"
    "comfy.options.enable_args_parsing()\n"
    "runpy.run_path(" + repr(str(PATCH_PATH)) + ", run_name='h3_runtime_patch')\n"
    "runpy.run_path(" + repr(str(COMFY / "main.py")) + ", run_name='__main__')\n",
    encoding="utf-8",
)

env = os.environ.copy()
env.update(
    {
        "PYTHONUNBUFFERED": "1",
        "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        "CUDA_MODULE_LOADING": "LAZY",
        "HF_HUB_DISABLE_TELEMETRY": "1",
        "H3_MEMORY_USAGE_FACTOR": "1.0",
    }
)

log = LOG_PATH.open("w", encoding="utf-8")
process = subprocess.Popen(
    [sys.executable, str(wrapper)],
    cwd=str(COMFY),
    env=env,
    stdout=log,
    stderr=subprocess.STDOUT,
    start_new_session=True,
)
log.close()
print({"pid": process.pid, "flags": FLAGS}, flush=True)

for _ in range(90):
    time.sleep(2)
    if ready():
        with urllib.request.urlopen("http://127.0.0.1:8188/system_stats", timeout=10) as response:
            stats = json.load(response)
        print({"ready": True, "system_stats": stats}, flush=True)
        break
else:
    tail = LOG_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()[-120:]
    print("\n".join(tail), flush=True)
    raise RuntimeError("ComfyUI did not become ready")

try:
    with urllib.request.urlopen("http://127.0.0.1:8188/object_info/MiniMaxH3TurboLoRA", timeout=10) as response:
        info = json.load(response)
    print({"turbo_node_detected": bool(info), "node_keys": list(info)[:10]}, flush=True)
except Exception as exc:
    print({"turbo_node_error": repr(exc)}, flush=True)

tail = LOG_PATH.read_text(encoding="utf-8", errors="ignore").splitlines()[-100:]
print("--- COMFY LOG TAIL ---", flush=True)
print("\n".join(tail), flush=True)
