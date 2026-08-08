#!/usr/bin/env bash
set -Eeuo pipefail

mkdir -p \
  /opt/ComfyUI/input \
  /opt/ComfyUI/output \
  /opt/ComfyUI/user

if [[ -n "${H3_MEMORY_USAGE_FACTOR:-}" ]]; then
  H3_MEMORY_USAGE_FACTOR="$H3_MEMORY_USAGE_FACTOR" python - <<'PY'
import os
from pathlib import Path

path = Path('/opt/ComfyUI/comfy/supported_models.py')
factor = os.environ['H3_MEMORY_USAGE_FACTOR']
lines = path.read_text().splitlines(keepends=True)
inside_h3 = False
changed = False
for index, line in enumerate(lines):
    stripped = line.strip()
    if stripped.startswith('class MiniMaxH3('):
        inside_h3 = True
    elif inside_h3 and stripped.startswith('class '):
        inside_h3 = False
    if inside_h3 and stripped.startswith('memory_usage_factor ='):
        newline = '\n' if line.endswith('\n') else ''
        lines[index] = f'    memory_usage_factor = {factor}{newline}'
        changed = True
        break
if not changed:
    raise SystemExit('MiniMaxH3 memory_usage_factor was not found')
path.write_text(''.join(lines))
PY
fi

exec python - "$@" <<'PY'
import runpy
import sys

main_args = sys.argv[1:]
sys.path.insert(0, '/opt/ComfyUI')
import comfy.options
comfy.options.enable_args_parsing()
runpy.run_path('/usr/local/bin/h3-runtime-patch.py', run_name='h3_runtime_patch')
sys.argv = ['/opt/ComfyUI/main.py', *main_args]
runpy.run_path('/opt/ComfyUI/main.py', run_name='__main__')
PY
