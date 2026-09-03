from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from pathlib import Path

import yaml
from orbitfabric.conformance.integration_contracts import validate_result

from orbitfabric_fprime_adapter.execution import ExecutionError, execute_projection
from orbitfabric_fprime_adapter.input_set import (
    InputSetError,
    compute_input_set_sha256,
    load_input_set,
)


def _write_json(path: Path, value: dict) -> str:
    raw = json.dumps(value, indent=2, sort_keys=True).encode("utf-8") + b"\n"
    path.write_bytes(raw)
    return hashlib.sha256(raw).hexdigest()


def _input_set(root: Path) -> Path:
    root.mkdir()
    surfaces = {
        "entity_index": {
            "kind": "orbitfabric.entity_index",
            "index_version": "0.1",
            "entities": [
                {"domain": "telemetry", "id": "payload.temperature"},
                {"domain": "commands", "id": "payload.set_mode"},
                {"domain": "events", "id": "payload.mode_changed"},
                {"domain": "packets", "id": "housekeeping.fast"},
            ],
        },
        "lint_report": {
            "tool": "orbitfabric-lint",
            "version": "1.2.0",
            "mission": "fprime-contract-test",
            "model_version": "0.1.0",
            "result": "passed",
            "loaded": {},
            "summary": {"errors": 0, "warnings": 0, "info": 0},
            "findings": [],
        },
        "mission_snapshot": {
            "kind": "orbitfabric.mission_snapshot",
            "snapshot_version": "0.1-candidate",
            "result": "loaded",
            "model": {
                "telemetry": [
                    {
                        "id": "payload.temperature",
                        "type": "float32",
                        "unit": "degC",
                    }
                ],
                "commands": [
                    {
                        "id": "payload.set_mode",
                        "arguments": [{"name": "mode", "type": "uint8"}],
                        "requires_ack": True,
                    }
                ],
                "events": [
                    {
                        "id": "payload.mode_changed",
                        "description": "Payload mode changed",
                    }
                ],
                "packets": [
                    {
                        "id": "housekeeping.fast",
                        "telemetry": ["payload.temperature"],
                    }
                ],
            },
        },
        "model_summary": {
            "kind": "orbitfabric.model_summary",
            "summary_version": "0.1",
        },
        "relationship_manifest": {
            "kind": "orbitfabric.relationship_manifest",
            "manifest_version": "0.1-candidate",
            "relationships": [],
        },
    }
    contracts = {
        "entity_index": ("required", "orbitfabric.entity_index", "0.1"),
        "lint_report": ("required", "orbitfabric-lint", "v1"),
        "mission_snapshot": (
            "required",
            "orbitfabric.mission_snapshot",
            "0.1-candidate",
        ),
        "model_summary": ("companion", "orbitfabric.model_summary", "0.1"),
        "relationship_manifest": (
            "required",
            "orbitfabric.relationship_manifest",
            "0.1-candidate",
        ),
    }

    records = []
    for role, value in surfaces.items():
        filename = f"{role}.json"
        digest = _write_json(root / filename, value)
        requirement, kind, version = contracts[role]
        records.append(
            {
                "role": role,
                "requirement": requirement,
                "status": "available",
                "kind": kind,
                "format_version": version,
                "path": filename,
                "sha256": digest,
                "unavailable_reason": None,
            }
        )

    manifest = {
        "kind": "orbitfabric.integration_input_set",
        "input_set_version": "0.1-candidate",
        "orbitfabric_version": "1.2.0",
        "mission": {"id": "fprime-contract-test", "model_version": "0.1.0"},
        "load_result": "loaded",
        "lint_result": "passed",
        "surfaces": sorted(records, key=lambda item: item["role"]),
    }
    manifest["input_set_sha256"] = compute_input_set_sha256(manifest)
    path = root / "integration_input_manifest.json"
    _write_json(path, manifest)
    return path


def _profile(path: Path) -> Path:
    value = {
        "kind": "orbitfabric.projection_profile",
        "profile_version": "0.1-candidate",
        "profile": {"id": "fprime-contract-test", "version": "0.1.0"},
        "integration": {"id": "orbitfabric-fprime", "schema_version": "0.1-candidate"},
        "settings": {
            "target": {
                "fprime": {
                    "version": "v4.2.2",
                    "commit": "8a62e455a90b6d4f498c332d45d65a2a819988d8",
                },
                "fpp": {
                    "version": "3.2.0",
                    "commit": "93f484b7521a8e8894cba25b26e633cc87d8e37a",
                },
            },
            "telemetry_limits": {"critical": "red", "warning": "yellow"},
        },
        "bindings": [
            {
                "id": "tm.temperature",
                "sources": [{"domain": "telemetry", "id": "payload.temperature"}],
                "config": {
                    "kind": "telemetry",
                    "host_component": "Payload.Monitor",
                    "host_instance": "Ref.payloadMonitor",
                    "symbol": "OF_Temperature",
                    "local_id": 16,
                    "update": "always",
                },
            },
            {
                "id": "cmd.set_mode",
                "sources": [{"domain": "commands", "id": "payload.set_mode"}],
                "config": {
                    "kind": "command",
                    "host_component": "Payload.Controller",
                    "host_instance": "Ref.payloadController",
                    "symbol": "OF_SetMode",
                    "local_opcode": 32,
                    "command_kind": "async",
                    "priority": 0,
                    "queue_full_behavior": "drop",
                },
            },
            {
                "id": "evt.mode_changed",
                "sources": [{"domain": "events", "id": "payload.mode_changed"}],
                "config": {
                    "kind": "event",
                    "host_component": "Payload.Controller",
                    "host_instance": "Ref.payloadController",
                    "symbol": "OF_ModeChanged",
                    "local_id": 48,
                    "severity": "activity_high",
                },
            },
            {
                "id": "packet.hk",
                "sources": [{"domain": "packets", "id": "housekeeping.fast"}],
                "config": {
                    "kind": "packet",
                    "packet_set": "PayloadPackets",
                    "packet_name": "OF_HousekeepingFast",
                    "packet_id": 100,
                    "group": 1,
                },
            },
        ],
    }
    path.write_text(yaml.safe_dump(value, sort_keys=False), encoding="utf-8")
    return path


def test_canonical_execution_produces_core_conformant_result(tmp_path: Path) -> None:
    manifest_path = _input_set(tmp_path / "input")
    profile_path = _profile(tmp_path / "profile.yaml")
    output_dir = tmp_path / "output"

    projection, result = execute_projection(
        manifest_path=manifest_path,
        profile_path=profile_path,
        output_dir=output_dir,
    )

    package_manifest = json.loads(
        files("orbitfabric_fprime_adapter")
        .joinpath("integration_package.json")
        .read_text(encoding="utf-8")
    )
    validate_result(package_manifest, result)

    assert result["result"] == "succeeded"
    assert result["capabilities"] == [
        "profile_validation",
        "projection",
        "artifact_generation",
        "traceability",
    ]
    assert result["inputs"]["operation_inputs"] == []
    assert result["coverage"]["status"] == "complete"
    assert len(result["mappings"]) == 4
    assert len(result["artifacts"]) == 4
    assert projection.artifacts
    assert (output_dir / "integration_result.json").is_file()

    resolutions = result["resolutions"]
    assert resolutions
    assert {item["origin"] for item in resolutions} == {"profile"}
    assert {
        (item["binding"], item["property"], item["value"])
        for item in resolutions
        if item["property"] in {"local_id", "local_opcode", "packet_id"}
    } == {
        ("tm.temperature", "local_id", 16),
        ("cmd.set_mode", "local_opcode", 32),
        ("evt.mode_changed", "local_id", 48),
        ("packet.hk", "packet_id", 100),
    }
    assert all("resolved_id" not in item["property"] for item in resolutions)


def test_tampered_surface_is_rejected(tmp_path: Path) -> None:
    manifest_path = _input_set(tmp_path / "input")
    surface = manifest_path.parent / "mission_snapshot.json"
    surface.write_text(surface.read_text(encoding="utf-8") + " ", encoding="utf-8")

    try:
        load_input_set(manifest_path)
    except InputSetError as exc:
        assert "SHA-256 mismatch" in str(exc)
    else:
        raise AssertionError("tampered Core surface was accepted")


def test_lint_report_tool_must_match_core_contract(tmp_path: Path) -> None:
    manifest_path = _input_set(tmp_path / "input")
    lint_path = manifest_path.parent / "lint_report.json"
    lint = json.loads(lint_path.read_text(encoding="utf-8"))
    lint["tool"] = "other-linter"
    digest = _write_json(lint_path, lint)

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    for surface in manifest["surfaces"]:
        if surface["role"] == "lint_report":
            surface["sha256"] = digest
    manifest["input_set_sha256"] = compute_input_set_sha256(manifest)
    _write_json(manifest_path, manifest)

    try:
        load_input_set(manifest_path)
    except InputSetError as exc:
        assert "lint report tool mismatch" in str(exc)
    else:
        raise AssertionError("unexpected lint report producer was accepted")


def test_profile_source_must_resolve_in_entity_index(tmp_path: Path) -> None:
    manifest_path = _input_set(tmp_path / "input")
    profile_path = _profile(tmp_path / "profile.yaml")
    profile = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    profile["bindings"][0]["sources"][0]["id"] = "payload.not_indexed"
    profile_path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding="utf-8")

    try:
        execute_projection(
            manifest_path=manifest_path,
            profile_path=profile_path,
            output_dir=tmp_path / "output",
        )
    except ExecutionError as exc:
        assert "Core entity_index" in str(exc)
    else:
        raise AssertionError("unindexed Profile source was accepted")
