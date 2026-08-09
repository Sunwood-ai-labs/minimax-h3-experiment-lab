#!/usr/bin/env bash
set -Eeuo pipefail

# The manifest is the human-readable lock file. Keep the small download table
# here as well so this script only needs bash, hf, and standard coreutils.
profile="${H3_PROFILE:-${H3_VARIANT:-fl2va}}"
official_repo="${H3_MODEL_REPO:-Comfy-Org/MiniMax-H3}"
official_ref="${H3_MODEL_REF:-93acf8c91365d40dc32a3abd19af06df6b6f7c65}"
lightx2v_repo="${H3_LIGHTX2V_REPO:-Kijai/MiniMax-H3_comfy}"
lightx2v_ref="${H3_LIGHTX2V_REF:-37ae5cbe1d6f2243484812fc511f9fa427b12a30}"
turbo_repo="${H3_TURBO_MODEL_REPO:-larryvrh/MiniMax-H3-Turbo-Lora}"
turbo_ref="${H3_TURBO_MODEL_REF:-43a74557ac3f6539db8e0f2a959d03feb7a81480}"
models_root="/opt/ComfyUI/models"

specs=()

add_spec() {
  local id="$1"
  local source_repo="$2"
  local source_ref="$3"
  local source_path="$4"
  local target_path="$5"
  local expected_size="$6"
  local expected_sha256="$7"
  local download_root="$8"
  specs+=("$id|$source_repo|$source_ref|$source_path|$target_path|$expected_size|$expected_sha256|$download_root")
}

add_official_common() {
  add_spec \
    "text-nvfp4" "$official_repo" "$official_ref" \
    "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors" \
    "text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors" \
    "15687142551" "35A88D51044231FE332301D7A62AA81E3F2CBA62FEBEB446E2C1E3E0EF76F2C6" \
    "$models_root"
  add_spec \
    "video-vae-fp16" "$official_repo" "$official_ref" \
    "vae/minimax_h3_video_vae_fp16.safetensors" \
    "vae/minimax_h3_video_vae_fp16.safetensors" \
    "5207808496" "7C1F131492E7EDDACAAC9069A61B81BDD39DE5CC96561E677C5EAB1CDCE5E522" \
    "$models_root"
  add_spec \
    "audio-vae-fp32" "$official_repo" "$official_ref" \
    "vae/minimax_h3_audio_vae_fp32.safetensors" \
    "vae/minimax_h3_audio_vae_fp32.safetensors" \
    "605254808" "8E505D95DD1561D47ABD43D4238FD40D9BB1AE9E147ED0A4CBA778D76AE4DB48" \
    "$models_root"
}

case "$profile" in
  fl2va)
    add_spec \
      "fl2va-pruned-int8" "$official_repo" "$official_ref" \
      "diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors" \
      "diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors" \
      "20970379616" "E889202C41DAFB67B10D67B97F0D8541508036A6090AF23425A5C2615D03C47A" \
      "$models_root"
    add_official_common
    ;;
  ref2va)
    add_spec \
      "ref2va-pruned-int8" "$official_repo" "$official_ref" \
      "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors" \
      "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors" \
      "20970379616" "9255F52B6677845AD238F20DFAAFA94727053694127AB7F255C048F0F9365779" \
      "$models_root"
    add_official_common
    ;;
  fl2va-lightx2v)
    add_spec \
      "fl2va-pruned-int8" "$official_repo" "$official_ref" \
      "diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors" \
      "diffusion_models/minimax_h3_fl2va_pruned_int8_convrot.safetensors" \
      "20970379616" "E889202C41DAFB67B10D67B97F0D8541508036A6090AF23425A5C2615D03C47A" \
      "$models_root"
    add_official_common
    add_spec \
      "lightx2v-comfy-lora" "$lightx2v_repo" "$lightx2v_ref" \
      "loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors" \
      "loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors" \
      "1956171984" "FC9B6500F0331FE925B004738BAAA31BD34104741C8BF9334816F9AC3005C8C1" \
      "$models_root"
    ;;
  ref2va-lightx2v)
    add_spec \
      "ref2va-pruned-int8" "$official_repo" "$official_ref" \
      "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors" \
      "diffusion_models/minimax_h3_ref2va_pruned_int8_convrot.safetensors" \
      "20970379616" "9255F52B6677845AD238F20DFAAFA94727053694127AB7F255C048F0F9365779" \
      "$models_root"
    add_official_common
    add_spec \
      "lightx2v-comfy-lora" "$lightx2v_repo" "$lightx2v_ref" \
      "loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors" \
      "loras/minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy.safetensors" \
      "1956171984" "FC9B6500F0331FE925B004738BAAA31BD34104741C8BF9334816F9AC3005C8C1" \
      "$models_root"
    ;;
  legacy-turbo)
    add_spec \
      "fl2va-int8" "$official_repo" "$official_ref" \
      "diffusion_models/minimax_h3_fl2va_int8_convrot.safetensors" \
      "diffusion_models/minimax_h3_fl2va_int8_convrot.safetensors" \
      "34038892334" "7AD4C73E6E378B822FFD1629F27F632D3787D95F5E468E3AF958F98C58DF96A5" \
      "$models_root"
    add_official_common
    add_spec \
      "turbo-ckpt850" "$turbo_repo" "$turbo_ref" \
      "minimax_h3_turbo_4step_ema_ckpt850.safetensors" \
      "loras/minimax_h3_turbo_4step_ema_ckpt850.safetensors" \
      "779849816" "5A6EEBA171CF183020A4AD48774BB2968F29F8168AFD6EC17A04987F3528B4EA" \
      "$models_root/loras"
    ;;
  *)
    echo "H3_PROFILE must be fl2va, ref2va, fl2va-lightx2v, ref2va-lightx2v, or legacy-turbo; got: $profile" >&2
    exit 2
    ;;
esac

verify_file() {
  local target_path="$1"
  local expected_size="$2"
  local expected_sha256="$3"
  if [[ ! -f "$target_path" ]]; then
    return 1
  fi
  if [[ "$(stat -c '%s' "$target_path")" != "$expected_size" ]]; then
    return 1
  fi
  if [[ -n "$expected_sha256" ]]; then
    local actual_sha256
    actual_sha256="$(sha256sum "$target_path" | awk '{print toupper($1)}')"
    [[ "$actual_sha256" == "$(printf '%s' "$expected_sha256" | tr '[:lower:]' '[:upper:]')" ]]
  fi
}

download_spec() {
  local id="$1"
  local source_repo="$2"
  local source_ref="$3"
  local source_path="$4"
  local target_path="$5"
  local expected_size="$6"
  local expected_sha256="$7"
  local download_root="$8"
  local target_file="$models_root/$target_path"

  if verify_file "$target_file" "$expected_size" "$expected_sha256"; then
    echo "Verified: $id -> $target_path"
    return 0
  fi

  mkdir -p "$(dirname "$target_file")" "$download_root"
  echo "Downloading: $id from $source_repo@$source_ref"
  download_args=(download "$source_repo" "$source_path" --revision "$source_ref" --local-dir "$download_root")
  if [[ -n "${HF_TOKEN:-}" ]]; then
    download_args+=(--token "$HF_TOKEN")
  fi
  hf "${download_args[@]}"

  if ! verify_file "$target_file" "$expected_size" "$expected_sha256"; then
    echo "Verification failed for $target_file (expected bytes=$expected_size sha256=$expected_sha256)" >&2
    exit 1
  fi
  echo "Downloaded and verified: $id"
}

echo "MiniMax-H3 model profile: $profile"
echo "Official model source: $official_repo@$official_ref"
for spec in "${specs[@]}"; do
  IFS='|' read -r id source_repo source_ref source_path target_path expected_size expected_sha256 download_root <<< "$spec"
  download_spec "$id" "$source_repo" "$source_ref" "$source_path" "$target_path" "$expected_size" "$expected_sha256" "$download_root"
done

echo "MiniMax-H3 model download and SHA-256 verification completed."
