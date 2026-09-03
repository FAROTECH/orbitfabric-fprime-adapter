# OrbitFabric F Prime Adapter

`orbitfabric-fprime-adapter` connects OrbitFabric mission contracts to native F Prime (F´) projects.

The adapter is designed to project explicit OrbitFabric contract entities into FPP artifacts while preserving F Prime ownership of component architecture, instances, topology, scheduling and runtime behavior.

> **Development status:** `0.1.0.dev0`. The canonical product identity and managed lifecycle are established. FPP projection semantics are being migrated from validated historical evidence and are not yet part of this baseline. There is no stable public release yet.

## Product boundary

OrbitFabric owns mission-level identity and integration contracts. This adapter owns F Prime-specific projection and target binding. F Prime remains authoritative for native FPP interpretation, autocoding, generated dictionaries, build behavior and runtime semantics.

In particular, this adapter does **not** infer:

- OrbitFabric subsystems as F Prime components;
- OrbitFabric relationships as F Prime topology connections;
- OrbitFabric modes as F Prime state machines;
- project topology, scheduling or runtime architecture.

The first product operation is reserved as:

```text
fpp_contract_projection
```

Its target-specific contract and implementation are intentionally introduced after the product bootstrap has been accepted.

## Canonical identity

```text
repository / distribution  orbitfabric-fprime-adapter
Python package              orbitfabric_fprime_adapter
console command             orbitfabric-fprime
adapter / integration id    orbitfabric-fprime
logical key                 orbitfabric/fprime
source coordinate           github.com/FAROTECH:orbitfabric/fprime
development version         0.1.0.dev0
first stable target         0.1.0
```

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
orbitfabric-fprime --version
pytest -q
ruff check .
mkdocs build --strict
```

The exact OrbitFabric Core conformance baseline used by CI is pinned in `.github/workflows/ci.yml`.

## Documentation

- [Architecture and ownership](docs/architecture-and-ownership.md)
- [Development and verification](docs/development.md)

## F Prime project relationship

F´ / F Prime is an external downstream project. This repository is an independent OrbitFabric integration and is not part of, or an endorsement by, the F Prime project, NASA or JPL.

## License

Apache License 2.0. See [LICENSE](LICENSE).
