from __future__ import annotations

import json
import tomllib
from pathlib import Path

from orbitfabric_fprime_adapter import __version__
from orbitfabric_fprime_adapter.constants import (
    ADAPTER_ID,
    CONSOLE_COMMAND,
    DISTRIBUTION_NAME,
    INTEGRATION_ID,
    OPERATION_ID,
    PYTHON_PACKAGE,
    SOURCE_COORDINATE,
    VERSION,
)

ROOT = Path(__file__).resolve().parents[1]


def test_canonical_identity() -> None:
    assert __version__ == VERSION
    assert DISTRIBUTION_NAME == "orbitfabric-fprime-adapter"
    assert PYTHON_PACKAGE == "orbitfabric_fprime_adapter"
    assert CONSOLE_COMMAND == "orbitfabric-fprime"
    assert ADAPTER_ID == "orbitfabric-fprime"
    assert INTEGRATION_ID == "orbitfabric-fprime"
    assert OPERATION_ID == "fpp_contract_projection"
    assert SOURCE_COORDINATE == {
        "authority": "github.com/OrbitFabric",
        "publisher": "orbitfabric",
        "name": "fprime",
    }


def test_release_version_surfaces_are_coherent() -> None:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    manifest = json.loads(
        (ROOT / "src/orbitfabric_fprime_adapter/integration_package.json").read_text(
            encoding="utf-8"
        )
    )

    assert pyproject["project"]["version"] == VERSION
    assert manifest["adapter"]["version"] == VERSION
