#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
FPRIME_ROOT="${1:-${ROOT}/_native/fprime}"
FPP_ROOT="${2:-${ROOT}/_native/fpp}"
WORK_ROOT="${3:-${ROOT}/.native-static-work}"
CASE_ROOT="${ROOT}/native_acceptance/ref"
GENERATED="${WORK_ROOT}/generated"
PROJECT="${WORK_ROOT}/project"
DEPLOYMENT="${PROJECT}/Ref"
EVIDENCE="${WORK_ROOT}/evidence"
FPRIME_COMMIT="8a62e455a90b6d4f498c332d45d65a2a819988d8"
FPP_COMMIT="93f484b7521a8e8894cba25b26e633cc87d8e37a"

command -v python >/dev/null || { echo "error: python not found" >&2; exit 2; }
command -v orbitfabric-fprime >/dev/null || { echo "error: orbitfabric-fprime not found" >&2; exit 2; }
command -v fprime-util >/dev/null || { echo "error: fprime-util not found" >&2; exit 2; }

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

printf '%s\n' "==> Materialize ephemeral pinned Ref fixture"
python "${ROOT}/native_acceptance/materialize_ref_static.py" \
  --fprime-root "${FPRIME_ROOT}" \
  --fpp-root "${FPP_ROOT}" \
  --generated-dir "${GENERATED}" \
  --profile "${CASE_ROOT}/profile.yaml" \
  --output-project "${PROJECT}"

cd "${DEPLOYMENT}"
printf '%s\n' "==> F Prime generate"
fprime-util generate

printf '%s\n' "==> F Prime build"
fprime-util build

DICTIONARY="${DEPLOYMENT}/build-artifacts/Linux/Ref/dict/RefTopologyDictionary.json"
if [[ ! -f "${DICTIONARY}" ]]; then
  DICTIONARY="$(find "${DEPLOYMENT}" -type f -name 'RefTopologyDictionary.json' -print -quit)"
fi
if [[ -z "${DICTIONARY}" || ! -f "${DICTIONARY}" ]]; then
  echo "error: F Prime generated dictionary not found" >&2
  find "${DEPLOYMENT}" -type f -name '*Dictionary.json' -print >&2 || true
  exit 4
fi

printf '%s\n' "==> Canonical dictionary conformance"
python "${ROOT}/native_acceptance/check_fprime_dictionary.py" \
  "${DICTIONARY}" \
  "${CASE_ROOT}/dictionary_expectations.yaml" \
  --output "${EVIDENCE}/dictionary_conformance.json"

python - "${GENERATED}/integration_result.json" "${PROJECT}/HARNESS_MANIFEST.json" \
  "${EVIDENCE}/dictionary_conformance.json" "${EVIDENCE}/native_static_acceptance.json" <<'PY'
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

result_path, harness_path, dictionary_path, output_path = map(Path, sys.argv[1:])
result = json.loads(result_path.read_text(encoding="utf-8"))
harness = json.loads(harness_path.read_text(encoding="utf-8"))
dictionary = json.loads(dictionary_path.read_text(encoding="utf-8"))

def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

if result.get("result") != "succeeded":
    raise SystemExit("canonical Integration Result did not succeed")
if dictionary.get("status") != "passed":
    raise SystemExit("dictionary conformance did not pass")

payload = {
    "kind": "orbitfabric.fprime.native_static_acceptance",
    "version": "0.1-candidate",
    "status": "passed",
    "operation": "fpp_contract_projection",
    "fprime": harness["fprime"],
    "fpp": harness["fpp"],
    "integration_result_sha256": digest(result_path),
    "fixture_manifest_sha256": digest(harness_path),
    "dictionary_conformance_sha256": digest(dictionary_path),
    "dictionary": dictionary["dictionary"],
    "resolutions": dictionary["resolutions"],
    "checks": [
        "canonical_projection",
        "exact_fprime_source",
        "exact_fpp_source",
        "fprime_generate",
        "fprime_build",
        "generated_dictionary_conformance",
    ],
}
output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
print(json.dumps(payload, indent=2, sort_keys=True))
PY

printf '%s\n' "PASS: canonical F Prime native static acceptance"
printf 'Evidence: %s\n' "${EVIDENCE}/native_static_acceptance.json"
