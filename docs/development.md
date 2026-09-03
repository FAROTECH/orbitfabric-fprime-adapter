# Development and verification

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Basic checks:

```bash
orbitfabric-fprime --version
ruff check .
pytest -q
mkdocs build --strict
```

## CI layers

The bootstrap CI intentionally separates four concerns:

1. source quality and package tests;
2. exact OrbitFabric Core manifest conformance;
3. managed Adapter Manager install, verify and remove behavior;
4. release descriptor and project-lock construction.

No F Prime native compatibility is claimed by these controls. Native F Prime generation, build, dictionary and runtime evidence are separate acceptance gates.

## Version discipline

Development version:

```text
0.1.0.dev0
```

Target first stable version:

```text
0.1.0
```

A stable version must not be published until the declared projection scope, Integration Coverage, native target acceptance, consumer examples and greenfield release path are all closed.
