from __future__ import annotations

from pathlib import Path

import pytest

from orbitfabric_fprime_adapter.projection import (
    ProjectionError,
    build_projection,
    write_projection,
)


def _model() -> dict:
    return {
        "telemetry": [
            {
                "id": "payload.temperature",
                "type": "float32",
                "unit": "degC",
                "limits": {
                    "warning_low": -5.0,
                    "critical_low": -10.0,
                    "warning_high": 65.0,
                    "critical_high": 75.0,
                },
            }
        ],
        "commands": [
            {
                "id": "payload.set_mode",
                "arguments": [
                    {
                        "name": "mode",
                        "type": "uint8",
                        "description": "Requested payload mode",
                    }
                ],
                "requires_ack": True,
            }
        ],
        "events": [
            {
                "id": "payload.mode_changed",
                "description": "Payload mode changed",
                "downlink_priority": "high",
            }
        ],
        "packets": [
            {
                "id": "housekeeping.fast",
                "telemetry": ["payload.temperature"],
                "period": "1s",
            }
        ],
    }


def _profile() -> dict:
    return {
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


def _artifact(result, role: str) -> str:
    return next(artifact.content for artifact in result.artifacts if artifact.role == role)


def test_projects_proven_fpp_surface() -> None:
    result = build_projection(_model(), _profile())

    telemetry = _artifact(result, "fpp_telemetry")
    assert "telemetry OF_Temperature: F32" in telemetry
    assert "low { yellow -5.0, red -10.0 }" in telemetry
    assert "high { yellow 65.0, red 75.0 }" in telemetry

    command = _artifact(result, "fpp_commands")
    assert "async command OF_SetMode" in command
    assert "mode: U8" in command
    assert "opcode 32 priority 0 drop" in command

    event = _artifact(result, "fpp_events")
    assert "event OF_ModeChanged" in event
    assert "severity activity high" in event
    assert "id 48" in event

    packet = _artifact(result, "fpp_packet_specifiers")
    assert "packet OF_HousekeepingFast id 100 group 1" in packet
    assert "Ref.payloadMonitor.OF_Temperature" in packet


def test_packet_identity_uses_profile_authored_instance_qualification() -> None:
    profile = _profile()
    profile["bindings"][0]["config"]["host_instance"] = "Mission.Payload.payloadMonitor"

    result = build_projection(_model(), profile)

    packet = _artifact(result, "fpp_packet_specifiers")
    assert "Mission.Payload.payloadMonitor.OF_Temperature" in packet


def test_only_present_unrepresented_fields_emit_diagnostics() -> None:
    result = build_projection(_model(), _profile())
    observed = {
        (diagnostic["source"]["domain"], diagnostic["source"]["id"], diagnostic["field"])
        for diagnostic in result.diagnostics
    }

    assert ("telemetry", "payload.temperature", "unit") in observed
    assert ("commands", "payload.set_mode", "requires_ack") in observed
    assert ("events", "payload.mode_changed", "downlink_priority") in observed
    assert ("packets", "housekeeping.fast", "period") in observed
    assert ("telemetry", "payload.temperature", "sampling") not in observed


def test_unsupported_source_type_fails() -> None:
    model = _model()
    model["telemetry"][0]["type"] = "string"

    with pytest.raises(ProjectionError, match="unsupported OrbitFabric type"):
        build_projection(model, _profile())


def test_duplicate_component_allocation_fails() -> None:
    profile = _profile()
    duplicate = {
        "id": "tm.second",
        "sources": [{"domain": "telemetry", "id": "payload.second"}],
        "config": {
            "kind": "telemetry",
            "host_component": "Payload.Monitor",
            "host_instance": "Ref.payloadMonitor",
            "symbol": "OF_Second",
            "local_id": 16,
            "update": "always",
        },
    }
    profile["bindings"].append(duplicate)
    model = _model()
    model["telemetry"].append({"id": "payload.second", "type": "uint16"})

    with pytest.raises(ProjectionError, match="duplicate generated telemetry allocation"):
        build_projection(model, profile)


def test_packet_requires_projected_telemetry_members() -> None:
    model = _model()
    model["packets"][0]["telemetry"].append("payload.unprojected")

    with pytest.raises(ProjectionError, match="have no projected F Prime target"):
        build_projection(model, _profile())


def test_build_is_pure_and_write_is_explicit(tmp_path: Path) -> None:
    result = build_projection(_model(), _profile())
    assert list(tmp_path.iterdir()) == []

    metadata = write_projection(result, tmp_path)

    assert (tmp_path / "components/Payload_Monitor/OF_Telemetry.fppi").is_file()
    assert (tmp_path / "topology/PayloadPackets/OF_Packets.fppi").is_file()
    assert all(record["sha256"] for record in metadata)
