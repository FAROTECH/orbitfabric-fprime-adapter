# Development and verification

This guide is for contributors working on the adapter source. Normal consumers should start with [Getting Started](getting-started.md).

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

## Repository map

```text
src/
    adapter product

examples/
    public executable integration stories

native_acceptance/
    concrete F Prime materialization and downstream acceptance

docs/
    user, architecture and contributor documentation
```

The public examples and the native acceptance harnesses are deliberately separate. The examples explain the integration property being demonstrated. The native harnesses ask the real F Prime toolchain to generate, build, resolve dictionaries and exercise selected runtime behavior.

## CI layers

Canonical CI separates the product concerns deliberately:

1. source quality, package tests and wheel construction;
2. exact OrbitFabric Core input-contract conformance;
3. consumer Reference Example contract-evolution proof;
4. native two-layout Reference Example generation, build and dictionary resolution;
5. provider-native FPP semantic reconciliation;
6. managed Adapter Manager lifecycle proof;
7. exact F Prime/FPP native static generation, build and dictionary conformance;
8. F Prime GDS closed-loop runtime acceptance;
9. provider-neutral release proof.

These layers are not interchangeable. Core conformance does not imply F Prime compatibility, semantic reconciliation does not replace generated-dictionary or runtime evidence, and F Prime native acceptance does not imply publication or external greenfield acceptance.

## Public local reproduction paths

The repository exposes two bounded local paths for users who want to reproduce the public integration evidence:

- [Contract Evolution Reference Example](https://github.com/FAROTECH/orbitfabric-fprime-adapter/blob/main/examples/reference-contract-evolution/README.md), including the full native `run_native.sh` path;
- [Semantic Reconciliation Reference Example](https://github.com/FAROTECH/orbitfabric-fprime-adapter/blob/main/examples/reference-semantic-reconciliation/README.md), including the clean FPP semantic greenfield path.

The default local workspaces used by these examples and native harnesses are ignored by Git so running a supported example does not dirty the checkout.

## Accepted downstream lane

The current canonical native lane is exact:

```text
F Prime  v4.2.2  @ 8a62e455a90b6d4f498c332d45d65a2a819988d8
FPP      3.2.0   @ 93f484b7521a8e8894cba25b26e633cc87d8e37a
```

CI has observed generation, build, generated dictionary conformance, provider-native semantic reconciliation and GDS closed-loop behavior for this pair. The Reference Examples exercise both the monolithic and split F Prime placements against the same exact lane. No broader target range is claimed.

## Version discipline

The current source version is:

```text
0.1.2
```

`v0.1.0` remains the immutable first stable release. `v0.1.1` corrected release identity metadata. The `0.1.2` patch keeps adapter behavior and the exact F Prime/FPP lane unchanged while freezing the two public Reference Examples, provider-native semantic reconciliation and their reproducible local paths in one tagged repository state.

Source development, release publication and post-publication acceptance remain distinct states:

```text
source under development
    != accepted source baseline
    != published release bytes
    != published-byte verification
    != external greenfield acceptance
```

Release tooling derives the default Source Coordinate from the adapter's canonical product identity. CI verifies that project metadata, canonical package identity and the Integration Package Manifest agree on the release version before release material can be published. Generated release material must preserve the exact structured Source Coordinate and version identity.
