#!/usr/bin/env python3
"""Run the same OrbitFabric contract through two F Prime projection layouts."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


def run(command: list[str], *, cwd: Path | None = None) -> None:
    subprocess.run(command, cwd=cwd, check=True)


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: expected JSON object")
    return value


def mapping_targets(result: dict[str, Any]) -> dict[tuple[str, str], str]:
    targets: dict[tuple[str, str], str] = {}
    for mapping in result["mappings"]:
        source = mapping["sources"][0]
        target = mapping["targets"][0]
        targets[(source["domain"], source["id"])] = target["id"]
    return targets


def resolution_value(
    result: dict[str, Any], binding: str, property_name: str
) -> Any:
    wanted = f"resolution.{binding}.{property_name}"
    for record in result["resolutions"]:
        if record["id"] == wanted:
            if record["origin"] != "profile":
                raise RuntimeError(f"{wanted}: expected profile provenance")
            return record["value"]
    raise RuntimeError(f"missing resolution: {wanted}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--core-root", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()

    here = Path(__file__).resolve().parent
    work = args.work_dir.resolve()
    input_set = work / "input-set"
    out_a = work / "layout-a"
    out_b = work / "layout-b"
    proof_path = work / "reference-example-proof.json"

    mission = args.core_root.resolve() / "examples/demo-3u/mission"
    if not mission.is_dir():
        raise RuntimeError(f"Core reference mission not found: {mission}")

    work.mkdir(parents=True, exist_ok=True)
    run(
        [
            "orbitfabric",
            "export",
            "integration-input-set",
            str(mission),
            "--output-dir",
            str(input_set),
        ]
    )

    manifest = input_set / "integration_input_manifest.json"
    for profile, output in (
        (here / "profile-a-monolithic.yaml", out_a),
        (here / "profile-b-split.yaml", out_b),
    ):
        run(
            [
                "orbitfabric-fprime",
                "run",
                "--operation",
                "fpp_contract_projection",
                "--input-set-manifest",
                str(manifest),
                "--profile",
                str(profile),
                "--output-dir",
                str(output),
            ]
        )

    result_a = load_json(out_a / "integration_result.json")
    result_b = load_json(out_b / "integration_result.json")

    if result_a["result"] != "succeeded" or result_b["result"] != "succeeded":
        raise RuntimeError("both projections must succeed")
    if result_a["mission"] != result_b["mission"]:
        raise RuntimeError("mission identity changed between layouts")
    if result_a["inputs"]["core_input_set"] != result_b["inputs"]["core_input_set"]:
        raise RuntimeError("Core Integration Input Set changed between layouts")
    if result_a["coverage"]["status"] != "complete":
        raise RuntimeError("layout A coverage is not complete")
    if result_b["coverage"]["status"] != "complete":
        raise RuntimeError("layout B coverage is not complete")

    targets_a = mapping_targets(result_a)
    targets_b = mapping_targets(result_b)
    if set(targets_a) != set(targets_b):
        raise RuntimeError("OrbitFabric source identity set changed between layouts")

    expected_changes = {
        ("telemetry", "payload.acquisition.active"): (
            "payload.OF_AcquisitionActive",
            "payloadMonitor.OF_AcquisitionActive",
        ),
        ("commands", "payload.start_acquisition"): (
            "payload.OF_StartAcquisition",
            "payloadController.OF_StartAcquisition",
        ),
        ("commands", "payload.stop_acquisition"): (
            "payload.OF_StopAcquisition",
            "payloadController.OF_StopAcquisition",
        ),
        ("events", "payload.acquisition_started"): (
            "payload.OF_AcquisitionStarted",
            "payloadController.OF_AcquisitionStarted",
        ),
        ("events", "payload.acquisition_stopped"): (
            "payload.OF_AcquisitionStopped",
            "payloadController.OF_AcquisitionStopped",
        ),
    }
    for source, expected in expected_changes.items():
        actual = (targets_a[source], targets_b[source])
        if actual != expected:
            raise RuntimeError(f"unexpected target evolution for {source}: {actual}")

    packet_source = ("packets", "payload_status")
    expected_packet = "ReferencePackets.OF_PayloadStatus"
    if targets_a[packet_source] != expected_packet:
        raise RuntimeError("layout A packet identity changed unexpectedly")
    if targets_b[packet_source] != expected_packet:
        raise RuntimeError("layout B packet identity changed unexpectedly")

    if resolution_value(result_a, "payload-active", "host_component") != (
        "Reference.PayloadComponent"
    ):
        raise RuntimeError("layout A host component resolution is wrong")
    if resolution_value(result_b, "payload-active", "host_component") != (
        "Reference.PayloadMonitor"
    ):
        raise RuntimeError("layout B host component resolution is wrong")

    packet_a = (
        out_a / "topology/ReferencePackets/OF_Packets.fppi"
    ).read_text(encoding="utf-8")
    packet_b = (
        out_b / "topology/ReferencePackets/OF_Packets.fppi"
    ).read_text(encoding="utf-8")
    if "payload.OF_AcquisitionActive" not in packet_a:
        raise RuntimeError("layout A packet does not use monolithic telemetry placement")
    if "payloadMonitor.OF_AcquisitionActive" not in packet_b:
        raise RuntimeError("layout B packet does not use split telemetry placement")

    proof = {
        "kind": "orbitfabric.fprime.reference_contract_evolution",
        "version": "0.1",
        "adapter_version": "0.1.0",
        "status": "passed",
        "mission": result_a["mission"],
        "core_input_set_sha256": result_a["inputs"]["core_input_set"]["sha256"],
        "stable_sources": [
            {"domain": domain, "id": entity_id}
            for domain, entity_id in sorted(targets_a)
        ],
        "layout_a": {
            "profile": "profile-a-monolithic.yaml",
            "targets": {
                f"{domain}:{entity_id}": target
                for (domain, entity_id), target in sorted(targets_a.items())
            },
        },
        "layout_b": {
            "profile": "profile-b-split.yaml",
            "targets": {
                f"{domain}:{entity_id}": target
                for (domain, entity_id), target in sorted(targets_b.items())
            },
        },
        "assertions": {
            "same_mission_identity": True,
            "same_core_input_set": True,
            "same_orbitfabric_source_identity_set": True,
            "fprime_placement_changed": True,
            "packet_membership_followed_telemetry_placement": True,
            "coverage_explicit": True,
        },
    }
    proof_path.write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
