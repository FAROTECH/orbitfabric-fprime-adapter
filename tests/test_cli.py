from __future__ import annotations

import pytest

from orbitfabric_fprime_adapter.cli import main


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])

    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == "orbitfabric-fprime 0.1.0.dev0"


def test_reserved_operation_is_not_implemented_yet(
    capsys: pytest.CaptureFixture[str],
) -> None:
    status = main(
        [
            "run",
            "--operation",
            "fpp_contract_projection",
            "--input-set-manifest",
            "input.json",
            "--profile",
            "profile.yaml",
            "--output-dir",
            "out",
        ]
    )

    assert status == 2
    assert "not included in the initial product bootstrap baseline" in capsys.readouterr().err
