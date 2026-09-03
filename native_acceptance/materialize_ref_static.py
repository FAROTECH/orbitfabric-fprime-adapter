#!/usr/bin/env python3
"""Materialize an ephemeral F Prime Ref project for native static acceptance."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
from typing import Any

import yaml

FPRIME_COMMIT = "8a62e455a90b6d4f498c332d45d65a2a819988d8"
FPRIME_VERSION = "v4.2.2"
FPP_COMMIT = "93f484b7521a8e8894cba25b26e633cc87d8e37a"
FPP_VERSION = "3.2.0"
COMPONENT = "Ref.PingReceiver"
INSTANCE = "pingRcvr"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(
            f"{path}: expected exactly one patch anchor, found {count}: {old!r}"
        )
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: expected a YAML mapping")
    return value


def one_binding(profile: dict[str, Any], kind: str) -> dict[str, Any]:
    matches = [
        item
        for item in profile.get("bindings", [])
        if item.get("config", {}).get("kind") == kind
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"static acceptance requires exactly one {kind} binding, found {len(matches)}"
        )
    return matches[0]


def verify_git_checkout(path: Path, expected_commit: str, label: str) -> str:
    if not (path / ".git").exists():
        raise RuntimeError(f"{label} checkout not found at {path}")
    actual = subprocess.check_output(
        ["git", "-C", str(path), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != expected_commit:
        raise RuntimeError(
            f"unsupported {label} checkout: expected {expected_commit}, got {actual}"
        )
    return actual


def verify_profile(profile: dict[str, Any]) -> tuple[dict, dict, dict, dict]:
    target = profile.get("settings", {}).get("target", {})
    fprime = target.get("fprime", {})
    fpp = target.get("fpp", {})
    if fprime.get("version") != FPRIME_VERSION or fprime.get("commit") != FPRIME_COMMIT:
        raise RuntimeError("acceptance Profile does not target the pinned F Prime baseline")
    if fpp.get("version") != FPP_VERSION or fpp.get("commit") != FPP_COMMIT:
        raise RuntimeError("acceptance Profile does not target the pinned FPP baseline")

    telemetry = one_binding(profile, "telemetry")
    command = one_binding(profile, "command")
    event = one_binding(profile, "event")
    packet = one_binding(profile, "packet")

    for binding in (telemetry, command, event):
        config = binding["config"]
        if config.get("host_component") != COMPONENT or config.get("host_instance") != INSTANCE:
            raise RuntimeError(
                f"Ref acceptance only supports {COMPONENT} with instance {INSTANCE}"
            )

    if command["config"].get("symbol") != "OF_SetMode":
        raise RuntimeError("Ref acceptance expects command symbol OF_SetMode")
    if telemetry["config"].get("symbol") != "OF_Temperature":
        raise RuntimeError("Ref acceptance expects telemetry symbol OF_Temperature")
    if event["config"].get("symbol") != "OF_ModeChanged":
        raise RuntimeError("Ref acceptance expects event symbol OF_ModeChanged")
    if packet["config"].get("packet_set") != "RefPackets":
        raise RuntimeError("Ref acceptance expects packet set RefPackets")

    return telemetry, command, event, packet


def extract_explicit_ids(text: str, keyword: str, field: str) -> set[int]:
    # This is fixture-only preflight against one pinned Ref source tree.
    # Product projection code does not parse downstream FPP with regular expressions.
    pattern = (
        rf"\b{re.escape(keyword)}\s+[A-Za-z_][A-Za-z0-9_]*"
        rf"(?:\([^)]*\))?[\s\S]*?\b{re.escape(field)}\s+"
        r"(0x[0-9A-Fa-f]+|\d+)"
    )
    return {int(value, 0) for value in re.findall(pattern, text, flags=re.MULTILINE)}


def extract_packet_ids(text: str) -> set[int]:
    pattern = r"\bpacket\s+[A-Za-z_][A-Za-z0-9_]*\s+id\s+(0x[0-9A-Fa-f]+|\d+)"
    return {int(value, 0) for value in re.findall(pattern, text)}


def preflight_allocations(
    source_ref: Path,
    telemetry: dict[str, Any],
    command: dict[str, Any],
    event: dict[str, Any],
    packet: dict[str, Any],
) -> None:
    component_text = (source_ref / "PingReceiver/PingReceiver.fpp").read_text(
        encoding="utf-8"
    )
    packet_text = (source_ref / "Top/RefPackets.fppi").read_text(encoding="utf-8")

    checks = [
        (
            "command opcode",
            command["config"]["local_opcode"],
            extract_explicit_ids(component_text, "command", "opcode"),
        ),
        (
            "event id",
            event["config"]["local_id"],
            extract_explicit_ids(component_text, "event", "id"),
        ),
        (
            "telemetry id",
            telemetry["config"]["local_id"],
            extract_explicit_ids(component_text, "telemetry", "id"),
        ),
        (
            "packet id",
            packet["config"]["packet_id"],
            extract_packet_ids(packet_text),
        ),
    ]
    for label, value, existing in checks:
        if value in existing:
            raise RuntimeError(
                f"Ref acceptance collision: {label} {value} already exists in pinned Ref"
            )


def require_files(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.is_file()]
    if missing:
        raise RuntimeError("missing canonical adapter artifacts: " + ", ".join(missing))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fprime-root", type=Path, required=True)
    parser.add_argument("--fpp-root", type=Path, required=True)
    parser.add_argument("--generated-dir", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--output-project", type=Path, required=True)
    args = parser.parse_args()

    fprime_root = args.fprime_root.resolve()
    fpp_root = args.fpp_root.resolve()
    generated = args.generated_dir.resolve()
    profile_path = args.profile.resolve()
    output_project = args.output_project.resolve()
    output_ref = output_project / "Ref"

    actual_fprime = verify_git_checkout(fprime_root, FPRIME_COMMIT, "F Prime")
    actual_fpp = verify_git_checkout(fpp_root, FPP_COMMIT, "FPP")
    profile = load_yaml(profile_path)
    telemetry, command, event, packet = verify_profile(profile)

    source_ref = fprime_root / "Ref"
    preflight_allocations(source_ref, telemetry, command, event, packet)

    generated_component = generated / "components/Ref_PingReceiver"
    commands = generated_component / "OF_Commands.fppi"
    events = generated_component / "OF_Events.fppi"
    telemetry_file = generated_component / "OF_Telemetry.fppi"
    packets = generated / "topology/RefPackets/OF_Packets.fppi"
    result_file = generated / "integration_result.json"
    require_files([commands, events, telemetry_file, packets, result_file])

    if output_project.exists():
        shutil.rmtree(output_project)
    output_project.mkdir(parents=True)
    shutil.copytree(source_ref, output_ref)

    (output_ref / "settings.ini").write_text(
        "[fprime]\n"
        "project_root: ..\n"
        f"framework_path: {fprime_root}\n",
        encoding="utf-8",
    )
    replace_once(
        output_ref / "CMakeLists.txt",
        'find_package(FPrime REQUIRED PATHS "${CMAKE_CURRENT_LIST_DIR}/..")',
        'find_package(FPrime REQUIRED PATHS "${FPRIME_FRAMEWORK_PATH}")',
    )

    replace_once(
        output_ref / "PingReceiver/PingReceiverComponentImpl.cpp",
        "#include <Ref/PingReceiver/PingReceiverComponentImpl.hpp>",
        '#include "PingReceiverComponentImpl.hpp"',
    )

    top_cmake = output_ref / "Top/CMakeLists.txt"
    with top_cmake.open("a", encoding="utf-8") as stream:
        stream.write(
            "\n# Native acceptance: prefer copied Ref implementation headers.\n"
            'target_include_directories(Ref_Top BEFORE PRIVATE "${FPRIME_PROJECT_ROOT}")\n'
        )

    component_generated = output_ref / "PingReceiver/generated"
    component_generated.mkdir(parents=True)
    shutil.copy2(commands, component_generated / commands.name)
    shutil.copy2(events, component_generated / events.name)
    shutil.copy2(telemetry_file, component_generated / telemetry_file.name)

    topology_generated = output_ref / "Top/generated"
    topology_generated.mkdir(parents=True)
    shutil.copy2(packets, topology_generated / packets.name)

    include_block = (
        "\n    # OrbitFabric-generated contract fragments for native acceptance\n"
        '    include "generated/OF_Commands.fppi"\n'
        '    include "generated/OF_Events.fppi"\n'
        '    include "generated/OF_Telemetry.fppi"\n'
    )
    replace_once(
        output_ref / "PingReceiver/PingReceiver.fpp",
        "\n  }\n\n}\n",
        include_block + "\n  }\n\n}\n",
    )
    replace_once(
        output_ref / "Top/RefPackets.fppi",
        "\n} omit {\n",
        '\n  include "generated/OF_Packets.fppi"\n\n} omit {\n',
    )

    # F Prime component implementations must implement generated command handlers.
    # This fixture-only handler exists solely to make native static linking possible.
    handler_decl = (
        "    //! Native acceptance handler for the generated command declaration.\n"
        "    void OF_SetMode_cmdHandler(FwOpcodeType opCode, U32 cmdSeq, U32 mode);\n\n"
    )
    replace_once(
        output_ref / "PingReceiver/PingReceiverComponentImpl.hpp",
        "    bool m_inhibitPings;\n",
        handler_decl + "    bool m_inhibitPings;\n",
    )
    handler_impl = r'''

void PingReceiverComponentImpl::OF_SetMode_cmdHandler(FwOpcodeType opCode, U32 cmdSeq, U32 mode) {
    (void)mode;
    this->cmdResponse_out(opCode, cmdSeq, Fw::CmdResponse::OK);
}
'''
    replace_once(
        output_ref / "PingReceiver/PingReceiverComponentImpl.cpp",
        "\n}  // end namespace Ref\n",
        handler_impl + "\n}  // end namespace Ref\n",
    )

    manifest = {
        "kind": "orbitfabric.fprime.native_static_fixture",
        "version": "0.1-candidate",
        "fprime": {"version": FPRIME_VERSION, "commit": actual_fprime},
        "fpp": {"version": FPP_VERSION, "commit": actual_fpp},
        "source_deployment": "Ref",
        "target_component": COMPONENT,
        "target_instance": INSTANCE,
        "profile_sha256": sha256_file(profile_path),
        "integration_result_sha256": sha256_file(result_file),
        "generated_artifacts": {
            path.name: sha256_file(path)
            for path in (commands, events, telemetry_file, packets)
        },
        "fixture_behavior": "Minimal command handler required only for static linking.",
    }
    (output_project / "HARNESS_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(f"materialized F Prime native static fixture: {output_ref}")
    print(f"F Prime: {FPRIME_VERSION} @ {actual_fprime}")
    print(f"FPP source: {FPP_VERSION} @ {actual_fpp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
