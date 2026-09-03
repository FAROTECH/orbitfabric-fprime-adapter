# OrbitFabric F Prime Adapter

`orbitfabric-fprime-adapter` connects OrbitFabric mission contracts to native F Prime (F´) projects.

The adapter projects explicit OrbitFabric contract entities into FPP artifacts while preserving F Prime ownership of component architecture, instances, topology, scheduling and runtime behavior.

> **Development status:** `0.1.0.dev0`. Product identity, Core Integration Input Set execution, FPP projection, consumer Reference Example acceptance, exact-lane native generation/build/dictionary conformance and canonical GDS closed-loop runtime acceptance are established. Publication and external greenfield acceptance remain before the first stable release.

## Why this boundary exists

OrbitFabric owns stable mission-level identity and integration contracts. This adapter owns explicit F Prime-specific projection intent. F Prime remains authoritative for FPP interpretation, autocoding, generated dictionaries, build behavior and runtime semantics.

That means an F Prime project can evolve its internal architecture without forcing the upstream OrbitFabric mission contract to become an F Prime architecture model.

The adapter does **not** infer:

- OrbitFabric subsystems as F Prime components;
- OrbitFabric relationships as F Prime topology connections;
- OrbitFabric modes as F Prime state machines;
- project topology, scheduling or runtime architecture.

## First operation

```text
fpp_contract_projection
```

The first release is deliberately limited to four projection families:

```text
OrbitFabric telemetry   -> FPP telemetry declarations
OrbitFabric commands    -> FPP command declarations
OrbitFabric events      -> FPP event declarations
OrbitFabric packets     -> FPP telemetry packet specifiers
```

All target placement and local allocation are explicit Profile intent. The adapter does not create the hosting F Prime components, instances or topology.

## Canonical execution boundary

The adapter consumes the public Core Integration Input Set. It does not parse Mission Model YAML directly.

```bash
orbitfabric-fprime run \
  --operation fpp_contract_projection \
  --input-set-manifest path/to/integration_input_manifest.json \
  --profile path/to/fprime-profile.yaml \
  --output-dir generated/fprime
```

The adapter verifies the input-set digest, each required surface digest, supported Core surface versions, semantic lint state and Profile schema before projection. The generated bundle is completed by `integration_result.json`, which records input provenance, artifacts, mappings, integration diagnostics and execution-backed coverage.

See [Core input and result boundary](docs/core-input-and-result.md).

## Target lane

The initial compatibility lane is exact:

```text
F Prime  v4.2.2  @ 8a62e455a90b6d4f498c332d45d65a2a819988d8
FPP      3.2.0   @ 93f484b7521a8e8894cba25b26e633cc87d8e37a
```

Canonical CI has observed this exact lane through adapter wheel installation, FPP generation, `fprime-util generate`, `fprime-util build`, generated dictionary conformance and a live F Prime GDS closed loop. The runtime gate sends `Ref.pingRcvr.OF_SetMode(mode=2)` and observes command completion, `Ref.pingRcvr.OF_Temperature = 22.0` and `Ref.pingRcvr.OF_ModeChanged` in the evidence-only Ref fixture. No broader F Prime version range is currently claimed.

See [Target compatibility](docs/target-compatibility.md).

## Reference Example

The consumer-facing Reference Example demonstrates a central architectural property:

```text
one stable OrbitFabric mission contract
    -> Profile A -> monolithic F Prime placement
    -> Profile B -> split F Prime placement
```

The OrbitFabric source identities remain unchanged while the explicit F Prime host components and instances evolve. The example uses the exact accepted OrbitFabric Core baseline and verifies the dual projection through the installed adapter product path.

See [Stable Mission Contract, Evolving F Prime Architecture](examples/reference-contract-evolution/README.md).

## Integration Coverage

The initial semantic matrix is explicit about partial representation and unsupported semantics. OrbitFabric fields that do not have an equivalent FPP declaration meaning are preserved as upstream semantics rather than silently converted into F Prime behavior.

See [Integration Coverage](coverage/integration-coverage.md).

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

- [Product contract](docs/product-contract.md)
- [F Prime Projection Profile](docs/projection-profile.md)
- [Core input and result boundary](docs/core-input-and-result.md)
- [Architecture and ownership](docs/architecture-and-ownership.md)
- [Target compatibility](docs/target-compatibility.md)
- [Reference Example](examples/reference-contract-evolution/README.md)
- [Integration Coverage](coverage/integration-coverage.md)
- [Development and verification](docs/development.md)

## F Prime project relationship

F´ / F Prime is an external downstream project. This repository is an independent OrbitFabric integration and is not part of, or an endorsement by, the F Prime project, NASA or JPL.

## License

Apache License 2.0. See [LICENSE](LICENSE).
