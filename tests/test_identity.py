from __future__ import annotations

from orbitfabric_fprime_adapter import __version__
from orbitfabric_fprime_adapter.constants import (
    ADAPTER_ID,
    CONSOLE_COMMAND,
    DISTRIBUTION_NAME,
    INTEGRATION_ID,
    OPERATION_ID,
    PYTHON_PACKAGE,
    SOURCE_COORDINATE,
)


def test_canonical_identity() -> None:
    assert __version__ == "0.1.1"
    assert DISTRIBUTION_NAME == "orbitfabric-fprime-adapter"
    assert PYTHON_PACKAGE == "orbitfabric_fprime_adapter"
    assert CONSOLE_COMMAND == "orbitfabric-fprime"
    assert ADAPTER_ID == "orbitfabric-fprime"
    assert INTEGRATION_ID == "orbitfabric-fprime"
    assert OPERATION_ID == "fpp_contract_projection"
    assert SOURCE_COORDINATE == {
        "authority": "github.com/FAROTECH",
        "publisher": "orbitfabric",
        "name": "fprime",
    }
