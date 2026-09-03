from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".py", ".toml", ".json", ".yaml", ".yml", ".sh"}
IGNORED_PARTS = {".git", ".venv", "build", "dist", "site", "__pycache__"}


def _text_files():
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if any(part in IGNORED_PARTS for part in path.relative_to(ROOT).parts):
            continue
        yield path


def test_inherited_scaffolding_language_is_absent() -> None:
    forbidden = (
        "dum" + "my",
        "tem" + "plate",
    )
    findings: list[str] = []

    for path in _text_files():
        text = path.read_text(encoding="utf-8").lower()
        for token in forbidden:
            if token in text:
                findings.append(f"{path.relative_to(ROOT)} contains forbidden residue: {token}")

    assert findings == []


def test_long_dash_characters_are_absent() -> None:
    forbidden_codepoints = {0x2013, 0x2014}
    findings: list[str] = []

    for path in _text_files():
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(ord(character) in forbidden_codepoints for character in line):
                findings.append(f"{path.relative_to(ROOT)}:{line_number}")

    assert findings == []
