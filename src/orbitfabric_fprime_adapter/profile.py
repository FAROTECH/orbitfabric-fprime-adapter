from __future__ import annotations

import hashlib
import json
from importlib.resources import files
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator


class ProfileError(ValueError):
    """Raised when a projection Profile cannot be parsed or validated."""


def sha256_file(path: Path) -> str:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError as exc:
        raise ProfileError(f"cannot read Profile {path}: {exc}") from exc


def _schema() -> dict[str, Any]:
    value = json.loads(
        files("orbitfabric_fprime_adapter")
        .joinpath("schemas/profile-0.1.schema.json")
        .read_text(encoding="utf-8")
    )
    if not isinstance(value, dict):
        raise ProfileError("packaged Profile schema is invalid")
    return value


def load_profile(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ProfileError(f"cannot read Profile {path}: {exc}") from exc

    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise ProfileError(f"cannot parse Profile {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ProfileError("Profile top level must be an object")

    errors = sorted(
        Draft202012Validator(_schema()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        error = errors[0]
        location = ".".join(str(part) for part in error.absolute_path) or "<root>"
        raise ProfileError(f"Profile validation failed at {location}: {error.message}")
    return value
