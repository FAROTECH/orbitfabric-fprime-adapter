#!/usr/bin/env python3
"""Materialize one Reference Example layout inside an ephemeral pinned Ref host."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

FPRIME_COMMIT = "8a62e455a90b6d4f498c332d45d65a2a819988d8"
COMMANDS = [
    ("OF_StartAcquisition", [("U16", "duration_s")]),
    ("OF_StopAcquisition", []),
]


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise RuntimeError(f"{path}: expected one patch anchor: {old!r}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def append_before_last_brace(path: Path, block: str) -> None:
    text = path.read_text(encoding="utf-8")
    pos = text.rfind("}\n")
    if pos < 0:
        raise RuntimeError(f"{path}: closing brace not found")
    path.write_text(text[:pos] + block + text[pos:], encoding="utf-8")


def telemetry_refs_in_packet_set(path: Path) -> list[str]:
    """Collect complete qualified channel references from one FPP packet set."""
    text = path.read_text(encoding="utf-8")
    uncommented = "\n".join(line.split("#", 1)[0] for line in text.splitlines())
    segment = r"\$?[A-Za-z_][A-Za-z0-9_]*"
    refs = re.findall(
        rf"(?<![A-Za-z0-9_$]){segment}(?:\.{segment})+(?![A-Za-z0-9_$])",
        uncommented,
    )
    values = sorted(set(refs))
    if not values:
        raise RuntimeError(f"{path}: no telemetry references found")
    return values


def handler_signature(command: str, parameters: list[tuple[str, str]]) -> str:
    suffix = "".join(f", {type_name} {name}" for type_name, name in parameters)
    return f"{command}_cmdHandler(FwOpcodeType opCode, U32 cmdSeq{suffix})"


def component_files(
    project: Path,
    name: str,
    generated: Path,
    commands: list[tuple[str, list[tuple[str, str]]]],
) -> None:
    root = project / "Ref" / "Reference" / name
    generated_root = root / "generated"
    generated_root.mkdir(parents=True, exist_ok=True)

    for filename in ("OF_Commands.fppi", "OF_Events.fppi", "OF_Telemetry.fppi"):
        source = generated / filename
        if source.is_file():
            shutil.copy2(source, generated_root / filename)

    includes = []
    if (generated_root / "OF_Commands.fppi").is_file():
        includes.append('    include "generated/OF_Commands.fppi"')
    if (generated_root / "OF_Events.fppi").is_file():
        includes.append('    include "generated/OF_Events.fppi"')
    if (generated_root / "OF_Telemetry.fppi").is_file():
        includes.append('    include "generated/OF_Telemetry.fppi"')

    kind = "active" if commands else "passive"
    imports = ["    time get port timeCaller"]
    if (generated_root / "OF_Commands.fppi").is_file():
        imports.append("    import Fw.Command")
    if (generated_root / "OF_Events.fppi").is_file():
        imports.append("    import Fw.Event")
    if (generated_root / "OF_Telemetry.fppi").is_file():
        imports.append("    import Fw.Channel")

    fpp = (
        "module Reference {\n"
        f"  {kind} component {name} {{\n"
        + "\n".join(imports)
        + "\n\n"
        + "\n".join(includes)
        + "\n  }\n}\n"
    )
    (root / f"{name}.fpp").write_text(fpp, encoding="utf-8")

    impl_name = f"{name}ComponentImpl"
    base_name = f"{name}ComponentBase"
    header = [
        "#pragma once",
        f"#include <Ref/Reference/{name}/{name}ComponentAc.hpp>",
        "",
        "namespace Reference {",
        f"class {impl_name} final : public {base_name} {{",
        "  public:",
        f"    explicit {impl_name}(const char* const compName);",
        f"    ~{impl_name}();",
    ]
    if commands:
        header.extend(["", "  private:"])
        for command, parameters in commands:
            header.append(f"    void {handler_signature(command, parameters)};")
    header.extend(["};", "}  // namespace Reference", ""])
    (root / f"{impl_name}.hpp").write_text("\n".join(header), encoding="utf-8")

    source = [
        f'#include "{impl_name}.hpp"',
        "",
        "namespace Reference {",
        f"{impl_name}::{impl_name}(const char* const compName) : {base_name}(compName) {{}}",
        f"{impl_name}::~{impl_name}() {{}}",
    ]
    for command, parameters in commands:
        source.extend(
            [
                "",
                f"void {impl_name}::{handler_signature(command, parameters)} {{",
            ]
        )
        for _, parameter_name in parameters:
            source.append(f"    (void){parameter_name};")
        source.extend(
            [
                "    this->cmdResponse_out(opCode, cmdSeq, Fw::CmdResponse::OK);",
                "}",
            ]
        )
    source.extend(["}  // namespace Reference", ""])
    (root / f"{impl_name}.cpp").write_text("\n".join(source), encoding="utf-8")

    standardization_header = (
        "#pragma once\n"
        f'#include "Ref/Reference/{name}/{impl_name}.hpp"\n'
        "\n"
        "namespace Reference {\n"
        f"using {name} = {impl_name};\n"
        "}  // namespace Reference\n"
    )
    (root / f"{name}.hpp").write_text(standardization_header, encoding="utf-8")

    cmake = (
        "set(SOURCE_FILES\n"
        f'  "${{CMAKE_CURRENT_LIST_DIR}}/{name}.fpp"\n'
        f'  "${{CMAKE_CURRENT_LIST_DIR}}/{impl_name}.cpp"\n'
        ")\nregister_fprime_module()\n"
    )
    (root / "CMakeLists.txt").write_text(cmake, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fprime-root", type=Path, required=True)
    parser.add_argument("--projection", type=Path, required=True)
    parser.add_argument("--layout", choices=("a", "b"), required=True)
    parser.add_argument("--output-project", type=Path, required=True)
    args = parser.parse_args()

    fprime_root = args.fprime_root.resolve()
    actual = subprocess.check_output(
        ["git", "-C", str(fprime_root), "rev-parse", "HEAD"], text=True
    ).strip()
    if actual != FPRIME_COMMIT:
        raise RuntimeError(f"unexpected F Prime checkout: {actual}")

    projection = args.projection.resolve()
    project = args.output_project.resolve()
    deployment = project / "Ref"
    if project.exists():
        shutil.rmtree(project)
    project.mkdir(parents=True)
    shutil.copytree(fprime_root / "Ref", deployment)

    (deployment / "settings.ini").write_text(
        "[fprime]\nproject_root: ..\n" f"framework_path: {fprime_root}\n",
        encoding="utf-8",
    )
    replace_once(
        deployment / "CMakeLists.txt",
        'find_package(FPrime REQUIRED PATHS "${CMAKE_CURRENT_LIST_DIR}/..")',
        'find_package(FPrime REQUIRED PATHS "${FPRIME_FRAMEWORK_PATH}")',
    )
    replace_once(
        deployment / "PingReceiver/PingReceiverComponentImpl.cpp",
        "#include <Ref/PingReceiver/PingReceiverComponentImpl.hpp>",
        '#include "PingReceiverComponentImpl.hpp"',
    )
    with (deployment / "Top/CMakeLists.txt").open("a", encoding="utf-8") as stream:
        stream.write(
            "\n# Reference Example native fixture: prefer copied implementation headers.\n"
            'target_include_directories(Ref_Top BEFORE PRIVATE "${FPRIME_PROJECT_ROOT}")\n'
        )

    instances = deployment / "Top/instances.fpp"
    topology = deployment / "Top/topology.fpp"
    root_cmake = deployment / "CMakeLists.txt"

    if args.layout == "a":
        component_files(
            project,
            "PayloadComponent",
            projection / "components/Reference_PayloadComponent",
            COMMANDS,
        )
        reference_telemetry = "payload.OF_AcquisitionActive"
        add_fpp = (
            "\n  instance payload: Reference.PayloadComponent base id 0x10030000 \\\n"
            "    queue size Default.QUEUE_SIZE \\\n"
            "    stack size Default.STACK_SIZE \\\n"
            "    priority 18\n\n"
        )
        append_before_last_brace(instances, add_fpp)
        replace_once(
            topology,
            "    instance pingRcvr\n",
            "    instance pingRcvr\n    instance payload\n",
        )
        replace_once(
            root_cmake,
            'add_fprime_subdirectory("${CMAKE_CURRENT_LIST_DIR}/Top/")',
            'add_fprime_subdirectory("${CMAKE_CURRENT_LIST_DIR}/Reference/PayloadComponent/")\n'
            'add_fprime_subdirectory("${CMAKE_CURRENT_LIST_DIR}/Top/")',
        )
    else:
        component_files(
            project,
            "PayloadController",
            projection / "components/Reference_PayloadController",
            COMMANDS,
        )
        component_files(
            project,
            "PayloadMonitor",
            projection / "components/Reference_PayloadMonitor",
            [],
        )
        reference_telemetry = "payloadMonitor.OF_AcquisitionActive"
        add_fpp = (
            "\n  instance payloadController: Reference.PayloadController base id 0x10030000 \\\n"
            "    queue size Default.QUEUE_SIZE \\\n"
            "    stack size Default.STACK_SIZE \\\n"
            "    priority 18\n\n"
            "  instance payloadMonitor: Reference.PayloadMonitor base id 0x10031000\n\n"
        )
        append_before_last_brace(instances, add_fpp)
        replace_once(
            topology,
            "    instance pingRcvr\n",
            "    instance pingRcvr\n    instance payloadController\n    instance payloadMonitor\n",
        )
        replace_once(
            root_cmake,
            'add_fprime_subdirectory("${CMAKE_CURRENT_LIST_DIR}/Top/")',
            'add_fprime_subdirectory("${CMAKE_CURRENT_LIST_DIR}/Reference/PayloadController/")\n'
            'add_fprime_subdirectory("${CMAKE_CURRENT_LIST_DIR}/Reference/PayloadMonitor/")\n'
            'add_fprime_subdirectory("${CMAKE_CURRENT_LIST_DIR}/Top/")',
        )

    packet_fragment = projection / "topology/ReferencePackets/OF_Packets.fppi"
    if not packet_fragment.is_file():
        raise RuntimeError(f"missing generated packet fragment: {packet_fragment}")

    ref_packets = deployment / "Top/RefPackets.fppi"
    existing_ref_telemetry = telemetry_refs_in_packet_set(ref_packets)
    append_before_last_brace(ref_packets, f"  {reference_telemetry}\n")

    packet_dir = deployment / "Top/generated/ReferencePackets"
    packet_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(packet_fragment, packet_dir / "OF_Packets.fppi")
    omit_lines = "".join(f"  {name}\n" for name in existing_ref_telemetry)
    (deployment / "Top/ReferencePackets.fppi").write_text(
        "telemetry packets ReferencePackets {\n"
        '  include "generated/ReferencePackets/OF_Packets.fppi"\n'
        "} omit {\n"
        f"{omit_lines}"
        "}\n",
        encoding="utf-8",
    )
    replace_once(
        topology,
        '    include "RefPackets.fppi"\n',
        '    include "RefPackets.fppi"\n    include "ReferencePackets.fppi"\n',
    )

    manifest = {
        "kind": "orbitfabric.fprime.reference_example_native_fixture",
        "version": "0.1-candidate",
        "layout": args.layout,
        "fprime_commit": actual,
        "host_deployment": "Ref",
        "consumer_architecture": (
            ["Reference.PayloadComponent", "payload"]
            if args.layout == "a"
            else [
                "Reference.PayloadController",
                "payloadController",
                "Reference.PayloadMonitor",
                "payloadMonitor",
            ]
        ),
        "command_handler_contract": {
            command: [f"{type_name} {name}" for type_name, name in parameters]
            for command, parameters in COMMANDS
        },
        "packet_set_reconciliation": {
            "reference_telemetry": reference_telemetry,
            "ref_packet_set_omits_reference_telemetry": True,
            "reference_packet_set_omits_existing_ref_telemetry": True,
            "existing_ref_telemetry_count": len(existing_ref_telemetry),
        },
        "note": (
            "Pinned Ref is infrastructure-only evidence scaffolding; "
            "Reference.* components and placement are the acceptance subject."
        ),
    }
    (project / "REFERENCE_EXAMPLE_NATIVE_FIXTURE.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
