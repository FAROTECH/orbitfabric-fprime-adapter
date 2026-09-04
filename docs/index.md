# OrbitFabric F Prime Adapter

The OrbitFabric F Prime Adapter projects selected OrbitFabric mission-contract entities into native FPP declaration fragments through explicit target bindings.

The current stable release is `0.1.0` (`v0.1.0`). Published release bytes, external greenfield installation/execution, native two-layout F Prime acceptance and canonical GDS closed-loop runtime acceptance are complete.

## Choose your path

### I want to use the adapter

Start with [Getting Started](getting-started.md) for the published release and Adapter Manager consumer flow.

### I want to try the adapter

Start with the [Reference Example](../examples/reference-contract-evolution/README.md). It demonstrates one stable OrbitFabric mission contract projected into two different native F Prime placements while keeping upstream source identities unchanged.

### I want to develop or contribute

Start with [Development and verification](development.md).

## Current product boundary

The operation is `fpp_contract_projection`. Its initial semantic scope covers telemetry, commands, events and telemetry packet specifiers while leaving F Prime component architecture, topology, scheduling and runtime behavior under F Prime project ownership.

The adapter does not infer F Prime architecture from OrbitFabric structure. Target placement is explicit Profile intent, and the generated FPP fragments are composed by an existing F Prime project.

## Documentation

- [Getting Started](getting-started.md)
- [Reference Example](../examples/reference-contract-evolution/README.md)
- [Product contract](product-contract.md)
- [F Prime Projection Profile](projection-profile.md)
- [Core input and result boundary](core-input-and-result.md)
- [Architecture and ownership](architecture-and-ownership.md)
- [Target compatibility](target-compatibility.md)
- [Integration Coverage](integration-coverage.md)
- [Development and verification](development.md)
- [0.1.0 release notes](releases/0.1.0.md)
