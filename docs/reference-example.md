# Reference Example

The Reference Example is the fastest way to evaluate the architectural purpose of the adapter.

It demonstrates one stable OrbitFabric mission contract projected into two different native F Prime placements:

```text
same OrbitFabric mission contract
    -> Profile A -> monolithic F Prime placement
    -> Profile B -> split F Prime placement
```

The upstream OrbitFabric entity identities remain unchanged. The F Prime component and instance placement changes only through explicit Profile intent.

## What the example proves

The accepted `0.1` example requires:

- the same OrbitFabric mission identity across both layouts;
- the same Core Integration Input Set across both layouts;
- the same OrbitFabric source identity set;
- explicit F Prime placement changes matching the two Profiles;
- telemetry packet membership following the changed telemetry placement;
- native `fprime-util generate` and `fprime-util build` success for both layouts;
- generated F Prime dictionaries resolving the projected command, event, telemetry and packet identities.

The validated lane is exact:

```text
F Prime  v4.2.2  @ 8a62e455a90b6d4f498c332d45d65a2a819988d8
FPP      3.2.0   @ 93f484b7521a8e8894cba25b26e633cc87d8e37a
```

## Why this matters

The adapter is not trying to replace FPP or model F Prime topology.

Its value is the separation of concerns:

```text
OrbitFabric
    owns stable mission-level identity and generic integration contracts

Projection Profile
    owns explicit F Prime-specific placement and allocation intent

F Prime project
    owns components, instances, topology, wiring, scheduling and runtime architecture

F Prime toolchain
    owns native interpretation, build and generated downstream identity
```

This lets the native F Prime architecture evolve without forcing the upstream mission contract to be renamed or remodeled around one implementation layout.

## Full runnable example

The complete example inputs, profiles, verifier and native acceptance fixture are kept in the repository under:

[examples/reference-contract-evolution](https://github.com/FAROTECH/orbitfabric-fprime-adapter/tree/main/examples/reference-contract-evolution)

Read the full [Reference Example README](https://github.com/FAROTECH/orbitfabric-fprime-adapter/blob/main/examples/reference-contract-evolution/README.md) for the detailed layouts and execution path.

For consumer installation of the released adapter, start with [Getting Started](getting-started.md).
