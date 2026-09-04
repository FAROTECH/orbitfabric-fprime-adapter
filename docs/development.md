# Development and verification

This guide is for contributors working on the adapter source. Normal consumers should start with [Getting Started](getting-started.md).

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
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

Canonical CI separates the product concerns deliberately:

1. source quality, package tests and wheel construction;
2. exact OrbitFabric Core input-contract conformance;
3. consumer Reference Example acceptance;
4. native two-layout Reference Example generation, build and dictionary resolution;
5. managed Adapter Manager lifecycle proof;
6. exact F Prime/FPP native generation, build and dictionary conformance;
7. F Prime GDS closed-loop runtime acceptance;
8. provider-neutral release proof.

These layers are not interchangeable. Core conformance does not imply F Prime compatibility, and F Prime native acceptance does not imply publication or external greenfield acceptance.

## Accepted downstream lane

The current canonical native lane is exact:

```text
F Prime  v4.2.2  @ 8a62e455a90b6d4f498c332d45d65a2a819988d8
FPP      3.2.0   @ 93f484b7521a8e8894cba25b26e633cc87d8e37a
```

CI has observed generation, build, generated dictionary conformance and GDS closed-loop behavior for this pair. The Reference Example also proves both its monolithic and split F Prime placements through native generation, build and generated dictionary resolution against the same exact lane. No broader target range is claimed.

## Version discipline

The current source version is:

```text
0.1.1
```

`v0.1.0` remains the immutable first stable release. The `0.1.1` patch retains the same F Prime integration behavior while aligning release metadata with the canonical Adapter Source Coordinate.

Source development, release publication and post-publication acceptance remain distinct states:

```text
source under development
    != accepted source baseline
    != published release bytes
    != published-byte verification
    != external greenfield acceptance
```

Release tooling derives the default Source Coordinate from the adapter's canonical product identity. CI verifies that generated release material preserves that exact structured identity before the release publication pipeline can publish it.
