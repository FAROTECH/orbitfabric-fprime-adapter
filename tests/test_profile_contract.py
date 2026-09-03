from __future__ import annotations

import copy
import json
from importlib.resources import files

import pytest
from jsonschema import Draft202012Validator


def _schema() -> dict:
    return json.loads(
        files("orbitfabric_fprime_adapter")
        .joinpath("schemas/profile-0.1.schema.json")
        .read_text(encoding="utf-8")
    )


def _valid_profile() -> dict:
    return {
        "kind": "orbitfabric.projection_profile",
        "profile_version": "0.1-candidate",
        "profile": {"id": "contract-test", "version": "0.1.0"},
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
                    "host_instance": "payloadMonitor",
                    "symbol": "OF_Temperature",
                    "local_id": 16,
                    "update": "always",
                },
            },
            {
                "id": "cmd.start",
                "sources": [{"domain": "commands", "id": "payload.start_acquisition"}],
                "config": {
                    "kind": "command",
                    "host_component": "Payload.Controller",
                    "host_instance": "payloadController",
                    "symbol": "OF_StartAcquisition",
                    "local_opcode": 32,
                    "command_kind": "async",
                    "priority": 0,
                    "queue_full_behavior": "drop",
                },
            },
            {
                "id": "evt.started",
                "sources": [{"domain": "events", "id": "payload.acquisition_started"}],
                "config": {
                    "kind": "event",
                    "host_component": "Payload.Controller",
                    "host_instance": "payloadController",
                    "symbol": "OF_AcquisitionStarted",
                    "local_id": 48,
                    "severity": "activity_high",
                },
            },
            {
                "id": "packet.hk",
                "sources": [{"domain": "packets", "id": "housekeeping"}],
                "config": {
                    "kind": "packet",
                    "packet_set": "PayloadPackets",
                    "packet_name": "OF_Housekeeping",
                    "packet_id": 100,
                    "group": 1,
                },
            },
        ],
    }


def _validate(profile: dict) -> list:
    return list(Draft202012Validator(_schema()).iter_errors(profile))


def test_representative_profile_conforms() -> None:
    assert _validate(_valid_profile()) == []


def test_cross_domain_binding_is_rejected() -> None:
    profile = _valid_profile()
    profile["bindings"][0]["sources"][0]["domain"] = "commands"
    assert _validate(profile)


def test_multiple_sources_are_rejected() -> None:
    profile = _valid_profile()
    profile["bindings"][0]["sources"].append(
        {"domain": "telemetry", "id": "payload.second_temperature"}
    )
    assert _validate(profile)


def test_async_command_requires_queue_policy() -> None:
    profile = _valid_profile()
    del profile["bindings"][1]["config"]["priority"]
    assert _validate(profile)


def test_sync_command_rejects_async_queue_policy() -> None:
    profile = _valid_profile()
    config = profile["bindings"][1]["config"]
    config["command_kind"] = "sync"
    assert _validate(profile)


def test_unproven_target_version_is_rejected() -> None:
    profile = _valid_profile()
    profile["settings"]["target"]["fprime"]["version"] = "v4.3.0"
    assert _validate(profile)


@pytest.mark.parametrize("symbol", ["packet", "U32", "9invalid", "has-dash"])
def test_invalid_fpp_symbol_is_rejected(symbol: str) -> None:
    profile = copy.deepcopy(_valid_profile())
    profile["bindings"][0]["config"]["symbol"] = symbol
    assert _validate(profile)
