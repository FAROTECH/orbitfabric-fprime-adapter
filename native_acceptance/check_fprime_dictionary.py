#!/usr/bin/env python3
"""Validate a generated F Prime dictionary against native acceptance expectations."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a YAML mapping")
    return value


def index_by_name(items: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        item["name"]: item
        for item in items
        if isinstance(item, dict) and isinstance(item.get("name"), str)
    }


def require_equal(errors: list[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(f"{label}: expected {expected!r}, got {actual!r}")


def optional_equal(
    errors: list[str],
    label: str,
    actual: Any,
    spec: dict[str, Any],
    key: str,
) -> None:
    if key in spec:
        require_equal(errors, label, actual, spec[key])


def check_dictionary(
    dictionary_path: Path,
    expectations_path: Path,
) -> tuple[dict[str, Any], list[str]]:
    raw = dictionary_path.read_bytes()
    dictionary = json.loads(raw)
    expected = load_yaml(expectations_path)
    errors: list[str] = []
    resolutions: list[dict[str, Any]] = []

    metadata = dictionary.get("metadata", {})
    require_equal(
        errors,
        "metadata.frameworkVersion",
        metadata.get("frameworkVersion"),
        expected.get("fprime_version"),
    )
    if "deployment_name" in expected:
        require_equal(
            errors,
            "metadata.deploymentName",
            metadata.get("deploymentName"),
            expected["deployment_name"],
        )

    commands = index_by_name(dictionary.get("commands", []))
    events = index_by_name(dictionary.get("events", []))
    telemetry = index_by_name(dictionary.get("telemetryChannels", []))

    for spec in expected.get("entities", {}).get("commands", []):
        item = commands.get(spec["name"])
        if item is None:
            errors.append(f"command missing: {spec['name']}")
            continue
        require_equal(
            errors,
            f"command {spec['name']} kind",
            item.get("commandKind"),
            spec.get("command_kind"),
        )
        optional_equal(
            errors,
            f"command {spec['name']} opcode",
            item.get("opcode"),
            spec,
            "absolute_opcode",
        )
        resolutions.append(
            {
                "domain": "commands",
                "source_id": spec["source_id"],
                "target_name": spec["name"],
                "absolute_opcode": item.get("opcode"),
            }
        )

    for spec in expected.get("entities", {}).get("events", []):
        item = events.get(spec["name"])
        if item is None:
            errors.append(f"event missing: {spec['name']}")
            continue
        require_equal(
            errors,
            f"event {spec['name']} severity",
            item.get("severity"),
            spec.get("severity"),
        )
        optional_equal(
            errors,
            f"event {spec['name']} id",
            item.get("id"),
            spec,
            "absolute_id",
        )
        resolutions.append(
            {
                "domain": "events",
                "source_id": spec["source_id"],
                "target_name": spec["name"],
                "absolute_id": item.get("id"),
            }
        )

    for spec in expected.get("entities", {}).get("telemetry", []):
        item = telemetry.get(spec["name"])
        if item is None:
            errors.append(f"telemetry missing: {spec['name']}")
            continue
        require_equal(
            errors,
            f"telemetry {spec['name']} type",
            (item.get("type") or {}).get("name"),
            spec.get("type"),
        )
        require_equal(
            errors,
            f"telemetry {spec['name']} update",
            item.get("telemetryUpdate"),
            spec.get("update"),
        )
        optional_equal(
            errors,
            f"telemetry {spec['name']} id",
            item.get("id"),
            spec,
            "absolute_id",
        )
        resolutions.append(
            {
                "domain": "telemetry",
                "source_id": spec["source_id"],
                "target_name": spec["name"],
                "absolute_id": item.get("id"),
            }
        )

    packet_sets = index_by_name(dictionary.get("telemetryPacketSets", []))
    for spec in expected.get("packets", []):
        packet_set = packet_sets.get(spec["packet_set"])
        if packet_set is None:
            errors.append(f"packet set missing: {spec['packet_set']}")
            continue
        packets = index_by_name(packet_set.get("members", []))
        packet = packets.get(spec["name"])
        if packet is None:
            errors.append(f"packet missing: {spec['packet_set']}.{spec['name']}")
            continue
        require_equal(errors, f"packet {spec['name']} id", packet.get("id"), spec.get("id"))
        require_equal(
            errors,
            f"packet {spec['name']} group",
            packet.get("group"),
            spec.get("group"),
        )
        require_equal(
            errors,
            f"packet {spec['name']} members",
            packet.get("members"),
            spec.get("members"),
        )
        resolutions.append(
            {
                "domain": "packets",
                "source_id": spec["source_id"],
                "target_name": f"{spec['packet_set']}.{spec['name']}",
                "packet_id": packet.get("id"),
                "group": packet.get("group"),
                "members": packet.get("members"),
            }
        )

    evidence = {
        "kind": "orbitfabric.fprime.dictionary_conformance",
        "version": "0.1-candidate",
        "status": "passed" if not errors else "failed",
        "dictionary": {
            "path": str(dictionary_path),
            "sha256": hashlib.sha256(raw).hexdigest(),
            "deployment_name": metadata.get("deploymentName"),
            "framework_version": metadata.get("frameworkVersion"),
            "dictionary_spec_version": metadata.get("dictionarySpecVersion"),
        },
        "resolutions": resolutions,
        "errors": errors,
    }
    return evidence, errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dictionary", type=Path)
    parser.add_argument("expectations", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    evidence, errors = check_dictionary(args.dictionary, args.expectations)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(evidence, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print(json.dumps(evidence, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
