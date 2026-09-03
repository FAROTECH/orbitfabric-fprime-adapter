from __future__ import annotations

import pytest

from orbitfabric_fprime_adapter.cli import main


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])

    assert exc.value.code == 0
    assert capsys.readouterr().out.strip() == "orbitfabric-fprime 0.1.0.dev0"


def test_unknown_operation_is_rejected(
    capsys: pytest.CaptureFixture[str], tmp_path
) -> None:
    status = main(
        [
            "run",
            "--operation",
            "unknown_operation",
            "--input-set-manifest",
            "input.json",
            "--profile",
            "profile.yaml",
            "--output-dir",
            str(tmp_path / "out"),
        ]
    )

    assert status == 2
    assert "unsupported operation: unknown_operation" in capsys.readouterr().err


def test_projection_operation_rejects_additional_operation_input(
    capsys: pytest.CaptureFixture[str], tmp_path
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
            str(tmp_path / "out"),
            "--operation-input",
            "scenario=unexpected.json",
        ]
    )

    assert status == 2
    assert "does not accept operation inputs" in capsys.readouterr().err
