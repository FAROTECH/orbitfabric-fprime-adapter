from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any

TYPE_MAP = {
    "bool": "bool",
    "uint8": "U8",
    "uint16": "U16",
    "uint32": "U32",
    "int8": "I8",
    "int16": "I16",
    "int32": "I32",
    "float32": "F32",
    "float64": "F64",
}

EVENT_SEVERITY_FPP = {
    "activity_high": "activity high",
    "activity_low": "activity low",
    "command": "command",
    "diagnostic": "diagnostic",
    "fatal": "fatal",
    "warning_high": "warning high",
    "warning_low": "warning low",
}

UNREPRESENTED_FIELDS = {
    "telemetry": (
        "unit",
        "sampling",
        "criticality",
        "persistence",
        "downlink_priority",
        "quality",
    ),
    "commands": (
        "allowed_modes",
        "preconditions",
        "requires_ack",
        "timeout_ms",
        "risk",
        "emits",
        "expected_effects",
    ),
    "events": ("downlink_priority", "persistence"),
    "packets": ("type", "max_payload_bytes", "period"),
}


class ProjectionError(ValueError):
    """Raised when a Profile cannot be projected without ambiguity."""


@dataclass(frozen=True)
class Artifact:
    role: str
    path: str
    content: str
    host_component: str | None = None

    @property
    def sha256(self) -> str:
        return sha256(self.content.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ProjectionResult:
    artifacts: tuple[Artifact, ...]
    mappings: tuple[dict[str, Any], ...]
    diagnostics: tuple[dict[str, Any], ...]


def _entity_map(model: dict[str, Any], domain: str) -> dict[str, dict[str, Any]]:
    items = model.get(domain)
    if not isinstance(items, list):
        raise ProjectionError(f"model.{domain} must be an array")

    result: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            raise ProjectionError(f"model.{domain} entries must have string ids")
        entity_id = item["id"]
        if entity_id in result:
            raise ProjectionError(f"duplicate source entity in {domain}: {entity_id}")
        result[entity_id] = item
    return result


def _source(binding: dict[str, Any]) -> tuple[str, str]:
    sources = binding.get("sources")
    if not isinstance(sources, list) or len(sources) != 1:
        raise ProjectionError(f"binding {binding.get('id')}: exactly one source is required")

    source = sources[0]
    if not isinstance(source, dict):
        raise ProjectionError(f"binding {binding.get('id')}: source must be an object")

    domain = source.get("domain")
    entity_id = source.get("id")
    if not isinstance(domain, str) or not isinstance(entity_id, str):
        raise ProjectionError(
            f"binding {binding.get('id')}: source domain and id must be strings"
        )
    return domain, entity_id


def _fpp_type(source_type: Any) -> str:
    if not isinstance(source_type, str):
        raise ProjectionError(f"OrbitFabric type must be a string, got {source_type!r}")
    try:
        return TYPE_MAP[source_type]
    except KeyError as exc:
        raise ProjectionError(f"unsupported OrbitFabric type: {source_type!r}") from exc


def _annotation(value: Any) -> str:
    return " ".join(str(value).replace("\r", " ").replace("\n", " ").split())


def _quote(value: Any) -> str:
    return str(value).replace("\\", "\\\\").replace('"', '\\"')


def _format_number(value: Any) -> str:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ProjectionError(f"FPP limit must be numeric, got {value!r}")
    return repr(value)


def _render_limits(item: dict[str, Any], settings: dict[str, Any]) -> list[str]:
    limits = item.get("limits")
    if limits is None:
        return []
    if not isinstance(limits, dict):
        raise ProjectionError(f"telemetry {item['id']}: limits must be an object")

    policy = settings.get("telemetry_limits")
    if not isinstance(policy, dict):
        raise ProjectionError("settings.telemetry_limits must be an object")

    rendered: list[str] = []
    for side in ("low", "high"):
        entries: list[tuple[str, Any]] = []
        seen_colors: set[str] = set()
        for level in ("warning", "critical"):
            value = limits.get(f"{level}_{side}")
            color = policy.get(level)
            if value is None or color == "unmapped":
                continue
            if color not in {"yellow", "orange", "red"}:
                raise ProjectionError(f"invalid FPP telemetry limit color: {color!r}")
            if color in seen_colors:
                raise ProjectionError(
                    f"telemetry {item['id']}: multiple {side} limits map to FPP {color}"
                )
            seen_colors.add(color)
            entries.append((color, value))

        if entries:
            body = ", ".join(
                f"{color} {_format_number(value)}" for color, value in entries
            )
            rendered.append(f"  {side} {{ {body} }}")
    return rendered


def _render_telemetry(
    item: dict[str, Any], config: dict[str, Any], settings: dict[str, Any]
) -> str:
    update = "on change" if config["update"] == "on_change" else "always"
    lines = [
        f"@ OrbitFabric telemetry: {item['id']}",
        f"telemetry {config['symbol']}: {_fpp_type(item.get('type'))} \\",
        f"  id {config['local_id']} \\",
    ]

    limit_lines = _render_limits(item, settings)
    if not limit_lines:
        lines.append(f"  update {update}")
        return "\n".join(lines)

    lines.append(f"  update {update} \\")
    for index, line in enumerate(limit_lines):
        suffix = " \\" if index < len(limit_lines) - 1 else ""
        lines.append(line + suffix)
    return "\n".join(lines)


def _render_command(item: dict[str, Any], config: dict[str, Any]) -> str:
    arguments = item.get("arguments", [])
    if not isinstance(arguments, list):
        raise ProjectionError(f"command {item['id']}: arguments must be an array")

    parameters: list[str] = []
    seen_names: set[str] = set()
    for argument in arguments:
        if not isinstance(argument, dict):
            raise ProjectionError(f"command {item['id']}: arguments must be objects")
        name = argument.get("name")
        if not isinstance(name, str) or not name:
            raise ProjectionError(f"command {item['id']}: argument name must be a string")
        if name in seen_names:
            raise ProjectionError(f"command {item['id']}: duplicate argument name {name}")
        seen_names.add(name)

        description = _annotation(
            argument.get("description") or f"OrbitFabric argument {name}"
        )
        fpp_type = _fpp_type(argument.get("type"))
        parameters.append(f"  {name}: {fpp_type} @< {description}")

    head = f"{config['command_kind']} command {config['symbol']}"
    if parameters:
        head += "(\n" + "\n".join(parameters) + "\n)"

    line = head + f" opcode {config['local_opcode']}"
    if config["command_kind"] == "async":
        if "priority" not in config or "queue_full_behavior" not in config:
            raise ProjectionError(
                f"async command {item['id']}: priority and queue policy are required"
            )
        line += f" priority {config['priority']} {config['queue_full_behavior']}"
    return "\n".join([f"@ OrbitFabric command: {item['id']}", line])


def _render_event(item: dict[str, Any], config: dict[str, Any]) -> str:
    try:
        severity = EVENT_SEVERITY_FPP[config["severity"]]
    except KeyError as exc:
        value = config.get("severity")
        raise ProjectionError(f"unsupported FPP event severity: {value!r}") from exc

    description = _annotation(item.get("description") or item["id"])
    return "\n".join(
        [
            f"@ OrbitFabric event: {item['id']} - {description}",
            f"event {config['symbol']} \\",
            f"  severity {severity} \\",
            f"  id {config['local_id']} \\",
            f"  format \"{_quote(item['id'])}\"",
        ]
    )


def _unrepresented(domain: str, item: dict[str, Any]) -> list[str]:
    return [field for field in UNREPRESENTED_FIELDS[domain] if field in item]


def _diagnostics(
    domain: str, entity_id: str, fields: list[str]
) -> list[dict[str, Any]]:
    return [
        {
            "severity": "info",
            "code": "OF_FPRIME_FIELD_NOT_PROJECTED",
            "source": {"domain": domain, "id": entity_id},
            "field": field,
        }
        for field in fields
    ]


def build_projection(model: dict[str, Any], profile: dict[str, Any]) -> ProjectionResult:
    """Build all FPP artifacts in memory before any output is written."""

    by_domain = {
        domain: _entity_map(model, domain)
        for domain in ("telemetry", "commands", "events", "packets")
    }
    settings = profile.get("settings")
    bindings = profile.get("bindings")
    if not isinstance(settings, dict):
        raise ProjectionError("profile.settings must be an object")
    if not isinstance(bindings, list):
        raise ProjectionError("profile.bindings must be an array")

    component_fragments: dict[str, dict[str, list[str]]] = defaultdict(
        lambda: defaultdict(list)
    )
    telemetry_targets: dict[str, str] = {}
    mappings: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []
    packet_bindings: list[tuple[dict[str, Any], dict[str, Any]]] = []
    binding_ids: set[str] = set()
    projected_sources: set[tuple[str, str]] = set()
    symbols: set[tuple[str, str]] = set()
    allocations: set[tuple[str, str, int]] = set()

    for binding in bindings:
        if not isinstance(binding, dict):
            raise ProjectionError("profile bindings must be objects")
        binding_id = binding.get("id")
        if not isinstance(binding_id, str) or not binding_id:
            raise ProjectionError("profile binding id must be a non-empty string")
        if binding_id in binding_ids:
            raise ProjectionError(f"duplicate binding id: {binding_id}")
        binding_ids.add(binding_id)

        domain, source_id = _source(binding)
        source_key = (domain, source_id)
        if source_key in projected_sources:
            raise ProjectionError(f"source projected more than once: {domain}:{source_id}")
        projected_sources.add(source_key)

        source = by_domain.get(domain, {}).get(source_id)
        if source is None:
            raise ProjectionError(f"source is not present in model: {domain}:{source_id}")

        config = binding.get("config")
        if not isinstance(config, dict):
            raise ProjectionError(f"binding {binding_id}: config must be an object")
        kind = config.get("kind")

        if kind == "packet":
            if domain != "packets":
                raise ProjectionError(
                    f"binding {binding_id}: packet config requires packets source"
                )
            packet_bindings.append((binding, source))
            continue

        expected_domain = {
            "telemetry": "telemetry",
            "command": "commands",
            "event": "events",
        }.get(kind)
        if expected_domain is None:
            raise ProjectionError(f"binding {binding_id}: unsupported kind {kind!r}")
        if domain != expected_domain:
            raise ProjectionError(f"binding {binding_id}: {kind} cannot project {domain}")

        component = config["host_component"]
        symbol = config["symbol"]
        symbol_key = (component, symbol)
        if symbol_key in symbols:
            raise ProjectionError(f"duplicate generated symbol in {component}: {symbol}")
        symbols.add(symbol_key)

        allocation_field = "local_opcode" if kind == "command" else "local_id"
        allocation_value = config[allocation_field]
        allocation_key = (component, kind, allocation_value)
        if allocation_key in allocations:
            raise ProjectionError(
                f"duplicate generated {kind} allocation in {component}: "
                f"{allocation_value}"
            )
        allocations.add(allocation_key)

        if kind == "telemetry":
            rendered = _render_telemetry(source, config, settings)
            component_fragments[component]["telemetry"].append(rendered)
            telemetry_targets[source_id] = f"{config['host_instance']}.{symbol}"
        elif kind == "command":
            rendered = _render_command(source, config)
            component_fragments[component]["commands"].append(rendered)
        else:
            rendered = _render_event(source, config)
            component_fragments[component]["events"].append(rendered)

        fields = _unrepresented(domain, source)
        mappings.append(
            {
                "binding_id": binding_id,
                "source": {"domain": domain, "id": source_id},
                "target": {
                    "kind": kind,
                    "host_component": component,
                    "host_instance": config["host_instance"],
                    "symbol": symbol,
                    allocation_field: allocation_value,
                },
                "unrepresented_source_fields": fields,
            }
        )
        diagnostics.extend(_diagnostics(domain, source_id, fields))

    artifacts = _component_artifacts(component_fragments)
    packet_artifacts, packet_mappings, packet_diagnostics = _project_packets(
        packet_bindings,
        telemetry_targets,
    )
    artifacts.extend(packet_artifacts)
    mappings.extend(packet_mappings)
    diagnostics.extend(packet_diagnostics)

    return ProjectionResult(
        artifacts=tuple(artifacts),
        mappings=tuple(mappings),
        diagnostics=tuple(diagnostics),
    )


def _component_artifacts(
    fragments: dict[str, dict[str, list[str]]],
) -> list[Artifact]:
    filenames = {
        "commands": "OF_Commands.fppi",
        "events": "OF_Events.fppi",
        "telemetry": "OF_Telemetry.fppi",
    }
    artifacts: list[Artifact] = []

    for component in sorted(fragments):
        safe_component = component.replace(".", "_")
        for category in ("commands", "events", "telemetry"):
            blocks = fragments[component].get(category)
            if not blocks:
                continue
            content = (
                "# Generated by orbitfabric-fprime-adapter. DO NOT EDIT.\n\n"
                + "\n\n".join(blocks)
                + "\n"
            )
            artifacts.append(
                Artifact(
                    role=f"fpp_{category}",
                    path=f"components/{safe_component}/{filenames[category]}",
                    content=content,
                    host_component=component,
                )
            )
    return artifacts


def _project_packets(
    packet_bindings: list[tuple[dict[str, Any], dict[str, Any]]],
    telemetry_targets: dict[str, str],
) -> tuple[list[Artifact], list[dict[str, Any]], list[dict[str, Any]]]:
    blocks_by_set: dict[str, list[str]] = defaultdict(list)
    packet_ids: set[tuple[str, int]] = set()
    packet_names: set[tuple[str, str]] = set()
    mappings: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []

    for binding, packet in packet_bindings:
        config = binding["config"]
        packet_set = config["packet_set"]
        id_key = (packet_set, config["packet_id"])
        name_key = (packet_set, config["packet_name"])
        if id_key in packet_ids:
            raise ProjectionError(
                f"duplicate packet id in {packet_set}: {config['packet_id']}"
            )
        if name_key in packet_names:
            raise ProjectionError(
                f"duplicate packet name in {packet_set}: {config['packet_name']}"
            )
        packet_ids.add(id_key)
        packet_names.add(name_key)

        members = packet.get("telemetry")
        if not isinstance(members, list) or not members:
            raise ProjectionError(f"packet {packet['id']}: telemetry must be non-empty")

        missing = [member for member in members if member not in telemetry_targets]
        if missing:
            raise ProjectionError(
                f"packet {packet['id']}: telemetry members have no projected "
                f"F Prime target: {missing}"
            )
        target_members = [telemetry_targets[member] for member in members]
        body = "\n".join(f"  {member}" for member in target_members)
        declaration = (
            f"packet {config['packet_name']} id {config['packet_id']} "
            f"group {config['group']} {{"
        )
        blocks_by_set[packet_set].append(
            "\n".join(
                [
                    f"@ OrbitFabric packet: {packet['id']}",
                    declaration,
                    body,
                    "}",
                ]
            )
        )

        fields = _unrepresented("packets", packet)
        mappings.append(
            {
                "binding_id": binding["id"],
                "source": {"domain": "packets", "id": packet["id"]},
                "target": {
                    "kind": "packet",
                    "packet_set": packet_set,
                    "packet_name": config["packet_name"],
                    "packet_id": config["packet_id"],
                    "group": config["group"],
                    "members": target_members,
                },
                "unrepresented_source_fields": fields,
            }
        )
        diagnostics.extend(_diagnostics("packets", packet["id"], fields))

    artifacts: list[Artifact] = []
    for packet_set in sorted(blocks_by_set):
        content = (
            "# Include this fragment inside the project-owned telemetry packet set block.\n"
            "# Generated by orbitfabric-fprime-adapter. DO NOT EDIT.\n\n"
            + "\n\n".join(blocks_by_set[packet_set])
            + "\n"
        )
        artifacts.append(
            Artifact(
                role="fpp_packet_specifiers",
                path=f"topology/{packet_set}/OF_Packets.fppi",
                content=content,
            )
        )
    return artifacts, mappings, diagnostics


def write_projection(result: ProjectionResult, output_dir: Path) -> list[dict[str, Any]]:
    """Write a validated projection result and return artifact metadata."""

    metadata: list[dict[str, Any]] = []
    for artifact in result.artifacts:
        path = output_dir / artifact.path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(artifact.content, encoding="utf-8")

        record: dict[str, Any] = {
            "role": artifact.role,
            "path": artifact.path,
            "sha256": artifact.sha256,
        }
        if artifact.host_component is not None:
            record["host_component"] = artifact.host_component
        metadata.append(record)
    return metadata
