from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import rfc8785

CANONICAL_ROLES = {
    "entity_index": ("required", "orbitfabric.entity_index", "0.1"),
    "lint_report": ("required", "orbitfabric-lint", "v1"),
    "mission_snapshot": ("required", "orbitfabric.mission_snapshot", "0.1-candidate"),
    "model_summary": ("companion", "orbitfabric.model_summary", "0.1"),
    "relationship_manifest": (
        "required",
        "orbitfabric.relationship_manifest",
        "0.1-candidate",
    ),
}


class InputSetError(ValueError):
    """Raised when the Core Integration Input Set cannot be safely consumed."""


@dataclass(frozen=True)
class LoadedInputSet:
    root: Path
    manifest: dict[str, Any]
    snapshot: dict[str, Any]
    entity_index: dict[str, Any]
    relationship_manifest: dict[str, Any]
    lint_report: dict[str, Any]
    model_summary: dict[str, Any] | None

    @property
    def model(self) -> dict[str, Any]:
        model = self.snapshot.get("model")
        if not isinstance(model, dict):
            raise InputSetError("mission_snapshot.model is not an object")
        return model


def _sha256(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise InputSetError(f"cannot read surface {path}: {exc}") from exc


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InputSetError(f"cannot load JSON document {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise InputSetError(f"{path}: top-level JSON must be an object")
    return value


def _digest_payload(manifest: dict[str, Any]) -> dict[str, Any]:
    records = manifest.get("surfaces")
    if not isinstance(records, list):
        raise InputSetError("manifest.surfaces must be an array")

    surfaces = []
    for surface in sorted(records, key=lambda item: item.get("role", "")):
        if not isinstance(surface, dict):
            raise InputSetError("invalid surface record")
        surfaces.append(
            {
                key: surface.get(key)
                for key in (
                    "role",
                    "requirement",
                    "status",
                    "kind",
                    "format_version",
                    "sha256",
                    "unavailable_reason",
                )
            }
        )

    return {
        "kind": manifest.get("kind"),
        "input_set_version": manifest.get("input_set_version"),
        "orbitfabric_version": manifest.get("orbitfabric_version"),
        "mission": manifest.get("mission"),
        "load_result": manifest.get("load_result"),
        "lint_result": manifest.get("lint_result"),
        "surfaces": surfaces,
    }


def compute_input_set_sha256(manifest: dict[str, Any]) -> str:
    canonical = rfc8785.dumps(_digest_payload(manifest))
    return hashlib.sha256(canonical).hexdigest()


def _safe_surface_path(root: Path, relative: str) -> Path:
    path = (root / relative).resolve()
    if path == root or root not in path.parents:
        raise InputSetError(f"surface path escapes input-set root: {relative}")
    return path


def load_input_set(manifest_path: Path) -> LoadedInputSet:
    manifest_path = manifest_path.resolve()
    if manifest_path.name != "integration_input_manifest.json":
        raise InputSetError("input-set manifest must be integration_input_manifest.json")

    root = manifest_path.parent
    manifest = _load_json(manifest_path)
    if manifest.get("kind") != "orbitfabric.integration_input_set":
        raise InputSetError("unsupported input-set kind")
    if manifest.get("input_set_version") != "0.1-candidate":
        raise InputSetError("unsupported input-set version")
    if manifest.get("load_result") != "loaded":
        raise InputSetError(f"input set is not loaded: {manifest.get('load_result')!r}")
    if manifest.get("lint_result") not in {"passed", "passed_with_warnings"}:
        raise InputSetError(
            f"semantic lint blocks projection: {manifest.get('lint_result')!r}"
        )

    records = manifest.get("surfaces")
    if not isinstance(records, list):
        raise InputSetError("manifest.surfaces must be an array")

    by_role: dict[str, dict[str, Any]] = {}
    for record in records:
        if not isinstance(record, dict) or not isinstance(record.get("role"), str):
            raise InputSetError("invalid surface record")
        role = record["role"]
        if role in by_role:
            raise InputSetError(f"duplicate surface role: {role}")
        by_role[role] = record

    if set(by_role) != set(CANONICAL_ROLES):
        raise InputSetError(
            "canonical roles mismatch: "
            f"expected {sorted(CANONICAL_ROLES)}, got {sorted(by_role)}"
        )

    declared_digest = manifest.get("input_set_sha256")
    actual_digest = compute_input_set_sha256(manifest)
    if declared_digest != actual_digest:
        raise InputSetError(
            f"input_set_sha256 mismatch: expected {declared_digest}, computed {actual_digest}"
        )

    loaded: dict[str, dict[str, Any] | None] = {}
    for role, (requirement, kind, format_version) in CANONICAL_ROLES.items():
        record = by_role[role]
        if record.get("requirement") != requirement:
            raise InputSetError(f"{role}: unexpected requirement")
        if record.get("kind") != kind or record.get("format_version") != format_version:
            raise InputSetError(f"{role}: unsupported kind/format_version")

        if record.get("status") != "available":
            if requirement == "required":
                raise InputSetError(f"required surface unavailable: {role}")
            loaded[role] = None
            continue

        relative = record.get("path")
        if not isinstance(relative, str) or not relative:
            raise InputSetError(f"{role}: available surface has no path")
        path = _safe_surface_path(root, relative)
        if _sha256(path) != record.get("sha256"):
            raise InputSetError(f"{role}: SHA-256 mismatch")
        loaded[role] = _load_json(path)

    snapshot = loaded["mission_snapshot"]
    index = loaded["entity_index"]
    relationships = loaded["relationship_manifest"]
    lint = loaded["lint_report"]
    assert snapshot is not None
    assert index is not None
    assert relationships is not None
    assert lint is not None

    if snapshot.get("kind") != "orbitfabric.mission_snapshot":
        raise InputSetError("mission snapshot kind mismatch")
    if snapshot.get("result") != "loaded":
        raise InputSetError("mission snapshot is not loaded")
    if index.get("kind") != "orbitfabric.entity_index":
        raise InputSetError("entity index kind mismatch")
    if relationships.get("kind") != "orbitfabric.relationship_manifest":
        raise InputSetError("relationship manifest kind mismatch")
    if lint.get("tool") != "orbitfabric-lint":
        raise InputSetError("lint report tool mismatch")
    if lint.get("result") != manifest.get("lint_result"):
        raise InputSetError("lint report result does not match input-set manifest")

    return LoadedInputSet(
        root=root,
        manifest=manifest,
        snapshot=snapshot,
        entity_index=index,
        relationship_manifest=relationships,
        lint_report=lint,
        model_summary=loaded["model_summary"],
    )
