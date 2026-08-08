#!/usr/bin/env bash
set -Eeuo pipefail

variant="${H3_VARIANT:-fl2va}"
repo="${H3_MODEL_REPO:-Comfy-Org/MiniMax-H3}"

case "$variant" in
  fl2va|ref2va)
    ;;
  *)
    echo "H3_VARIANT must be fl2va or ref2va; got: $variant" >&2
    exit 2
    ;;
esac

echo "Downloading MiniMax-H3 $variant weights from $repo"
echo "The selected official pruned/int8 + NVFP4 + official VAE files are approximately 42.5 GB in total."

diffusion_file="diffusion_models/minimax_h3_${variant}_pruned_int8_convrot.safetensors"

required_specs=(
  "$diffusion_file|20970379616"
  "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors|15687142551"
  "vae/minimax_h3_video_vae_fp16.safetensors|5207808496"
  "vae/minimax_h3_audio_vae_fp32.safetensors|605254808"
)

missing_includes=()
for spec in "${required_specs[@]}"; do
  IFS='|' read -r relative_path expected_size <<< "$spec"
  target_path="/opt/ComfyUI/models/$relative_path"
  if [[ -f "$target_path" ]] && [[ "$(stat -c '%s' "$target_path")" == "$expected_size" ]]; then
    echo "Already present: $relative_path"
  else
    missing_includes+=(--include "$relative_path")
  fi
done

if (( ${#missing_includes[@]} == 0 )); then
  echo "All selected MiniMax-H3 files are present; nothing to download."
else
  args=(
    download "$repo"
    "${missing_includes[@]}"
    --local-dir /opt/ComfyUI/models
  )

  if [[ -n "${HF_TOKEN:-}" ]]; then
    args+=(--token "$HF_TOKEN")
  fi

  hf "${args[@]}"
fi

download_one() {
  local source_repo="$1"
  local source_file="$2"
  local target_file="$3"
  local expected_size="$4"
  local target_dir

  if [[ -f "$target_file" ]] && [[ "$(stat -c '%s' "$target_file")" == "$expected_size" ]]; then
    echo "Already present: $target_file"
    return 0
  fi

  target_dir="$(dirname "$target_file")"
  mkdir -p "$target_dir"
  echo "Downloading $source_repo/$source_file -> $target_file"
  args=(download "$source_repo" "$source_file" --local-dir "$target_dir")
  if [[ -n "${HF_TOKEN:-}" ]]; then
    args+=(--token "$HF_TOKEN")
  fi
  hf "${args[@]}"

  if [[ ! -f "$target_file" ]] || [[ "$(stat -c '%s' "$target_file")" != "$expected_size" ]]; then
    echo "Size check failed for $target_file" >&2
    exit 1
  fi
}

echo "MiniMax-H3 model download and size checks completed."
