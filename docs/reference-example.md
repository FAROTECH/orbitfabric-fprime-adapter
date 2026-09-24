# Reference Examples

The fastest way to understand this adapter is to run its two complementary Reference Examples.

They use the same OrbitFabric mission contract and explicit F Prime Projection Profiles, but answer different questions.

| Example | Main question | Evidence |
| --- | --- | --- |
| [Contract evolution](https://github.com/OrbitFabric/orbitfabric-fprime-adapter/tree/main/examples/reference-contract-evolution) | Can native F Prime architecture evolve while OrbitFabric mission identity stays stable? | consumer proof plus native generate/build/dictionary acceptance |
| [Semantic reconciliation](https://github.com/OrbitFabric/orbitfabric-fprime-adapter/tree/main/examples/reference-semantic-reconciliation) | Did the provider-native FPP semantic model interpret the explicit projected intent as expected? | typed reconciliation against FPP AST, analysis and source-location evidence |

## Reference Example 1: contract evolution

```text
same OrbitFabric mission contract
    -> Profile A -> monolithic F Prime placement
    -> Profile B -> split F Prime placement
```

The upstream OrbitFabric entity identities remain unchanged. F Prime component and instance placement changes only through explicit Profile intent.

The full native path materializes both layouts, runs `fprime-util generate`, runs `fprime-util build`, collects generated dictionaries and verifies that provider-resolved identity evolves exactly with the Profiles.

See the [Contract Evolution README](https://github.com/OrbitFabric/orbitfabric-fprime-adapter/blob/main/examples/reference-contract-evolution/README.md) for the detailed layouts and clean local reproduction path.

## Reference Example 2: semantic reconciliation

```text
OrbitFabric source identity
    -> explicit Projection Profile intent
    -> adapter FPP projection
    -> native FPP composition
    -> provider-native semantic observation
    -> fail-closed reconciliation evidence
```

This proof checks component and instance placement, local allocations, symbols, packet membership and generated-source provenance through the version-matched `fprime-python-model` API.

See the [Semantic Reconciliation README](https://github.com/OrbitFabric/orbitfabric-fprime-adapter/blob/main/examples/reference-semantic-reconciliation/README.md) for the clean greenfield path.

## Repository map

The repository separates public examples from provider-native acceptance harnesses:

```text
examples/
    public stories, Profiles and proof logic

native_acceptance/
    concrete F Prime materialization and downstream acceptance

src/
    adapter product

docs/
    user and architecture documentation
```

For the contract-evolution example specifically:

```text
examples/reference-contract-evolution/
    story + Profiles + consumer proof

native_acceptance/reference_example/
    materializer + full native runner + dictionary verifier
```

This split keeps the public example small while keeping the real F Prime project path executable and reviewable.

## Validated lane

Both examples stay on the exact accepted downstream lane:

```text
F Prime  v4.2.2  @ 8a62e455a90b6d4f498c332d45d65a2a819988d8
FPP      3.2.0   @ 93f484b7521a8e8894cba25b26e633cc87d8e37a
```

The semantic-reconciliation example additionally pins `fprime-community/fprime-python-model` to commit `934d79ddbe4ad1286e56a5575fed34fb0c44a1bb`.

Neither example widens the adapter compatibility claim.

For consumer installation of the released adapter, start with [Getting Started](getting-started.md).
