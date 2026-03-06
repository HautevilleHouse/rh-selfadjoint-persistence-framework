#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "${ROOT_DIR}"

# Compatibility bootstrap for guard module default paths.
mkdir -p .codex_tmp/rh_closure
cp artifacts/stitch_constants.json .codex_tmp/rh_closure/stitch_constants.json
cp artifacts/constants_registry.json .codex_tmp/rh_closure/constants_registry.json

python3 scripts/rh_closure_drift_guard.py \
  --strict-coh-zero \
  --registry artifacts/constants_registry.json \
  --stitch artifacts/stitch_constants.json \
  --out repro/certificate_runtime.json \
  --history repro/drift_guard_runs.jsonl \
  --pretty

echo
echo "wrote ${ROOT_DIR}/repro/certificate_runtime.json"
