# Contributing

Thank you for contributing to the OrbitFabric F Prime Adapter.

This repository has a strict ownership boundary: OrbitFabric defines mission-level integration contracts, this adapter defines F Prime-specific projection, and F Prime remains authoritative for native project architecture and runtime semantics.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the local checks before opening a pull request:

```bash
ruff check .
pytest -q
mkdocs build --strict
```

## Contribution rules

Changes should:

- preserve canonical OrbitFabric entity identity;
- avoid inferring F Prime component, topology or scheduling architecture from mission semantics;
- keep target-specific decisions explicit and reviewable;
- add negative tests when introducing validation rules;
- distinguish adapter-produced artifacts from F Prime-produced evidence;
- avoid compatibility claims that are not backed by observed native evidence;
- update documentation when public behavior or ownership boundaries change.

Generated build outputs and local evidence should not be committed unless a specific acceptance record requires them.

## Pull requests

Keep pull requests focused on one productization gate or one coherent behavior change. Describe what the change proves, what it does not prove, and any downstream assumptions it introduces.
