from __future__ import annotations

import hashlib
import json
from importlib.resources import files

from orbitfabric.conformance.integration_contracts import validate_manifest

EXPECTED_CAPABILITIES = [
    "profile_validation",
    "projection",
    "artifact_generation",
    "traceability",
]


def test_manifest_conforms_to_core_contract() -> None:
    package = files("orbitfabric_fprime_adapter")
    manifest_path = package.joinpath("integration_package.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    validate_manifest(manifest)

    assert manifest["adapter"] == {
        "id": "orbitfabric-fprime",
        "version": "0.1.1",
    }
    assert manifest["integration"]["id"] == "orbitfabric-fprime"
    assert manifest["capabilities"] == EXPECTED_CAPABILITIES
    assert manifest["core_input_compatibility"]["relationship_families"] == []
    assert {item["role"] for item in manifest["core_input_compatibility"]["surfaces"]} == {
        "entity_index",
        "lint_report",
        "mission_snapshot",
        "model_summary",
        "relationship_manifest",
    }
    assert manifest["operations"] == [
        {
            "capabilities": EXPECTED_CAPABILITIES,
            "id": "fpp_contract_projection",
            "input_requirements": [],
        }
    ]


def test_packaged_profile_schema_digest_matches_manifest() -> None:
    package = files("orbitfabric_fprime_adapter")
    manifest = json.loads(package.joinpath("integration_package.json").read_text(encoding="utf-8"))
    schema_entry = manifest["profile_schemas"][0]
    schema_bytes = package.joinpath(schema_entry["path"]).read_bytes()

    assert hashlib.sha256(schema_bytes).hexdigest() == schema_entry["sha256"]

    schema = json.loads(schema_bytes)
    assert schema["properties"]["integration"]["properties"]["id"]["const"] == (
        "orbitfabric-fprime"
    )
