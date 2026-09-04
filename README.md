# OrbitFabric F Prime Adapter

`orbitfabric-fprime-adapter` connects OrbitFabric mission contracts to native F Prime (F') projects.

The adapter projects explicit OrbitFabric contract entities into FPP declaration fragments while preserving F Prime ownership of component architecture, instances, topology, scheduling and runtime behavior.

> **Release baseline:** `0.1.1`. This patch preserves the accepted F Prime/FPP behavior of the `0.1` line and aligns Adapter Source Coordinate metadata with the canonical product identity.

## Choose your path

### I want to use the adapter

Use the published release through **OrbitFabric Adapter Manager**.

```text
OrbitFabric Core
    -> published adapter release
    -> Adapter Manager install
    -> verify
    -> execute fpp_contract_projection
    -> FPP declaration fragments + Integration Result
```

A normal consumer does not need an editable source install, a locally rebuilt wheel or publisher tooling.

Start with **[Getting Started](docs/getting-started.md)**.

### I want to try the adapter

Start with the **[Reference Example: Stable Mission Contract, Evolving F Prime Architecture](examples/reference-contract-evolution/README.md)**.

It demonstrates the central architectural property of this adapter:

```text
same OrbitFabric mission contract
    -> Profile A -> monolithic F Prime placement
    -> Profile B -> split F Prime placement
```

The OrbitFabric source identities stay stable while explicit F Prime component and instance placement evolves. Both layouts have been materialized into native F Prime projects and accepted through `fprime-util generate`, `fprime-util build` and generated dictionary verification against the exact supported F Prime lane.

This is intentionally not an F Prime project generator. It is a reviewable bridge from stable mission-level contract identity to project-owned native F Prime architecture.

### I want to develop or contribute

Clone the repository and use the development environment:

```bash
git clone https://github.com/FAROTECH/orbitfabric-fprime-adapter.git
cd orbitfabric-fprime-adapter

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The direct adapter console command:

```text
orbitfabric-fprime
```

is primarily a contributor and development surface. Normal consumers should use `orbitfabric adapter ...` through Adapter Manager.

Start with **[Development and verification](docs/development.md)**.

## What the adapter does

The `0.1` product line consumes the public OrbitFabric Core Integration Input Set and supports one deliberately narrow operation:

```text
fpp_contract_projection
```

Its initial projection families are:

```text
OrbitFabric telemetry   -> FPP telemetry declarations
OrbitFabric commands    -> FPP command declarations
OrbitFabric events      -> FPP event declarations
OrbitFabric packets     -> FPP telemetry packet specifiers
```

All F Prime placement and local allocation choices are explicit Profile intent. The adapter does not create the hosting F Prime components, instances or topology.

The adapter does **not** infer:

- OrbitFabric subsystems as F Prime components;
- OrbitFabric relationships as F Prime topology connections;
- OrbitFabric modes as F Prime state machines;
- project topology, scheduling or runtime architecture.

## Why this boundary exists

OrbitFabric owns stable mission-level identity and generic integration contracts. This adapter owns explicit F Prime-specific projection intent. F Prime remains authoritative for component architecture, FPP interpretation, autocoding, generated dictionaries, build behavior and runtime semantics.

That separation allows an F Prime project to refactor its native architecture without forcing the upstream mission contract to become an F Prime architecture model.

The Reference Example makes this property executable rather than merely descriptive.

## Consumer execution model

The adapter consumes a coherent Core Integration Input Set. It does not parse Mission Model YAML directly.

Normal managed execution is:

```bash
orbitfabric adapter execute "$ORBITFABRIC_ADAPTER_INSTANCE_ID" \
  --operation fpp_contract_projection \
  --input-set-manifest <integration_input_manifest.json> \
  --profile <fprime-profile.yaml> \
  --output-dir <output-directory>
```

Representative outputs include:

```text
components/<component>/OF_Commands.fppi
components/<component>/OF_Events.fppi
components/<component>/OF_Telemetry.fppi
topology/<packet-set>/OF_Packets.fppi
integration_result.json
```

The adapter verifies the input-set digest, required surface digests, supported Core surface versions, semantic lint state and Profile schema before projection. `integration_result.json` records input provenance, artifacts, mappings, diagnostics, resolutions and execution-backed coverage.

See [Core input and result boundary](docs/core-input-and-result.md).

## Validated target lane

The compatibility lane remains exact:

```text
F Prime  v4.2.2  @ 8a62e455a90b6d4f498c332d45d65a2a819988d8
FPP      3.2.0   @ 93f484b7521a8e8894cba25b26e633cc87d8e37a
```

Canonical CI has observed this exact lane through adapter wheel installation, FPP generation, `fprime-util generate`, `fprime-util build`, generated dictionary conformance and a live F Prime GDS closed loop. No broader F Prime or FPP version range is currently claimed.

See [Target compatibility](docs/target-compatibility.md).

## Evidence model

The release line is backed by independent layers rather than one aggregate test:

```text
Core contract conformance
        +
adapter-owned tests
        +
consumer Reference Example
        +
native two-layout F Prime generate/build/dictionary acceptance
        +
installed Adapter Manager lifecycle
        +
canonical GDS closed-loop runtime acceptance
        +
release proof and published-byte verification
        +
external greenfield installation and execution
```

Core conformance does not substitute for downstream-native acceptance, and native acceptance does not substitute for release/publication evidence.

## Integration Coverage

The semantic matrix is explicit about partial representation and unsupported semantics. OrbitFabric fields that do not have an equivalent FPP declaration meaning are preserved as upstream semantics rather than silently converted into F Prime behavior.

See [Integration Coverage](coverage/integration-coverage.md).

## Product identity

```text
repository / distribution  orbitfabric-fprime-adapter
Python package              orbitfabric_fprime_adapter
console command             orbitfabric-fprime
adapter / integration id    orbitfabric-fprime
logical key                 orbitfabric/fprime
source coordinate           github.com/FAROTECH:orbitfabric/fprime
version                     0.1.1
```

## Documentation

### User

- [Getting Started](docs/getting-started.md)
- [Reference Example](examples/reference-contract-evolution/README.md)
- [F Prime Projection Profile](docs/projection-profile.md)
- [Core input and result boundary](docs/core-input-and-result.md)
- [Integration Coverage](coverage/integration-coverage.md)

### Developer / Contributor

- [Development and verification](docs/development.md)
- [Product contract](docs/product-contract.md)
- [Architecture and ownership](docs/architecture-and-ownership.md)
- [Target compatibility](docs/target-compatibility.md)

### Release

- [0.1.1 release notes](docs/releases/0.1.1.md)
- [0.1.0 release notes](docs/releases/0.1.0.md)

## F Prime project relationship

F Prime is an independent downstream project. This repository is an independent OrbitFabric integration and is not part of, or an endorsement by, the F Prime project, NASA or JPL.

## License

Apache License 2.0. See [LICENSE](LICENSE).
