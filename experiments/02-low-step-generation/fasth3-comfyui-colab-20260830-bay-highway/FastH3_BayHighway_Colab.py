# %% [markdown]
# # FastH3 を ComfyUI で動かす — 公開Colabノートブック
#
# このノートブックは、MiniMax-H3 の通常チェックポイントや「Fast T2V」ワークフローではなく、
# FastVideo の4-step VSA系チェックポイントを ComfyUI の vsa ブランチ経由で実行します。
#
# - FastH3 checkpoint: minimax_h3_fastvideo_vsa_datafree_1300step_4step_int8_convrot.safetensors
# - Sampler: Euler + FastVideo 4-step sigma ladder
# - Output: H.264/AAC MP4, 832×480, 124 frames, 24 fps（約5.17秒）
# - Recommended GPU: A100 40GB以上。ColabでそのGPUが割り当てられること自体は保証されません。
# - このノートブックはDrive/rcloneや秘密トークンを使いません。重いモデルは各自のColabランタイムへ取得します。
#
# 上から順に実行してください。GPUが割り当てられていない場合は、モデルをダウンロードする前の
# preflightセルで停止します。

# %%
from __future__ import annotations

import hashlib
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Any


BASE = Path("/content")
COMFY_ROOT = BASE / "ComfyUI"
MODEL_ROOT = COMFY_ROOT / "models"
OUTPUT_DIR = BASE / "fasth3-comfy-output"
SERVER_LOG = BASE / "fasth3-comfy-server.log"
METRICS_PATH = BASE / "fasth3-comfy-metrics.json"

COMFY_REPOSITORY = "https://github.com/kijai/ComfyUI.git"
COMFY_BRANCH = "vsa"
COMFY_COMMIT = "10febb01d7be73d1491cf5e5347b5ab8b6c2c09e"

FASTH3_REPOSITORY = "Kijai/MiniMax-H3-experimental"
FASTH3_REVISION = "f4cac997f880e93cf6940af61ee8d58ef31ff7f3"
COMFY_H3_REPOSITORY = "Comfy-Org/MiniMax-H3"
COMFY_H3_REVISION = "4cc1d817b6184899b41293954329f576cb5ae86b"

FASTH3_FILE = "minimax_h3_fastvideo_vsa_datafree_1300step_4step_int8_convrot.safetensors"
TEXT_ENCODER_FILE = "qwen3vl_32b_minimax_h3_int8_convrot.safetensors"
VIDEO_VAE_FILE = "minimax_h3_video_vae_fp16.safetensors"
AUDIO_VAE_FILE = "minimax_h3_audio_vae_fp32.safetensors"

WIDTH = 832
HEIGHT = 480
FRAMES = 124
FPS = 24
SEED = 20260831
SIGMAS = "0.99991659, 0.972832558, 0.923076923, 0.8, 0"

# The file is public and intentionally contains no credential or local path.
RUN_ID = "fasth3-bay-highway-a100-20260830-r2"
PROMPT_SOURCE = "colab-drive-cli-ops/references/h3-operation.md + FastH3 structured prompt contract"
WORKFLOW_URL = (
    "https://raw.githubusercontent.com/Sunwood-ai-labs/minimax-h3-experiment-lab/"
    "main/experiments/02-low-step-generation/fasth3-comfyui-colab-20260830-bay-highway/"
    "workflows/fasth3_bay_highway_vsa_t2v_832x480_api.json"
)

PROMPT = """integrated_multimodal_description: [Shot 1] A silver sports coupe races along a sweeping elevated coastal expressway beside a dark bay at blue hour, with a luminous city skyline, seawall, and distant harbor lights beyond the guardrail. At 00:01.000, on a closed-to-traffic section of rain-darkened roadway, the driver initiates a controlled four-wheel drift through a broad interchange curve; the rear tires release a thin veil of smoke and fine water spray while the headlights streak across wet lane markings and metal barriers. Low forward tracking camera beside the front quarter, realistic motorsport cinematography, stable silver bodywork, physically plausible wheel rotation, coherent reflections on the asphalt. [Shot 2] At 00:03.000, the camera arcs to a rear three-quarter view as the coupe holds the slide around the long coastal ramp, then exits onto a straight elevated expressway toward the skyline. The bay, layered overpasses, red aircraft warning lights, lane markings, and harbor cranes remain spatially coherent. End with the car accelerating away toward the glowing waterfront horizon. One car only, no readable signs, no text, no logos, no watermark, no extra vehicles, no warped wheels, no cartoon rendering. overall_soundscape: A high-revving turbocharged engine rises under throttle, synchronized tire squeal peaks as the car rotates through the wet curve, turbo flutter on throttle lift, tire hiss and water spray on the pavement, wind rushing over the elevated roadway, a distant city-and-harbor hum, and a restrained low electronic cinematic pulse. The engine, tire, wind, and pulse remain synchronized to the camera movement and fade naturally as the car accelerates toward the waterfront."""
PROMPT_SHA256 = hashlib.sha256(PROMPT.encode("utf-8")).hexdigest()


def run_cmd(command: list[str], *, cwd: Path | None = None, timeout: int = 1800) -> subprocess.CompletedProcess[str]:
    """Run one bounded command and keep the command visible in the notebook output."""
    printable = [str(item) for item in command]
    print("$ " + shlex.join(printable), flush=True)
    return subprocess.run(
        printable,
        cwd=str(cwd) if cwd else None,
        check=True,
        timeout=timeout,
        text=True,
    )


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(16 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def nvidia_smi() -> dict[str, Any]:
    query = [
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.used,memory.total,memory.free,utilization.gpu,utilization.memory",
        "--format=csv,noheader,nounits",
    ]
    try:
        result = subprocess.run(query, capture_output=True, text=True, check=True, timeout=15)
        row = [part.strip() for part in result.stdout.strip().splitlines()[0].split(",")]
        if len(row) != 7:
            return {"error": "unexpected nvidia-smi output", "raw": result.stdout[:500]}
        return {
            "gpu_name": row[0],
            "driver_version": row[1],
            "memory_used_mib": float(row[2]),
            "memory_total_mib": float(row[3]),
            "memory_free_mib": float(row[4]),
            "utilization_gpu_pct": float(row[5]),
            "utilization_memory_pct": float(row[6]),
        }
    except Exception as exc:
        return {"error_type": type(exc).__name__, "error": str(exc)}


def sample_gpu(event: str) -> dict[str, Any]:
    sample = {"event": event, "at_unix": time.time(), **nvidia_smi()}
    GPU_SAMPLES.append(sample)
    return sample


GPU_SAMPLES: list[dict[str, Any]] = []

# %% [markdown]
# ## 1. Colab GPU / ストレージの事前確認
#
# モデル4ファイルの合計は約52 GiBです。ComfyUI本体、Pythonパッケージ、キャッシュ、出力領域も
# 必要なので、/content に少なくとも65 GiBの空き容量を要求します。A100 40GBは過去の実測条件で、
# 下の処理は割り当てられたGPU名とVRAMを記録します。

# %%
import torch


if not torch.cuda.is_available():
    raise RuntimeError(
        "CUDA GPUが割り当てられていません。ColabのランタイムをGPUに変更してから、最初から再実行してください。"
    )

gpu_name = torch.cuda.get_device_name(0)
gpu_total_gib = torch.cuda.get_device_properties(0).total_memory / 1024**3
disk = shutil.disk_usage(BASE)
disk_free_gib = disk.free / 1024**3
print(f"GPU: {gpu_name}")
print(f"VRAM: {gpu_total_gib:.2f} GiB")
print(f"/content free: {disk_free_gib:.2f} GiB")
print(json.dumps(sample_gpu("preflight"), ensure_ascii=False, indent=2))

if gpu_total_gib < 38:
    print("WARNING: VRAMが38 GiB未満です。セットアップは続けますが、FastH3生成はVRAM不足になる可能性があります。")
if disk_free_gib < 65:
    raise RuntimeError("/contentの空き容量が65 GiB未満です。別ランタイムで再実行してください。")

print("preflight: OK")

# %% [markdown]
# ## 2. ComfyUI VSAブランチを固定して取得
#
# vsa ブランチの特定コミットを使います。これにより、MiniMaxH3ImageToVideo、
# ManualSigmas、動画+音声の保存ノードが入った実行環境を固定します。

# %%
def ensure_comfy() -> None:
    if not COMFY_ROOT.exists():
        run_cmd(
            [
                "git",
                "clone",
                "--filter=blob:none",
                "--no-checkout",
                COMFY_REPOSITORY,
                str(COMFY_ROOT),
            ],
            timeout=900,
        )
    run_cmd(["git", "-C", str(COMFY_ROOT), "fetch", "origin", COMFY_BRANCH, "--depth", "1"], timeout=900)
    run_cmd(["git", "-C", str(COMFY_ROOT), "fetch", "origin", COMFY_COMMIT, "--depth", "1"], timeout=900)
    run_cmd(["git", "-C", str(COMFY_ROOT), "checkout", "--force", COMFY_COMMIT], timeout=120)
    actual = subprocess.check_output(
        ["git", "-C", str(COMFY_ROOT), "rev-parse", "HEAD"], text=True, timeout=30
    ).strip()
    if actual != COMFY_COMMIT:
        raise RuntimeError(f"ComfyUI commit mismatch: expected {COMFY_COMMIT}, got {actual}")
    print(f"ComfyUI: {actual}")


ensure_comfy()

# %% [markdown]
# ## 3. 依存パッケージを導入
#
# Colabが持つCUDA版PyTorchを置き換えないよう、ComfyUIのrequirementsからtorch系だけを除外します。
# 依存関係を大きく変える操作なので、セルの実行ログを残しておくと再現時の切り分けに使えます。

# %%
def package_name(requirement: str) -> str:
    match = re.match(r"^([A-Za-z0-9_.-]+)", requirement.strip())
    return match.group(1).lower() if match else ""


requirements: list[str] = []
for line in (COMFY_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        continue
    if package_name(stripped) in {"torch", "torchvision", "torchaudio"}:
        continue
    requirements.append(stripped)

# torchsde declares trampoline as a dependency.  The requirements below use
# --no-deps to protect Colab's CUDA torch, so keep this small non-torch
# dependency explicit instead of relying on a preinstalled package.
requirements.append("trampoline==0.1.2")

run_cmd(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-cache-dir",
        "--no-deps",
        *requirements,
    ],
    timeout=1800,
)

# Hugging Face Hub is used only for public model downloads; it does not receive a token here.
run_cmd(
    [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--no-cache-dir",
        "huggingface_hub>=0.34.0",
    ],
    timeout=600,
)

print("dependencies: OK")

# %% [markdown]
# ## 4. FastH3 / H3 VAE / text encoderを公開リビジョンから取得
#
# 取得先は公開Hugging Faceリポジトリです。アクセストークンは不要な公開ファイルだけを指定しています。
# 既存ファイルはサイズを照合し、別リビジョンや途中ファイルを黙って使わないようにします。

# %%
from huggingface_hub import hf_hub_download


MODEL_SPECS = [
    {
        "repo_id": FASTH3_REPOSITORY,
        "revision": FASTH3_REVISION,
        "filename": FASTH3_FILE,
        "local_path": MODEL_ROOT / "diffusion_models" / FASTH3_FILE,
        "bytes": 22_898_594_920,
    },
    {
        "repo_id": COMFY_H3_REPOSITORY,
        "revision": COMFY_H3_REVISION,
        "filename": f"text_encoders/{TEXT_ENCODER_FILE}",
        "local_path": MODEL_ROOT / "text_encoders" / TEXT_ENCODER_FILE,
        "bytes": 27_141_342_152,
    },
    {
        "repo_id": COMFY_H3_REPOSITORY,
        "revision": COMFY_H3_REVISION,
        "filename": f"vae/{VIDEO_VAE_FILE}",
        "local_path": MODEL_ROOT / "vae" / VIDEO_VAE_FILE,
        "bytes": 5_207_808_496,
    },
    {
        "repo_id": COMFY_H3_REPOSITORY,
        "revision": COMFY_H3_REVISION,
        "filename": f"vae/{AUDIO_VAE_FILE}",
        "local_path": MODEL_ROOT / "vae" / AUDIO_VAE_FILE,
        "bytes": 605_254_808,
    },
]


def download_models() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for spec in MODEL_SPECS:
        target = Path(spec["local_path"])
        target.parent.mkdir(parents=True, exist_ok=True)
        expected_bytes = int(spec["bytes"])
        if target.exists():
            if target.stat().st_size != expected_bytes:
                raise RuntimeError(
                    f"既存ファイルのサイズが不一致です（途中ダウンロードの可能性）: {target} "
                    f"{target.stat().st_size} != {expected_bytes}"
                )
            print(f"reuse: {target.name} ({expected_bytes:,} bytes)")
        else:
            downloaded = hf_hub_download(
                repo_id=str(spec["repo_id"]),
                filename=str(spec["filename"]),
                revision=str(spec["revision"]),
                local_dir=str(MODEL_ROOT if "/" in str(spec["filename"]) else target.parent),
            )
            downloaded_path = Path(downloaded)
            if downloaded_path.resolve() != target.resolve() and downloaded_path.exists():
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(downloaded_path, target)
            if not target.exists() or target.stat().st_size != expected_bytes:
                raise RuntimeError(f"モデル取得後のサイズ確認に失敗しました: {target}")
            print(f"downloaded: {target.name} ({target.stat().st_size:,} bytes)")
        records.append(
            {
                "repo_id": spec["repo_id"],
                "revision": spec["revision"],
                "filename": spec["filename"],
                "local_path": str(target),
                "bytes": target.stat().st_size,
            }
        )
    return records


MODEL_RECORDS = download_models()
print(json.dumps({"models": MODEL_RECORDS}, ensure_ascii=False, indent=2))

# %% [markdown]
# ## 5. APIワークフローを読み込んで、FastH3固有のノードを確認
#
# JSONは同じ公開リポジトリ内のワークフローを正本として読み込みます。重要なのは、
# UNETLoader がFastH3ファイルを指し、ManualSigmas が4-stepの値を持ち、
# VAEDecodeAudio → CreateVideo → SaveVideo で音声付きMP4になることです。

# %%
import requests


workflow_response = requests.get(WORKFLOW_URL, timeout=60)
workflow_response.raise_for_status()
WORKFLOW: dict[str, Any] = workflow_response.json()

required_nodes = {
    "UNETLoader",
    "CLIPLoader",
    "MiniMaxH3ImageToVideo",
    "ManualSigmas",
    "SamplerCustomAdvanced",
    "VAEDecodeAudio",
    "CreateVideo",
    "SaveVideo",
}
actual_nodes = {str(node.get("class_type")) for node in WORKFLOW.values() if isinstance(node, dict)}
missing_nodes = sorted(required_nodes - actual_nodes)
if missing_nodes:
    raise RuntimeError(f"FastH3ワークフローに必要なノードがありません: {missing_nodes}")

if WORKFLOW["1"]["inputs"]["unet_name"] != FASTH3_FILE:
    raise RuntimeError("UNETLoaderがFastH3 checkpointを指していません")
if WORKFLOW["9"]["inputs"]["sigmas"] != SIGMAS:
    raise RuntimeError("4-step sigma ladderが想定値と一致しません")
if WORKFLOW["5"]["inputs"].get("prompt") == PROMPT:
    print("workflow prompt already matches the run prompt")
else:
    WORKFLOW["5"]["inputs"]["prompt"] = PROMPT
    print("workflow prompt injected from the run prompt artifact")
if WORKFLOW["5"]["inputs"].get("prompt") != PROMPT:
    raise RuntimeError("workflow prompt does not match the H3 prompt artifact")
Path(BASE / "fasth3_vsa_workflow.json").write_text(
    json.dumps(WORKFLOW, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(f"workflow nodes: {len(WORKFLOW)}")
print(f"FastH3 checkpoint: {WORKFLOW['1']['inputs']['unet_name']}")
print(f"sigma ladder: {WORKFLOW['9']['inputs']['sigmas']}")
print(f"run_id: {RUN_ID}")
print(f"prompt_source: {PROMPT_SOURCE}")
print(f"prompt_sha256: {PROMPT_SHA256}")

# %% [markdown]
# ## 6. ComfyUIを起動し、APIから1回生成
#
# サーバーはColab VMのloopbackだけで待ち受け、生成終了後に必ず停止します。
# readinessは最大120回、生成待ちは最大360回（各10秒）という上限を持たせています。
# VRAMサンプルは観測できた範囲の値で、ColabのCU表示そのものではありません。

# %%
HOST = "127.0.0.1"
PORT = 8188
server_process: subprocess.Popen[str] | None = None
server_log_handle: Any = None


def start_comfy() -> subprocess.Popen[str]:
    global server_log_handle
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    environment = os.environ.copy()
    environment.update(
        {
            "PYTHONPATH": str(COMFY_ROOT),
            "HF_HUB_DISABLE_TELEMETRY": "1",
            "DO_NOT_TRACK": "1",
            "PYTHONUNBUFFERED": "1",
            "PYTORCH_CUDA_ALLOC_CONF": "expandable_segments:True",
        }
    )
    command = [
        sys.executable,
        "main.py",
        "--listen",
        HOST,
        "--port",
        str(PORT),
        "--lowvram",
        "--use-ck-attention",
        "--enable-triton-backend",
        "--disable-async-offload",
        "--disable-smart-memory",
        "--cache-none",
        "--disable-metadata",
        "--disable-auto-launch",
        "--output-directory",
        str(OUTPUT_DIR),
    ]
    server_log_handle = SERVER_LOG.open("w", encoding="utf-8")
    process = subprocess.Popen(
        command,
        cwd=str(COMFY_ROOT),
        env=environment,
        stdout=server_log_handle,
        stderr=subprocess.STDOUT,
        text=True,
    )
    print(f"ComfyUI pid={process.pid}")
    return process


def stop_comfy(process: subprocess.Popen[str] | None) -> None:
    global server_log_handle
    if process is not None and process.poll() is None:
        process.terminate()
        try:
            process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=30)
    if server_log_handle is not None:
        server_log_handle.close()
        server_log_handle = None


def wait_for_server(process: subprocess.Popen[str], max_attempts: int = 120) -> dict[str, Any]:
    url = f"http://{HOST}:{PORT}/system_stats"
    for attempt in range(max_attempts):
        if process.poll() is not None:
            raise RuntimeError(f"ComfyUIが起動前に終了しました: returncode={process.returncode}")
        try:
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            print(f"server ready after {attempt + 1} probe(s)")
            return response.json()
        except (requests.RequestException, ValueError):
            time.sleep(5)
    raise TimeoutError("ComfyUI readiness timeout: 120 probes × 5 seconds")


def inspect_nodes() -> None:
    response = requests.get(f"http://{HOST}:{PORT}/object_info", timeout=30)
    response.raise_for_status()
    available = response.json()
    missing = sorted(required_nodes - set(available))
    if missing:
        raise RuntimeError(f"ComfyUI側に必要なノードがありません: {missing}")
    print("ComfyUI nodes: OK")


def wait_for_history(process: subprocess.Popen[str], prompt_id: str, max_polls: int = 360) -> dict[str, Any]:
    url = f"http://{HOST}:{PORT}/history/{prompt_id}"
    for poll in range(max_polls):
        if process.poll() is not None:
            raise RuntimeError(f"ComfyUIが生成中に終了しました: returncode={process.returncode}")
        sample_gpu(f"history_poll_{poll + 1}")
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                payload = response.json()
                entry = payload.get(prompt_id) if isinstance(payload, dict) else None
                if isinstance(entry, dict):
                    status = entry.get("status")
                    if isinstance(status, dict) and status.get("status_str") == "error":
                        raise RuntimeError(json.dumps(status, ensure_ascii=False))
                    if "outputs" in entry:
                        return entry
        except requests.RequestException:
            pass
        if poll == 0 or (poll + 1) % 6 == 0:
            print(f"waiting for ComfyUI history: poll={poll + 1}/{max_polls}")
        time.sleep(10)
    raise TimeoutError("ComfyUI generation timeout: 360 polls × 10 seconds")


def media_probe(path: Path) -> dict[str, Any]:
    """Read basic video/audio facts without making ffprobe a hard dependency."""
    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        result = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration,size:stream=index,codec_type,codec_name,width,height,avg_frame_rate,channels,sample_rate",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=30,
        )
        return json.loads(result.stdout)
    return {"ffprobe": "not found", "bytes": path.stat().st_size}


def pick_new_mp4(started_at: float) -> Path:
    candidates = sorted(
        (path for path in OUTPUT_DIR.rglob("*.mp4") if path.stat().st_mtime >= started_at - 1),
        key=lambda path: path.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        raise FileNotFoundError(f"ComfyUI historyは完了しましたが、{OUTPUT_DIR} に新しいMP4がありません")
    return candidates[0]


generation_started = time.time()
server_process = start_comfy()
try:
    system_stats = wait_for_server(server_process)
    print(json.dumps(system_stats, ensure_ascii=False, indent=2)[:4000])
    inspect_nodes()
    sample_gpu("server_ready")

    client_id = str(uuid.uuid4())
    queued_response = requests.post(
        f"http://{HOST}:{PORT}/prompt",
        json={"prompt": WORKFLOW, "client_id": client_id},
        timeout=60,
    )
    queued_response.raise_for_status()
    queued = queued_response.json()
    if not isinstance(queued, dict) or "prompt_id" not in queued:
        raise RuntimeError(f"ComfyUIがワークフローを受理しませんでした: {queued}")
    prompt_id = str(queued["prompt_id"])
    print(f"prompt_id: {prompt_id}")

    sampling_started = time.perf_counter()
    history_entry = wait_for_history(server_process, prompt_id)
    generation_seconds = round(time.perf_counter() - sampling_started, 3)
    sample_gpu("output_found")
    output_path = pick_new_mp4(generation_started)
    result_record = {
        "status": "verified_in_this_runtime",
        "run_id": RUN_ID,
        "prompt_id": prompt_id,
        "prompt_source": PROMPT_SOURCE,
        "prompt_sha256": PROMPT_SHA256,
        "prompt": PROMPT,
        "output": str(output_path),
        "bytes": output_path.stat().st_size,
        "sha256": sha256(output_path),
        "generation_wall_seconds_observed": generation_seconds,
        "gpu_samples": GPU_SAMPLES,
        "gpu_peak_memory_used_mib_observed": max(
            (float(item["memory_used_mib"]) for item in GPU_SAMPLES if "memory_used_mib" in item),
            default=None,
        ),
        "system_stats": system_stats,
        "history_has_outputs": "outputs" in history_entry,
        "comfy_commit": COMFY_COMMIT,
        "fast_h3_revision": FASTH3_REVISION,
        "comfy_h3_revision": COMFY_H3_REVISION,
        "width": WIDTH,
        "height": HEIGHT,
        "frames": FRAMES,
        "fps": FPS,
        "seed": SEED,
        "sigmas": SIGMAS,
        "media": media_probe(output_path),
    }
    METRICS_PATH.write_text(json.dumps(result_record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result_record, ensure_ascii=False, indent=2)[:12000])

    from IPython.display import Video, display

    # `data=` works in both the Colab UI and the headless Colab CLI runtime.
    display(Video(data=str(output_path), embed=True))
finally:
    stop_comfy(server_process)
    print("ComfyUI stopped")
    if SERVER_LOG.exists():
        log_lines = SERVER_LOG.read_text(encoding="utf-8", errors="replace").splitlines()
        print("--- ComfyUI log tail ---")
        print("\n".join(log_lines[-80:]))

# %% [markdown]
# ## 7. 結果の持ち出し
#
# 生成MP4と fasth3-comfy-metrics.json はColabランタイム内にあります。必要なら下のセルで
# ローカルへダウンロードできます。ColabのCompute Unitsはアカウント・プラン・時期で変わるため、
# このノートブックの経過時間やVRAMサンプルをCUの確定値として扱わないでください。

# %%
# Colab UIではTrueに変更するとブラウザのダウンロードが始まります。
# Colab CLIなどのヘッドレス実行ではFalseのままにしてください。
DOWNLOAD_OUTPUTS = False
if DOWNLOAD_OUTPUTS:
    from google.colab import files

    if "output_path" not in globals() or not Path(output_path).exists():
        raise RuntimeError("先に生成セルを成功させてください")
    files.download(str(output_path))
    files.download(str(METRICS_PATH))
else:
    print("Download skipped. Set DOWNLOAD_OUTPUTS=True in the Colab UI to download the MP4 and metrics JSON.")

# %% [markdown]
# ## 参考リンク
#
# - FastVideo — FastH3 preview example: https://github.com/hao-ai-lab/FastVideo/blob/main/examples/inference/basic/basic_fasth3_lora_preview.py
# - Kijai — MiniMax-H3 experimental / FastH3 checkpoint: https://huggingface.co/Kijai/MiniMax-H3-experimental
# - Comfy-Org — MiniMax-H3 text encoder and VAE files: https://huggingface.co/Comfy-Org/MiniMax-H3
# - ComfyUI VSA branch: https://github.com/kijai/ComfyUI/tree/vsa
