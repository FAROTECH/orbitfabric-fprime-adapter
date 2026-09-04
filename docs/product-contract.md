# Product contract

## Operation

The first adapter operation is:

```text
fpp_contract_projection
```

It projects selected OrbitFabric mission-contract entities into FPP declaration fragments for explicit composition inside an existing F Prime project.

It does **not** create an F Prime project.

## Inputs

The operation consumes:

1. an OrbitFabric Core Integration Input Set;
2. an F Prime Projection Profile conforming to `profile-0.1.schema.json`.

Additional operation inputs:

```text
none
```

A Scenario is therefore not part of this operation.

The required Core surface contract is declared by the canonical Integration Package Manifest and is validated at execution time before projection.

## First projection families

The `0.1` product surface is deliberately limited to:

- telemetry declarations;
- command declarations;
- event declarations;
- telemetry packet specifiers.

The corresponding FPP fragments are included by project-owned F Prime source.

## Ownership boundary

The adapter may own:

- FPP-safe generated symbols;
- explicit Profile placement into an existing component/instance;
- target-local ids and command opcodes;
- command declaration kind and async queue policy;
- telemetry update policy and explicit limit-color policy;
- explicit F Prime event severity;
- telemetry packet name/id/group allocation;
- source-to-target mappings, diagnostics and coverage.

The adapter does not own:

- F Prime component architecture;
- component instances;
- topology and port wiring;
- rate groups or scheduling;
- threads, queues, stacks or priorities outside explicitly projected command declaration policy;
- runtime implementation behavior;
- globally resolved F Prime ids;
- generated dictionary semantics.

## Artifact boundary

Adapter-produced artifacts are:

```text
component-scoped FPP command include fragment(s)
component-scoped FPP event include fragment(s)
component-scoped FPP telemetry include fragment(s)
topology-scoped FPP telemetry packet-specifier fragment(s)
OrbitFabric Integration Result
```

The F Prime JSON dictionary is **downstream-produced evidence**, not an adapter-produced product artifact.

A project-owned component explicitly includes component fragments. A project-owned topology explicitly composes the telemetry packet specifiers inside its packet-set declaration. The adapter must not generate a complete topology merely to make composition convenient.
