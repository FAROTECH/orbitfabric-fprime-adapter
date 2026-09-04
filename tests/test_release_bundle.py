from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

from orbitfabric_fprime_adapter.constants import SOURCE_COORDINATE, VERSION

ROOT = Path(__file__).resolve().parents[1]


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
            str(ROOT / "src/orbitfabric_fprime_adapter/integration_package.json"),
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

    assert descriptor["source_coordinate"] == SOURCE_COORDINATE
    assert descriptor["release_version"] == VERSION
    assert artifact["filename"] == wheel.name
    assert artifact["sha256"] == hashlib.sha256(wheel.read_bytes()).hexdigest()
