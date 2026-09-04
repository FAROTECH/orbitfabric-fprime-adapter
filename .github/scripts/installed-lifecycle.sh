#!/usr/bin/env bash
set -euo pipefail

if [[ "${GITHUB_ACTIONS:-}" != "true" ]]; then
  echo "This destructive isolation proof must run only inside GitHub Actions." >&2
  exit 2
fi

root="${GITHUB_WORKSPACE:?GITHUB_WORKSPACE is required}"
work="/tmp/orbitfabric-fprime-installed-lifecycle"
state="$work/state"
evidence="$work/evidence"
wheelhouse="$work/wheelhouse"
release_dir="$work/release"

export ORBITFABRIC_STATE_DIR="$state"

rm -rf "$work"
mkdir -p "$evidence" "$wheelhouse" "$release_dir"

cd "$root"
rm -rf dist
python -m build --wheel
wheel="$(realpath "$(find "$root/dist" -maxdepth 1 -name '*.whl' -print -quit)")"
test -n "$wheel"

python tools/build_release_bundle.py \
  --wheel "$wheel" \
  --authority github.com \
  --publisher FAROTECH \
  --name orbitfabric/fprime \
  --output-dir "$release_dir"

descriptor="$release_dir/adapter-release.json"
descriptor_sha="$(sha256sum "$descriptor" | awk '{print $1}')"

cp "$descriptor" "$evidence/release-descriptor.json"
sha256sum "$wheel" > "$evidence/adapter-wheel.sha256"

python -m pip download --dest "$wheelhouse" "$wheel"
python -m pip download --dest "$wheelhouse" "hatchling>=1.24"

export PIP_NO_INDEX=1
export PIP_FIND_LINKS="$wheelhouse"
orbitfabric adapter install "$descriptor" \
  --artifact "$wheel" \
  --descriptor-sha256 "$descriptor_sha" \
  --json | tee "$evidence/install.json"
unset PIP_NO_INDEX
unset PIP_FIND_LINKS

EVIDENCE="$evidence" python - <<'PY' > "$work/install-env"
import json
import os
from pathlib import Path

record = json.loads((Path(os.environ["EVIDENCE"]) / "install.json").read_text(encoding="utf-8"))
assert record["backend_id"] == "python-wheel-managed-env"
assert Path(record["execution_argv_prefix"][0]).is_absolute()
assert Path(record["manifest_path"]).is_file()
print("INSTANCE_ID=" + record["instance_id"])
print("EXECUTABLE=" + record["execution_argv_prefix"][0])
PY
source "$work/install-env"

rm -f "$wheel" "$descriptor"
rm -rf "$wheelhouse"
rm -rf "$root/src"
test ! -e "$wheel"
test ! -d "$root/src"

cd /tmp
PYTHONPATH= orbitfabric adapter verify "$INSTANCE_ID" --json | tee "$evidence/verify.json"

EVIDENCE="$evidence" python - <<'PY'
import json
import os
from pathlib import Path

report = json.loads((Path(os.environ["EVIDENCE"]) / "verify.json").read_text(encoding="utf-8"))
for name in (
    "release_descriptor_integrity",
    "manifest_integrity",
    "manifest_conformance",
    "execution_binding",
    "backend_materialization",
):
    assert report[name]["status"] == "PASS", (name, report[name])
PY

"$EXECUTABLE" --version | tee "$evidence/console-version.txt"
grep -Fxq "orbitfabric-fprime 0.1.0" "$evidence/console-version.txt"

orbitfabric adapter remove "$INSTANCE_ID" --json | tee "$evidence/remove.json"
orbitfabric adapter list --json | tee "$evidence/final-inventory.json"

EVIDENCE="$evidence" python - <<'PY'
import json
import os
from pathlib import Path

inventory = json.loads(
    (Path(os.environ["EVIDENCE"]) / "final-inventory.json").read_text(encoding="utf-8")
)
assert inventory == []
PY
