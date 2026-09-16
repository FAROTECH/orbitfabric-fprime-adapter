from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from orbitfabric_fprime_adapter.constants import SOURCE_COORDINATE, VERSION

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "src/orbitfabric_fprime_adapter/integration_package.json"


def test_release_bundle_defaults_to_canonical_product_identity(tmp_path: Path) -> None:
    wheel = tmp_path / f"orbitfabric_fprime_adapter-{VERSION}-py3-none-any.whl"
    wheel.write_bytes(b"release-identity-regression-fixture\n")
    output_dir = tmp_path / "release"

    subprocess.run(
        [
            sys.executable,
            "tools/build_release_bundle.py",
            "--wheel",
            str(wheel),
            "--manifest",
            str(MANIFEST),
            "--output-dir",
            str(output_dir),
            "--release-only",
        ],
        cwd=ROOT,
        check=True,
    )

    descriptor = json.loads(
        (output_dir / "adapter-release.json").read_text(encoding="utf-8")
    )
    artifact = descriptor["artifacts"][0]
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert descriptor["source_coordinate"] == SOURCE_COORDINATE
    assert descriptor["release_version"] == VERSION
    assert descriptor["integration_package"]["sha256"] == hashlib.sha256(
        MANIFEST.read_bytes()
    ).hexdigest()
    assert manifest["adapter"]["version"] == VERSION
    assert artifact["filename"] == wheel.name
    assert artifact["sha256"] == hashlib.sha256(wheel.read_bytes()).hexdigest()


def test_release_bundle_rejects_manifest_version_drift(tmp_path: Path) -> None:
    wheel = tmp_path / f"orbitfabric_fprime_adapter-{VERSION}-py3-none-any.whl"
    wheel.write_bytes(b"release-version-drift-fixture\n")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["adapter"]["version"] = "9.9.9"
    drifted_manifest = tmp_path / "integration_package.json"
    drifted_manifest.write_text(json.dumps(manifest), encoding="utf-8")

    completed = subprocess.run(
        [
            sys.executable,
            "tools/build_release_bundle.py",
            "--wheel",
            str(wheel),
            "--manifest",
            str(drifted_manifest),
            "--output-dir",
            str(tmp_path / "release"),
            "--release-only",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "Release version and Integration Package adapter.version differ" in completed.stderr
