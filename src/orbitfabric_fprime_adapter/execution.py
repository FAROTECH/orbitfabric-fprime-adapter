from __future__ import annotations

from pathlib import Path
from typing import Any

from .input_set import LoadedInputSet, load_input_set
from .profile import load_profile
from .projection import ProjectionError, ProjectionResult, build_projection, write_projection
from .result import successful_result, write_result


class ExecutionError(ValueError):
    """Raised when canonical adapter execution cannot complete."""


def _indexed_entities(input_set: LoadedInputSet) -> set[tuple[str, str]]:
    records = input_set.entity_index.get("entities")
    if not isinstance(records, list):
        raise ExecutionError("entity_index.entities must be an array")

    result: set[tuple[str, str]] = set()
    for record in records:
        if not isinstance(record, dict):
            raise ExecutionError("entity_index.entities entries must be objects")
        domain = record.get("domain")
        entity_id = record.get("id")
        if not isinstance(domain, str) or not isinstance(entity_id, str):
            raise ExecutionError("entity_index entity domain and id must be strings")
        result.add((domain, entity_id))
    return result


def _validate_profile_sources(
    input_set: LoadedInputSet,
    profile: dict[str, Any],
) -> None:
    indexed = _indexed_entities(input_set)
    for binding in profile["bindings"]:
        source = binding["sources"][0]
        key = (source["domain"], source["id"])
        if key not in indexed:
            raise ExecutionError(
                f"Profile source is not present in Core entity_index: {key[0]}:{key[1]}"
            )


def execute_projection(
    *,
    manifest_path: Path,
    profile_path: Path,
    output_dir: Path,
) -> tuple[ProjectionResult, dict[str, Any]]:
    input_set = load_input_set(manifest_path)
    profile = load_profile(profile_path)
    _validate_profile_sources(input_set, profile)

    try:
        projection = build_projection(input_set.model, profile)
    except ProjectionError as exc:
        raise ExecutionError(str(exc)) from exc

    artifact_metadata = write_projection(projection, output_dir)
    result = successful_result(
        input_set=input_set,
        profile=profile,
        profile_path=profile_path,
        projection=projection,
        artifact_metadata=artifact_metadata,
    )
    write_result(output_dir, result)
    return projection, result
