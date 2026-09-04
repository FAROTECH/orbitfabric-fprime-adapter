# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added

- Canonical `orbitfabric-fprime-adapter` product identity at `0.1.0.dev0`.
- Python package `orbitfabric_fprime_adapter` and console command `orbitfabric-fprime`.
- Integration identity `orbitfabric-fprime` and operation `fpp_contract_projection`.
- Canonical F Prime Projection Profile contract for telemetry, command, event and telemetry-packet bindings.
- Exact accepted target lane for F Prime v4.2.2 and FPP 3.2.0, including exact commits.
- Canonical FPP projection implementation with validation, allocation checks, diagnostics and Integration Result generation.
- Core Integration Input Set consumption with digest, surface, lint and identity verification.
- Integration Coverage matrix with explicit partial, unsupported, out-of-scope and non-applicable semantics.
- Native F Prime generation/build and generated dictionary conformance against the exact target lane.
- Canonical F Prime GDS closed-loop runtime acceptance for projected command, telemetry, event and command completion.
- Consumer Reference Example showing one stable OrbitFabric contract across monolithic and split F Prime placements.
- Native Reference Example acceptance proving both placements through F Prime generation, build and generated dictionary resolution while preserving the same OrbitFabric source identity set.
- Managed install, verify, execute, inspect and remove lifecycle proof through OrbitFabric Adapter Manager.
- Provider-neutral release descriptor and project-lock proof.
- MkDocs documentation baseline.

### Remaining before stable 0.1.0

- immutable publication of the stable release bytes with checksums and provenance;
- published-byte verification;
- external greenfield installation and execution of the consumer path.

The development baseline must not be described as a stable public release until those release gates are closed.
