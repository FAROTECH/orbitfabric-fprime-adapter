from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from .constants import ADAPTER_ID, INTEGRATION_ID, OPERATION_ID, VERSION
from .input_set import LoadedInputSet
from .profile import sha256_file
from .projection import ProjectionResult

RESULT_VERSION = "0.2-candidate"
INTEGRATION_SCHEMA_VERSION = "0.1-candidate"
CAPABILITIES = [
    "profile_validation",
    "projection",
    "artifact_generation",
    "traceability",
]


def _mapping_id(binding_id: str) -> str:
    return f"mapping.{binding_id}"


def _target_reference(target: dict[str, Any]) -> dict[str, str]:
    if target["kind"] == "packet":
        target_id = f"{target['packet_set']}.{target['packet_name']}"
    else:
        target_id = f"{target['host_instance']}.{target['symbol']}"
    return {"namespace": "fprime", "kind": target["kind"], "id": target_id}


def _mappings(projection: ProjectionResult) -> list[dict[str, Any]]:
    return [
        {
            "id": _mapping_id(record["binding_id"]),
            "sources": [record["source"]],
            "profile_bindings": [record["binding_id"]],
            "targets": [_target_reference(record["target"])],
        }
        for record in projection.mappings
    ]


def _resolutions(
    profile: dict[str, Any], projection: ProjectionResult
) -> list[dict[str, Any]]:
    profile_bindings = {binding["id"]: binding for binding in profile["bindings"]}
    result: list[dict[str, Any]] = []

    for record in projection.mappings:
        binding_id = record["binding_id"]
        binding = profile_bindings[binding_id]
        config = binding["config"]
        source = record["source"]

        for property_name, value in config.items():
            if property_name == "kind":
                continue
            result.append(
                {
                    "id": f"resolution.{binding_id}.{property_name}",
                    "mapping": _mapping_id(binding_id),
                    "binding": binding_id,
                    "sources": [source],
                    "property": property_name,
                    "value": value,
                    "origin": "profile",
                }
            )

    return result


def _artifact_mapping_ids(projection: ProjectionResult) -> dict[str, list[str]]:
    by_kind: dict[str, list[str]] = defaultdict(list)
    for record in projection.mappings:
        by_kind[record["target"]["kind"]].append(_mapping_id(record["binding_id"]))
    return {
        "fpp_commands": by_kind["command"],
        "fpp_events": by_kind["event"],
        "fpp_telemetry": by_kind["telemetry"],
        "fpp_packet_specifiers": by_kind["packet"],
    }


def _artifacts(
    projection: ProjectionResult,
    artifact_metadata: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    mapping_ids = _artifact_mapping_ids(projection)
    role_counts: Counter[str] = Counter()
    result: list[dict[str, Any]] = []
    for item in artifact_metadata:
        role = item["role"]
        index = role_counts[role]
        role_counts[role] += 1
        result.append(
            {
                "id": f"fprime.{role}.{index}",
                "kind": f"fprime.{role}",
                "requirement": "required",
                "status": "generated",
                "path": item["path"],
                "media_type": "text/plain",
                "sha256": item["sha256"],
                "reason": None,
                "retained_partial": False,
                "derived_from_mappings": mapping_ids[role],
            }
        )
    return result


def _diagnostics(projection: ProjectionResult) -> list[dict[str, Any]]:
    binding_by_source = {
        (record["source"]["domain"], record["source"]["id"]): record["binding_id"]
        for record in projection.mappings
    }
    result: list[dict[str, Any]] = []
    for index, item in enumerate(projection.diagnostics, start=1):
        source = item["source"]
        binding_id = binding_by_source.get((source["domain"], source["id"]))
        result.append(
            {
                "id": f"diag-{index:03d}",
                "owner": "integration",
                "producer": INTEGRATION_ID,
                "phase": "projection",
                "severity": item["severity"].upper(),
                "code": item["code"],
                "message": (
                    f"Source field {item['field']} is not represented by the "
                    "current FPP contract projection."
                ),
                "sources": [source],
                "profile_bindings": [binding_id] if binding_id else [],
                "targets": [],
            }
        )
    return result


def _coverage(projection: ProjectionResult) -> dict[str, Any]:
    records = []
    for record in projection.mappings:
        fields = record["unrepresented_source_fields"]
        records.append(
            {
                "source": record["source"],
                "profile_binding": record["binding_id"],
                "target_kind": record["target"]["kind"],
                "semantic_disposition": "PARTIAL",
                "unrepresented_source_fields": fields,
            }
        )

    domains = sorted({record["source"]["domain"] for record in projection.mappings})
    return {
        "status": "complete",
        "scope": {"domains": domains},
        "reason": None,
        "summary": {
            "mapping_records": len(records),
            "partial_records": len(records),
            "unrepresented_field_instances": sum(
                len(record["unrepresented_source_fields"]) for record in records
            ),
        },
        "records": records,
    }


def successful_result(
    *,
    input_set: LoadedInputSet,
    profile: dict[str, Any],
    profile_path: Path,
    projection: ProjectionResult,
    artifact_metadata: list[dict[str, Any]],
) -> dict[str, Any]:
    mission = input_set.manifest["mission"]
    profile_digest = sha256_file(profile_path)
    return {
        "kind": "orbitfabric.integration_result",
        "result_version": RESULT_VERSION,
        "result": "succeeded",
        "integration": {
            "id": INTEGRATION_ID,
            "schema_version": INTEGRATION_SCHEMA_VERSION,
        },
        "adapter": {"id": ADAPTER_ID, "version": VERSION},
        "operation": {"id": OPERATION_ID},
        "mission": {
            "status": "available",
            "id": mission["id"],
            "model_version": mission["model_version"],
            "reason": None,
        },
        "inputs": {
            "core_input_set": {
                "status": "available",
                "kind": input_set.manifest["kind"],
                "version": input_set.manifest["input_set_version"],
                "sha256": input_set.manifest["input_set_sha256"],
                "reason": None,
            },
            "profile": {
                "status": "available",
                "kind": profile["kind"],
                "profile_version": profile["profile_version"],
                "id": profile["profile"]["id"],
                "version": profile["profile"]["version"],
                "sha256": profile_digest,
                "reason": None,
            },
            "operation_inputs": [],
        },
        "capabilities": list(CAPABILITIES),
        "artifacts": _artifacts(projection, artifact_metadata),
        "mappings": _mappings(projection),
        "resolutions": _resolutions(profile, projection),
        "diagnostics": _diagnostics(projection),
        "coverage": _coverage(projection),
        "evidence": [
            {
                "id": "core-input-integrity",
                "producer": INTEGRATION_ID,
                "kind": "core_input_set_integrity",
                "status": "passed",
                "sha256": input_set.manifest["input_set_sha256"],
            },
            {
                "id": "profile-validation",
                "producer": INTEGRATION_ID,
                "kind": "projection_profile_validation",
                "status": "passed",
                "sha256": profile_digest,
            },
        ],
        "external_tools": [],
    }


def failed_result(message: str) -> dict[str, Any]:
    unavailable_core = {
        "status": "unavailable",
        "kind": None,
        "version": None,
        "sha256": None,
        "reason": message,
    }
    unavailable_profile = {
        "status": "unavailable",
        "kind": None,
        "profile_version": None,
        "id": None,
        "version": None,
        "sha256": None,
        "reason": message,
    }
    return {
        "kind": "orbitfabric.integration_result",
        "result_version": RESULT_VERSION,
        "result": "failed",
        "integration": {"id": INTEGRATION_ID, "schema_version": None},
        "adapter": {"id": ADAPTER_ID, "version": VERSION},
        "operation": {"id": OPERATION_ID},
        "mission": {
            "status": "unavailable",
            "id": None,
            "model_version": None,
            "reason": message,
        },
        "inputs": {
            "core_input_set": unavailable_core,
            "profile": unavailable_profile,
            "operation_inputs": [],
        },
        "capabilities": [],
        "artifacts": [],
        "mappings": [],
        "resolutions": [],
        "diagnostics": [
            {
                "id": "diag-001",
                "owner": "integration",
                "producer": INTEGRATION_ID,
                "phase": "execution",
                "severity": "ERROR",
                "code": "OF_FPRIME_EXECUTION_FAILED",
                "message": message,
                "sources": [],
                "profile_bindings": [],
                "targets": [],
            }
        ],
        "coverage": {
            "status": "unavailable",
            "scope": {"domains": []},
            "reason": message,
            "summary": {},
            "records": [],
        },
        "evidence": [],
        "external_tools": [],
    }


def write_result(output_dir: Path, payload: dict[str, Any]) -> Path:
    path = output_dir / "integration_result.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path
