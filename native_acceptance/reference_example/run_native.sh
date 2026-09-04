#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
FPRIME_ROOT="${1:?F Prime checkout required}"
FPP_ROOT="${2:?FPP checkout required}"
CORE_ROOT="${3:?OrbitFabric Core checkout required}"
WORK_ROOT="${4:-${ROOT}/.reference-example-native-work}"
FPRIME_COMMIT="8a62e455a90b6d4f498c332d45d65a2a819988d8"
FPP_COMMIT="93f484b7521a8e8894cba25b26e633cc87d8e37a"

[[ "$(git -C "${FPRIME_ROOT}" rev-parse HEAD)" == "${FPRIME_COMMIT}" ]] || {
  echo "error: F Prime source mismatch" >&2
  exit 3
}
[[ "$(git -C "${FPP_ROOT}" rev-parse HEAD)" == "${FPP_COMMIT}" ]] || {
  echo "error: FPP source mismatch" >&2
  exit 3
}

rm -rf "${WORK_ROOT}"
mkdir -p "${WORK_ROOT}/evidence"

printf '%s\n' "==> Generate one Core Input Set and both canonical projections"
python "${ROOT}/examples/reference-contract-evolution/verify_reference_example.py" \
  --core-root "${CORE_ROOT}" \
  --work-dir "${WORK_ROOT}/consumer"

for layout in a b; do
  if [[ "${layout}" == "a" ]]; then
    projection="${WORK_ROOT}/consumer/layout-a"
  else
    projection="${WORK_ROOT}/consumer/layout-b"
  fi
  project="${WORK_ROOT}/native-${layout}"

  printf '%s\n' "==> Materialize native Reference Example layout ${layout}"
  python "${ROOT}/native_acceptance/reference_example/materialize_layout.py" \
    --fprime-root "${FPRIME_ROOT}" \
    --projection "${projection}" \
    --layout "${layout}" \
    --output-project "${project}"

  printf '%s\n' "==> F Prime generate layout ${layout}"
  (cd "${project}/Ref" && fprime-util generate)

  printf '%s\n' "==> F Prime build layout ${layout}"
  (cd "${project}/Ref" && fprime-util build)

  dictionary="${project}/Ref/build-artifacts/Linux/Ref/dict/RefTopologyDictionary.json"
  if [[ ! -f "${dictionary}" ]]; then
    dictionary="$(find "${project}/Ref" -type f -name 'RefTopologyDictionary.json' -print -quit)"
  fi
  if [[ -z "${dictionary}" || ! -f "${dictionary}" ]]; then
    echo "error: layout ${layout} generated dictionary not found" >&2
    exit 4
  fi
  cp "${dictionary}" "${WORK_ROOT}/evidence/layout-${layout}-dictionary.json"
done

printf '%s\n' "==> Verify stable OrbitFabric identity and evolved native F Prime resolution"
python "${ROOT}/native_acceptance/reference_example/verify_native_layouts.py" \
  --consumer-proof "${WORK_ROOT}/consumer/reference-example-proof.json" \
  --dictionary-a "${WORK_ROOT}/evidence/layout-a-dictionary.json" \
  --dictionary-b "${WORK_ROOT}/evidence/layout-b-dictionary.json" \
  --output "${WORK_ROOT}/evidence/reference-example-native-acceptance.json"

printf '%s\n' "PASS: Reference Example native two-layout acceptance"
