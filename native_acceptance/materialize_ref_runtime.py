#!/usr/bin/env python3
"""Extend the native Ref fixture with evidence-only runtime observability."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"{path}: expected exactly one runtime patch anchor, found {count}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fprime-root", type=Path, required=True)
    parser.add_argument("--fpp-root", type=Path, required=True)
    parser.add_argument("--generated-dir", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output-project", type=Path, required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    static_materializer = root / "materialize_ref_static.py"
    subprocess.run(
        [
            sys.executable,
            str(static_materializer),
            "--fprime-root",
            str(args.fprime_root),
            "--fpp-root",
            str(args.fpp_root),
            "--generated-dir",
            str(args.generated_dir),
            "--profile",
            str(args.profile),
            "--output-project",
            str(args.output_project),
        ],
        check=True,
    )

    implementation = args.output_project / "Ref/PingReceiver/PingReceiverComponentImpl.cpp"
    handler_signature = (
        "void PingReceiverComponentImpl::OF_SetMode_cmdHandler("
        "FwOpcodeType opCode, U32 cmdSeq, U32 mode) {\n"
    )
    static_handler = (
        handler_signature
        + "    (void)mode;\n"
        + "    this->cmdResponse_out(opCode, cmdSeq, Fw::CmdResponse::OK);\n"
        + "}\n"
    )
    runtime_handler = (
        handler_signature
        + "    // Evidence-only behavior. This is not OrbitFabric mission semantics.\n"
        + "    const F32 temperature = 20.0F + static_cast<F32>(mode);\n"
        + "    this->tlmWrite_OF_Temperature(temperature);\n"
        + "    this->log_ACTIVITY_HI_OF_ModeChanged();\n"
        + "    this->cmdResponse_out(opCode, cmdSeq, Fw::CmdResponse::OK);\n"
        + "}\n"
    )
    replace_once(implementation, static_handler, runtime_handler)

    manifest_path = args.output_project / "HARNESS_MANIFEST.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["kind"] = "orbitfabric.fprime.native_runtime_fixture"
    manifest["version"] = "0.1-candidate"
    manifest["fixture_behavior"] = (
        "Evidence-only command handler maps mode N to temperature 20+N, emits the "
        "projected event and returns command OK."
    )
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print("materialized F Prime native runtime fixture")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
