# OrbitFabric F Prime Adapter

The OrbitFabric F Prime Adapter projects selected OrbitFabric mission-contract entities into native FPP declaration fragments through explicit target bindings.

The project is currently at `0.1.0.dev0`.

## Current product boundary

The first operation is `fpp_contract_projection`. Its initial semantic scope covers telemetry, commands, events and telemetry packet specifiers while leaving F Prime component architecture, topology, scheduling and runtime behavior under F Prime project ownership.

Canonical implementation, Core Integration Input Set consumption, Integration Result generation, consumer Reference Example acceptance, exact-lane F Prime generation/build/dictionary conformance and GDS closed-loop runtime acceptance are established. Publication and external greenfield acceptance remain before the first stable release.

Continue with:

- [Product contract](product-contract.md)
- [F Prime Projection Profile](projection-profile.md)
- [Core input and result boundary](core-input-and-result.md)
- [Architecture and ownership](architecture-and-ownership.md)
- [Target compatibility](target-compatibility.md)
- [Integration Coverage](integration-coverage.md)
- [Development and verification](development.md)
