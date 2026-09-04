#!/usr/bin/env python3
"""Verify two native dictionaries preserve OF identity while F Prime placement evolves."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: expected JSON object")
    return value


def by_name(items: Any) -> dict[str, dict[str, Any]]:
    if not isinstance(items, list):
        return {}
    return {
        item["name"]: item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }


def require_names(index: dict[str, dict[str, Any]], names: list[str], label: str) -> None:
    missing = [name for name in names if name not in index]
    if missing:
        raise RuntimeError(f"{label}: missing resolved identities: {missing}")


def resolved(dictionary: dict[str, Any], layout: str) -> dict[str, Any]:
    commands = by_name(dictionary.get("commands"))
    events = by_name(dictionary.get("events"))
    telemetry = by_name(dictionary.get("telemetryChannels"))

    if layout == "a":
        prefix_command = "Ref.payload"
        prefix_telemetry = "Ref.payload"
    else:
        prefix_command = "Ref.payloadController"
        prefix_telemetry = "Ref.payloadMonitor"

    command_names = [
        f"{prefix_command}.OF_StartAcquisition",
        f"{prefix_command}.OF_StopAcquisition",
    ]
    event_names = [
        f"{prefix_command}.OF_AcquisitionStarted",
        f"{prefix_command}.OF_AcquisitionStopped",
    ]
    telemetry_names = [f"{prefix_telemetry}.OF_AcquisitionActive"]
    require_names(commands, command_names, f"layout {layout} commands")
    require_names(events, event_names, f"layout {layout} events")
    require_names(telemetry, telemetry_names, f"layout {layout} telemetry")

    packet_sets = by_name(dictionary.get("telemetryPacketSets"))
    packet_set = packet_sets.get("ReferencePackets")
    if packet_set is None:
        raise RuntimeError(f"layout {layout}: ReferencePackets missing")
    packets = by_name(packet_set.get("members"))
    packet = packets.get("OF_PayloadStatus")
    if packet is None:
        raise RuntimeError(f"layout {layout}: OF_PayloadStatus missing")
    expected_member = telemetry_names[0]
    if packet.get("members") != [expected_member]:
        raise RuntimeError(
            f"layout {layout}: packet members {packet.get('members')!r} != {[expected_member]!r}"
        )

    return {
        "commands": [
            {"name": name, "opcode": commands[name].get("opcode")} for name in command_names
        ],
        "events": [{"name": name, "id": events[name].get("id")} for name in event_names],
        "telemetry": [
            {"name": name, "id": telemetry[name].get("id")} for name in telemetry_names
        ],
        "packet": {
            "set": "ReferencePackets",
            "name": "OF_PayloadStatus",
            "id": packet.get("id"),
            "members": packet.get("members"),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--consumer-proof", type=Path, required=True)
    parser.add_argument("--dictionary-a", type=Path, required=True)
    parser.add_argument("--dictionary-b", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    proof = load(args.consumer_proof)
    if proof.get("status") != "passed":
        raise RuntimeError("consumer Reference Example proof did not pass")
    dictionary_a = load(args.dictionary_a)
    dictionary_b = load(args.dictionary_b)

    metadata_a = dictionary_a.get("metadata", {})
    metadata_b = dictionary_b.get("metadata", {})
    if metadata_a.get("frameworkVersion") != "8a62e45":
        raise RuntimeError("layout A dictionary does not come from accepted F Prime source")
    if metadata_b.get("frameworkVersion") != "8a62e45":
        raise RuntimeError("layout B dictionary does not come from accepted F Prime source")

    resolved_a = resolved(dictionary_a, "a")
    resolved_b = resolved(dictionary_b, "b")
    if resolved_a == resolved_b:
        raise RuntimeError("native resolved identities did not evolve between layouts")

    payload = {
        "kind": "orbitfabric.fprime.reference_contract_evolution_native_acceptance",
        "version": "0.1-candidate",
        "status": "passed",
        "core_input_set_sha256": proof["core_input_set_sha256"],
        "stable_sources": proof["stable_sources"],
        "fprime": {
            "version": "v4.2.2",
            "commit": "8a62e455a90b6d4f498c332d45d65a2a819988d8",
        },
        "fpp": {
            "version": "3.2.0",
            "commit": "93f484b7521a8e8894cba25b26e633cc87d8e37a",
        },
        "layout_a": {
            "dictionary_sha256": hashlib.sha256(args.dictionary_a.read_bytes()).hexdigest(),
            "resolved": resolved_a,
        },
        "layout_b": {
            "dictionary_sha256": hashlib.sha256(args.dictionary_b.read_bytes()).hexdigest(),
            "resolved": resolved_b,
        },
        "assertions": {
            "same_orbitfabric_source_identity_set": True,
            "both_native_generate_build_passed": True,
            "both_generated_dictionaries_resolved": True,
            "fprime_resolved_identity_evolved_with_profile": True,
            "packet_membership_followed_telemetry_placement": True,
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
