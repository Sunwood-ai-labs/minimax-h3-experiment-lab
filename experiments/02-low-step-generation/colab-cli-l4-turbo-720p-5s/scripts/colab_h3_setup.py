"""Prepare a pinned ComfyUI + MiniMax-H3 Turbo runtime on a Colab VM."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


ROOT = Path("/content")
CONFIG_PATH = Path(os.environ.get("H3_COLAB_CONFIG", ROOT / "colab_runtime.json"))
MANIFEST_PATH = Path(os.environ.get("H3_COLAB_MANIFEST", ROOT / "models_manifest.json"))
COMFY = ROOT / "ComfyUI"


def run(args: list[str], cwd: Path | None = None) -> None:
    print("+", " ".join(str(arg) for arg in args), flush=True)
    subprocess.run(args, cwd=cwd, check=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(32 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def disk_report() -> None:
    usage = shutil.disk_usage(ROOT)
    print({"disk_free_gb": round(usage.free / 1024**3, 2), "disk_total_gb": round(usage.total / 1024**3, 2)}, flush=True)


def checkout(repository: str, revision: str, target: Path) -> None:
    if not (target / ".git").exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        run(["git", "clone", "--filter=blob:none", repository, str(target)])
    run(["git", "fetch", "--depth", "1", "origin", revision], cwd=target)
    run(["git", "checkout", "--force", revision], cwd=target)


config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
profile_name = str(config["modelProfile"])
profile = manifest["profiles"][profile_name]
entries = {str(entry["id"]): entry for entry in manifest["files"]}

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")
os.environ.setdefault("CUDA_MODULE_LOADING", "LAZY")

disk_report()
checkout(config["comfyui"]["repository"], config["comfyui"]["revision"], COMFY)

node = COMFY / "custom_nodes" / "ComfyUI-MiniMax-H3-Turbo"
checkout(config["turboNode"]["repository"], config["turboNode"]["revision"], node)

run([sys.executable, "-m", "pip", "install", "-r", str(COMFY / "requirements.txt")])
run([sys.executable, "-m", "pip", "install", "huggingface_hub[cli]"])
node_requirements = node / "requirements.txt"
if node_requirements.exists():
    run([sys.executable, "-m", "pip", "install", "-r", str(node_requirements)])

from huggingface_hub import hf_hub_download


models_root = Path(config.get("modelRoot", COMFY / "models"))
for file_id in profile["files"]:
    if file_id not in entries:
        raise KeyError(f"model manifest entry is missing: {file_id}")
    asset = entries[file_id]
    target = models_root / str(asset["target"])
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists() and target.stat().st_size == int(asset["bytes"]) and sha256(target) == str(asset["sha256"]).upper():
        print(f"Verified existing: {target.relative_to(COMFY)}", flush=True)
        continue

    print(
        f"Downloading {asset['repository']}:{asset['sourcePath']} -> {target.relative_to(COMFY)} "
        f"({int(asset['bytes']) / 1024**3:.2f} GiB)",
        flush=True,
    )
    downloaded = Path(
        hf_hub_download(
            repo_id=str(asset["repository"]),
            filename=str(asset["sourcePath"]),
            revision=str(asset["revision"]),
            local_dir=str(models_root),
        )
    )
    if downloaded.resolve() != target.resolve():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(downloaded, target)
    if target.stat().st_size != int(asset["bytes"]):
        raise RuntimeError(f"size verification failed: {target}")
    actual = sha256(target)
    if actual != str(asset["sha256"]).upper():
        raise RuntimeError(f"sha256 verification failed: {target}: {actual}")
    print(f"Verified: {target.relative_to(COMFY)}", flush=True)
    disk_report()

print("SETUP_COMPLETE", flush=True)
disk_report()
