#!/usr/bin/env python3
"""Verify provider-native FPP semantics for both Reference Example layouts.

This example-owned verifier consumes FPP 3.2 semantic output through the
version-matched fprime-python-model API. It does not parse FPP JSON directly,
infer F Prime architecture, or calculate provider global IDs.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
from pathlib import Path
from typing import Any

import yaml

from fprime_python_model.fpp_ast import fpp_ast
from fprime_python_model.model import FprimePythonModel
from fprime_python_model.semantics.symbol import ComponentSymbol


EXPECTED_FPP_VERSION = "v3.2.0"

FAMILIES = (
    {
        "family": "command",
        "source": ("commands", "payload.start_acquisition"),
        "binding": "payload-start",
        "local_key": "local_opcode",
        "source_file": "OF_Commands.fppi",
    },
    {
        "family": "command",
        "source": ("commands", "payload.stop_acquisition"),
        "binding": "payload-stop",
        "local_key": "local_opcode",
        "source_file": "OF_Commands.fppi",
    },
    {
        "family": "telemetry",
        "source": ("telemetry", "payload.acquisition.active"),
        "binding": "payload-active",
        "local_key": "local_id",
        "source_file": "OF_Telemetry.fppi",
    },
    {
        "family": "event",
        "source": ("events", "payload.acquisition_started"),
        "binding": "payload-started",
        "local_key": "local_id",
        "source_file": "OF_Events.fppi",
    },
    {
        "family": "event",
        "source": ("events", "payload.acquisition_stopped"),
        "binding": "payload-stopped",
        "local_key": "local_id",
        "source_file": "OF_Events.fppi",
    },
)

PACKET_SOURCE = ("packets", "payload_status")
PACKET_BINDING = "payload-status-packet"
PACKET_SOURCE_FILE = "OF_Packets.fppi"


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: expected JSON object")
    return value


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise RuntimeError(f"{path}: expected YAML object")
    return value


def mapping_targets(result: dict[str, Any]) -> dict[tuple[str, str], str]:
    targets: dict[tuple[str, str], str] = {}
    for mapping in result["mappings"]:
        source = mapping["sources"][0]
        target = mapping["targets"][0]
        key = (source["domain"], source["id"])
        if key in targets:
            raise RuntimeError(f"duplicate Integration Result source mapping: {key}")
        targets[key] = target["id"]
    return targets


def binding_map(profile: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {binding["id"]: binding for binding in profile["bindings"]}


def resolution(result: dict[str, Any], binding: str, property_name: str) -> Any:
    wanted = f"resolution.{binding}.{property_name}"
    matches = [record for record in result["resolutions"] if record["id"] == wanted]
    if len(matches) != 1:
        raise RuntimeError(f"{wanted}: expected exactly one resolution, got {len(matches)}")
    record = matches[0]
    if record["origin"] != "profile":
        raise RuntimeError(f"{wanted}: expected profile provenance, got {record['origin']!r}")
    return record["value"]


def location_path(location: Any) -> Path:
    path = getattr(location, "path", None)
    if path is None:
        raise RuntimeError(
            "unsupported fprime-python-model Location API for the supported FPP 3.2 example"
        )
    return Path(path)


def location_record(model: FprimePythonModel, node: Any) -> dict[str, Any]:
    loc = model.get_location(node)
    chain: list[dict[str, str]] = []
    current = loc
    while current is not None:
        chain.append({"path": str(location_path(current)), "pos": current.pos})
        current = current.including_loc
    return {
        "path": str(location_path(loc)),
        "pos": loc.pos,
        "include_chain": chain,
    }


def component_qualified_name(model: FprimePythonModel, component: Any) -> str:
    symbol = ComponentSymbol(component.a_node)
    return str(model.analysis.get_qualified_name_from_map(symbol))


def find_component(model: FprimePythonModel, qualified_name: str) -> Any:
    matches = [
        component
        for component in model.analysis.component_map.values()
        if component_qualified_name(model, component) == qualified_name
    ]
    if len(matches) != 1:
        raise RuntimeError(
            f"component {qualified_name!r}: expected one semantic match, got {len(matches)}"
        )
    return matches[0]


def find_host_instance(model: FprimePythonModel, component: Any, host_instance: str) -> Any:
    matches = []
    for instance in model.analysis.component_instance_map.values():
        if instance.component != component:
            continue
        qname = str(instance.qualified_name)
        if qname == host_instance or qname.endswith("." + host_instance):
            matches.append(instance)
    if len(matches) != 1:
        raise RuntimeError(
            f"host instance {host_instance!r}: expected one instance of "
            f"{component_qualified_name(model, component)}, got {len(matches)}"
        )
    return matches[0]


def semantic_entity(component: Any, family: str, local_key: int) -> Any:
    if family == "command":
        table = component.command_map
    elif family == "telemetry":
        table = component.tlm_channel_map
    elif family == "event":
        table = component.event_map
    else:
        raise RuntimeError(f"unsupported semantic family {family!r}")
    if local_key not in table:
        raise RuntimeError(f"{family}: local key {local_key} not present in provider semantic map")
    return table[local_key]


def expr_int(node: Any) -> int:
    if node is None:
        raise RuntimeError("expected integer expression, got None")
    data = node.data
    if not isinstance(data, fpp_ast.ExprLiteralInt):
        raise RuntimeError(f"expected literal integer expression, got {type(data).__name__}")
    return int(data.value, 0)


def qual_ident_text(value: Any) -> str:
    if isinstance(value, fpp_ast.Unqualified):
        return str(value.name)
    if isinstance(value, fpp_ast.Qualified):
        return f"{qual_ident_text(value.qualifier.data)}.{value.name.data}"
    raise RuntimeError(f"unsupported qualified identifier: {type(value).__name__}")


def packet_members(packet_node: Any) -> list[str]:
    members: list[str] = []
    for member in packet_node.data.members:
        if not isinstance(member, fpp_ast.TlmPacketMemberTlmChannelIdentifier):
            raise RuntimeError(
                f"packet contains unsupported member type {type(member).__name__}; "
                "flattened membership is not proven"
            )
        identifier = member.node.data
        members.append(
            f"{qual_ident_text(identifier.component_instance.data)}."
            f"{identifier.channel_name.data}"
        )
    return members


def find_packet(
    model: FprimePythonModel,
    packet_name: str,
    packet_id: int,
    group: int,
) -> Any:
    matches = []
    for annotated_node in model.annotated_ast_id_map.values():
        node = annotated_node[1]
        if not isinstance(node.data, fpp_ast.SpecTlmPacket):
            continue
        if str(node.data.name) != packet_name:
            continue
        if node.data.id is None or expr_int(node.data.id) != packet_id:
            continue
        if expr_int(node.data.group) != group:
            continue
        if location_path(model.get_location(node)).name != PACKET_SOURCE_FILE:
            continue
        matches.append(node)
    if len(matches) != 1:
        raise RuntimeError(
            f"packet {packet_name!r}/{packet_id}: expected one semantic+provenance match, "
            f"got {len(matches)}"
        )
    return matches[0]


def validate_provider_version(ast: Path, locations: Path, analysis: Path) -> None:
    versions = {
        "ast": load_json(ast).get("fppVersion"),
        "locations": load_json(locations).get("fppVersion"),
        "analysis": load_json(analysis).get("fppVersion"),
    }
    if set(versions.values()) != {EXPECTED_FPP_VERSION}:
        raise RuntimeError(
            f"expected exact FPP 3.2 semantic output {EXPECTED_FPP_VERSION!r}, got {versions!r}"
        )


def reconcile_layout(
    *,
    name: str,
    ast: Path,
    locations: Path,
    analysis: Path,
    profile_path: Path,
    result_path: Path,
    input_set_manifest: Path,
) -> dict[str, Any]:
    validate_provider_version(ast, locations, analysis)

    profile = load_yaml(profile_path)
    result = load_json(result_path)
    manifest = load_json(input_set_manifest)

    if result.get("result") != "succeeded":
        raise RuntimeError(f"layout {name}: Integration Result did not succeed")

    declared_digest = result.get("inputs", {}).get("core_input_set", {}).get("sha256")
    manifest_digest = manifest.get("input_set_sha256")
    if declared_digest != manifest_digest:
        raise RuntimeError(
            f"layout {name}: Core input-set correlation mismatch "
            f"{declared_digest!r} != {manifest_digest!r}"
        )

    bindings = binding_map(profile)
    targets = mapping_targets(result)
    model = FprimePythonModel(str(ast), str(locations), str(analysis))
    records: list[dict[str, Any]] = []

    for spec in FAMILIES:
        family = spec["family"]
        source = spec["source"]
        binding = bindings[spec["binding"]]
        config = binding["config"]

        expected_symbol = str(config["symbol"])
        expected_target = f"{config['host_instance']}.{expected_symbol}"
        actual_target = targets[source]
        if actual_target != expected_target:
            raise RuntimeError(
                f"layout {name} {family} {source}: Integration Result target "
                f"{actual_target!r} != Profile target {expected_target!r}"
            )

        host_component = str(config["host_component"])
        if resolution(result, spec["binding"], "host_component") != host_component:
            raise RuntimeError(
                f"layout {name} {family} {source}: host-component resolution mismatch"
            )

        component = find_component(model, host_component)
        instance = find_host_instance(model, component, str(config["host_instance"]))
        local_key = int(config[spec["local_key"]])
        entity = semantic_entity(component, family, local_key)

        if str(entity.get_name()) != expected_symbol:
            raise RuntimeError(
                f"layout {name} {family} {source}: local key {local_key} resolved to "
                f"{entity.get_name()!r}, expected {expected_symbol!r}"
            )

        node = entity.get_node()
        location = location_record(model, node)
        if Path(location["path"]).name != spec["source_file"]:
            raise RuntimeError(
                f"layout {name} {family} {source}: provider provenance is "
                f"{location['path']!r}, expected {spec['source_file']!r}"
            )

        records.append(
            {
                "family": family,
                "source": {"domain": source[0], "id": source[1]},
                "intent": {
                    "host_component": host_component,
                    "host_instance": str(config["host_instance"]),
                    "symbol": expected_symbol,
                    "local_key": local_key,
                },
                "integration_target": actual_target,
                "observed": {
                    "component": component_qualified_name(model, component),
                    "instance": str(instance.qualified_name),
                    "symbol": str(entity.get_name()),
                    "local_key": local_key,
                    "ast_node_id": node.get_id(),
                    "location": location,
                },
                "status": "reconciled",
            }
        )

    packet_binding = bindings[PACKET_BINDING]
    packet_config = packet_binding["config"]
    expected_packet_target = f"{packet_config['packet_set']}.{packet_config['packet_name']}"
    if targets[PACKET_SOURCE] != expected_packet_target:
        raise RuntimeError(
            f"layout {name} packet: Integration Result target does not match Profile target"
        )

    packet_node = find_packet(
        model,
        str(packet_config["packet_name"]),
        int(packet_config["packet_id"]),
        int(packet_config["group"]),
    )
    members = packet_members(packet_node)

    telemetry_record = next(
        record
        for record in records
        if record["source"]
        == {"domain": "telemetry", "id": "payload.acquisition.active"}
    )
    if members != [telemetry_record["integration_target"]]:
        raise RuntimeError(
            f"layout {name} packet members {members!r} do not match projected telemetry "
            f"{[telemetry_record['integration_target']]!r}"
        )

    records.append(
        {
            "family": "packet",
            "source": {"domain": PACKET_SOURCE[0], "id": PACKET_SOURCE[1]},
            "intent": {
                "packet_set": str(packet_config["packet_set"]),
                "packet_name": str(packet_config["packet_name"]),
                "packet_id": int(packet_config["packet_id"]),
                "group": int(packet_config["group"]),
            },
            "integration_target": targets[PACKET_SOURCE],
            "observed": {
                "packet_name": str(packet_node.data.name),
                "packet_id": expr_int(packet_node.data.id),
                "group": expr_int(packet_node.data.group),
                "members": members,
                "ast_node_id": packet_node.get_id(),
                "location": location_record(model, packet_node),
            },
            "status": "reconciled",
        }
    )

    return {
        "profile": profile["profile"]["id"],
        "mission": result["mission"],
        "core_input_set_sha256": declared_digest,
        "records": records,
    }


def index_records(layout: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    return {
        (record["source"]["domain"], record["source"]["id"]): record
        for record in layout["records"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--layout-a-ast", type=Path, required=True)
    parser.add_argument("--layout-a-locations", type=Path, required=True)
    parser.add_argument("--layout-a-analysis", type=Path, required=True)
    parser.add_argument("--layout-b-ast", type=Path, required=True)
    parser.add_argument("--layout-b-locations", type=Path, required=True)
    parser.add_argument("--layout-b-analysis", type=Path, required=True)
    parser.add_argument("--profile-a", type=Path, required=True)
    parser.add_argument("--profile-b", type=Path, required=True)
    parser.add_argument("--result-a", type=Path, required=True)
    parser.add_argument("--result-b", type=Path, required=True)
    parser.add_argument("--input-set-manifest", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    layout_a = reconcile_layout(
        name="A",
        ast=args.layout_a_ast,
        locations=args.layout_a_locations,
        analysis=args.layout_a_analysis,
        profile_path=args.profile_a,
        result_path=args.result_a,
        input_set_manifest=args.input_set_manifest,
    )
    layout_b = reconcile_layout(
        name="B",
        ast=args.layout_b_ast,
        locations=args.layout_b_locations,
        analysis=args.layout_b_analysis,
        profile_path=args.profile_b,
        result_path=args.result_b,
        input_set_manifest=args.input_set_manifest,
    )

    if layout_a["mission"] != layout_b["mission"]:
        raise RuntimeError("mission identity changed between semantic-reconciliation layouts")
    if layout_a["core_input_set_sha256"] != layout_b["core_input_set_sha256"]:
        raise RuntimeError("Core Integration Input Set changed between layouts")

    records_a = index_records(layout_a)
    records_b = index_records(layout_b)
    if set(records_a) != set(records_b):
        raise RuntimeError("OrbitFabric source identity set changed between layouts")

    for source, record_a in records_a.items():
        record_b = records_b[source]
        if record_a["status"] != "reconciled" or record_b["status"] != "reconciled":
            raise RuntimeError(f"{source}: both layouts must reconcile")

    placement_sources = {
        ("commands", "payload.start_acquisition"),
        ("commands", "payload.stop_acquisition"),
        ("events", "payload.acquisition_started"),
        ("events", "payload.acquisition_stopped"),
        ("telemetry", "payload.acquisition.active"),
    }
    for source in placement_sources:
        a = records_a[source]["observed"]
        b = records_b[source]["observed"]
        if (a["component"], a["instance"]) == (b["component"], b["instance"]):
            raise RuntimeError(f"{source}: provider-native placement did not evolve")

    if (
        records_a[PACKET_SOURCE]["observed"]["members"]
        == records_b[PACKET_SOURCE]["observed"]["members"]
    ):
        raise RuntimeError("packet membership did not follow telemetry placement")

    proof = {
        "kind": "orbitfabric.fprime.example.semantic_reconciliation",
        "version": "0.1-example",
        "status": "passed",
        "provider": {
            "fpp_version": "3.2.0",
            "semantic_consumer": {
                "name": "fprime-python-model",
                "version": importlib.metadata.version("fprime-python-model"),
            },
        },
        "mission": layout_a["mission"],
        "core_input_set_sha256": layout_a["core_input_set_sha256"],
        "stable_sources": [
            {"domain": domain, "id": entity_id}
            for domain, entity_id in sorted(records_a)
        ],
        "layout_a": layout_a,
        "layout_b": layout_b,
        "assertions": {
            "same_mission_identity": True,
            "same_core_input_set": True,
            "same_orbitfabric_source_identity_set": True,
            "both_layouts_reconciled": True,
            "provider_native_placement_followed_profile": True,
            "generated_source_provenance_verified": True,
            "packet_membership_followed_telemetry_placement": True,
            "no_fuzzy_matching": True,
            "no_architecture_inference": True,
            "provider_global_identity_closure": False,
        },
        "limitations": [
            "FPP 3.2 does not expose dictionaryMap. Final provider-resolved global identity "
            "closure is outside this example proof and remains covered by downstream "
            "dictionary evidence."
        ],
        "note": (
            "This is an example-owned evidence artifact, not a stable adapter API or Core contract."
        ),
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(proof, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(proof, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
