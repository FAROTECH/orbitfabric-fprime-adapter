#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
FPRIME_ROOT="${1:-${ROOT}/_native/fprime}"
FPP_ROOT="${2:-${ROOT}/_native/fpp}"
WORK_ROOT="${3:-${ROOT}/.native-runtime-work}"
CASE_ROOT="${ROOT}/native_acceptance/ref"
GENERATED="${WORK_ROOT}/generated"
PROJECT="${WORK_ROOT}/project"
DEPLOYMENT="${PROJECT}/Ref"
EVIDENCE="${WORK_ROOT}/evidence"
GDS_LOG="${EVIDENCE}/gds.log"
JUNIT="${EVIDENCE}/runtime-junit.xml"
FPRIME_COMMIT="8a62e455a90b6d4f498c332d45d65a2a819988d8"
FPP_COMMIT="93f484b7521a8e8894cba25b26e633cc87d8e37a"

cleanup() {
  if [[ -n "${GDS_PID:-}" ]]; then
    kill "${GDS_PID}" 2>/dev/null || true
    wait "${GDS_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

command -v orbitfabric-fprime >/dev/null || { echo "error: orbitfabric-fprime not found" >&2; exit 2; }
command -v fprime-util >/dev/null || { echo "error: fprime-util not found" >&2; exit 2; }
command -v fprime-gds >/dev/null || { echo "error: fprime-gds not found" >&2; exit 2; }

actual_fprime="$(git -C "${FPRIME_ROOT}" rev-parse HEAD)"
actual_fpp="$(git -C "${FPP_ROOT}" rev-parse HEAD)"
[[ "${actual_fprime}" == "${FPRIME_COMMIT}" ]] || {
  echo "error: F Prime commit mismatch: ${actual_fprime}" >&2
  exit 3
}
[[ "${actual_fpp}" == "${FPP_COMMIT}" ]] || {
  echo "error: FPP commit mismatch: ${actual_fpp}" >&2
  exit 3
}

rm -rf "${WORK_ROOT}"
mkdir -p "${GENERATED}" "${EVIDENCE}"

printf '%s\n' "==> Canonical OrbitFabric projection"
orbitfabric-fprime run \
  --operation fpp_contract_projection \
  --input-set-manifest "${CASE_ROOT}/input_set/integration_input_manifest.json" \
  --profile "${CASE_ROOT}/profile.yaml" \
  --output-dir "${GENERATED}"

printf '%s\n' "==> Materialize evidence-only runtime fixture"
python "${ROOT}/native_acceptance/materialize_ref_runtime.py" \
  --fprime-root "${FPRIME_ROOT}" \
  --fpp-root "${FPP_ROOT}" \
  --generated-dir "${GENERATED}" \
  --profile "${CASE_ROOT}/profile.yaml" \
  --output-project "${PROJECT}"

export PATH="$(dirname "$(command -v fprime-util)"):${PATH}"
cd "${DEPLOYMENT}"
printf '%s\n' "==> F Prime generate"
fprime-util generate
printf '%s\n' "==> F Prime build"
fprime-util build

INSTALL_ROOT="${DEPLOYMENT}/build-artifacts/Linux/Ref"
BINARY="${INSTALL_ROOT}/bin/Ref"
DICTIONARY="${INSTALL_ROOT}/dict/RefTopologyDictionary.json"
[[ -x "${BINARY}" ]] || { echo "error: runtime binary not found: ${BINARY}" >&2; exit 4; }
[[ -f "${DICTIONARY}" ]] || { echo "error: runtime dictionary not found: ${DICTIONARY}" >&2; exit 4; }

printf '%s\n' "==> Start F Prime GDS without browser UI"
PYTHONUNBUFFERED=1 fprime-gds --gui none --deployment "${INSTALL_ROOT}" >"${GDS_LOG}" 2>&1 &
GDS_PID=$!

# Do not depend on a human-facing stdout marker for readiness. With redirected
# output, fprime-gds may buffer or omit that text while both GDS and Ref are
# already running. The live F Prime pytest fixture below is the authoritative
# connectivity probe and fails if the GDS Test API is not usable.
sleep 5
if ! kill -0 "${GDS_PID}" 2>/dev/null; then
  echo "error: fprime-gds exited before runtime test" >&2
  cat "${GDS_LOG}" >&2
  exit 5
fi

printf '%s\n' "==> Execute GDS closed-loop acceptance"
cd "${ROOT}"
if ! pytest -q "${ROOT}/native_acceptance/runtime/test_ref_projection_runtime.py" \
  --junitxml="${JUNIT}"; then
  echo "error: F Prime GDS closed-loop test failed" >&2
  cat "${GDS_LOG}" >&2
  exit 6
fi

python - "${GENERATED}/integration_result.json" "${PROJECT}/HARNESS_MANIFEST.json" \
  "${DICTIONARY}" "${JUNIT}" "${EVIDENCE}/native_runtime_acceptance.json" <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

result_path, harness_path, dictionary_path, junit_path, output_path = map(Path, sys.argv[1:])
result = json.loads(result_path.read_text(encoding="utf-8"))
harness = json.loads(harness_path.read_text(encoding="utf-8"))

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

if result.get("result") != "succeeded":
    raise SystemExit("canonical Integration Result did not succeed")

payload = {
    "kind": "orbitfabric.fprime.native_runtime_acceptance",
    "version": "0.1-candidate",
    "status": "passed",
    "operation": "fpp_contract_projection",
    "fprime": harness["fprime"],
    "fpp": harness["fpp"],
    "integration_result_sha256": digest(result_path),
    "fixture_manifest_sha256": digest(harness_path),
    "dictionary_sha256": digest(dictionary_path),
    "runtime_junit_sha256": digest(junit_path),
    "command": {
        "name": "Ref.pingRcvr.OF_SetMode",
        "arguments": [2],
        "completion": "observed",
    },
    "telemetry": {
        "name": "Ref.pingRcvr.OF_Temperature",
        "expected_value": 22.0,
        "observed": True,
    },
    "event": {
        "name": "Ref.pingRcvr.OF_ModeChanged",
        "observed": True,
    },
    "note": "Runtime behavior is evidence-only fixture behavior, not OrbitFabric mission semantics.",
}
output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, sort_keys=True))
PY

printf '%s\n' "PASS: canonical F Prime GDS closed-loop acceptance"
printf 'Evidence: %s\n' "${EVIDENCE}/native_runtime_acceptance.json"
