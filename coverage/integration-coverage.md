# F Prime Adapter Integration Coverage

Status: **initial semantic declaration for `0.1.0.dev0`; canonical implementation and native acceptance are still pending.**

This matrix defines the semantic denominator for the first maintained OrbitFabric F Prime adapter. It records what is meaningful for F Prime, what the first product intends to project, and where OrbitFabric semantics intentionally remain outside the FPP declaration surface.

It is not a measure of how much of F Prime is supported. It is also not a Core conformance contract.

## Adapter intent

```text
OrbitFabric mission contract
    -> explicit F Prime Projection Profile
    -> component-scoped FPP command / event / telemetry fragments
    -> topology-scoped FPP telemetry packet specifiers
    -> project-owned F Prime composition
    -> F Prime toolchain as downstream authority
```

The first release does not generate F Prime components, instances, topology, scheduling or runtime behavior.

## Status vocabulary

- `FULL`: the applicable OrbitFabric semantic area has a direct target representation for the declared adapter claim.
- `PARTIAL`: a meaningful target representation exists, but some OrbitFabric semantics remain outside that representation or require explicit target policy.
- `TARGET_UNSUPPORTED`: the target has no generic equivalent for the OrbitFabric semantic claim considered here.
- `OUT_OF_SCOPE`: a target-specific mapping could be investigated, but the first adapter release deliberately does not promise it.
- `NOT_ANALYZED`: no product disposition has yet been reached.
- `NOT_APPLICABLE`: treating the OrbitFabric concept as the proposed target concept would be a category error for this adapter.

`PARTIAL` is not a quality defect. It is often the correct result when the mission contract is richer than a downstream declaration language.

## Initial matrix

| OrbitFabric semantic area | F Prime representation / boundary | v0.1 disposition | Canonical implementation | Evidence / rationale |
| --- | --- | --- | --- | --- |
| Mission identity and source entity identity | Integration Result mappings plus preserved `{domain,id}` source identity | FULL | pending PR4 | Core identity remains authoritative; target placement must not replace source identity |
| Core Integration Input Set provenance | adapter input/provenance boundary, not an FPP declaration | FULL | pending PR4 | historical PoC consumed a coherent Input Set and verified surface digests; canonical proof is still required |
| Telemetry declaration | FPP telemetry declaration inside a project-owned component | PARTIAL | pending PR3 | type, target symbol, local id, update policy and selected numeric limits are representable; mission-level fields remain outside FPP |
| Telemetry primitive type | FPP built-in primitive types | PARTIAL | pending PR3 | historical proof covers bool, unsigned/signed 8/16/32-bit integers and float32/float64 only; enum/string are not claimed |
| Telemetry unit | no equivalent field in the generated FPP telemetry declaration used by this adapter | TARGET_UNSUPPORTED | n/a | preserve in OrbitFabric; do not manufacture a target annotation as equivalent semantics |
| Telemetry limits | FPP yellow/orange/red low/high limits via explicit Profile policy | PARTIAL | pending PR3 | warning/critical vocabulary is not identical to FPP color levels; mapping must remain explicit |
| Telemetry sampling / persistence / downlink priority / quality | no direct equivalent in the generated declaration slice | TARGET_UNSUPPORTED | n/a | these remain mission semantics rather than implicit F Prime runtime policy |
| Command declaration | FPP sync/guarded/async command declaration | PARTIAL | pending PR3 | symbol, local opcode, command kind and primitive arguments are representable; broader OrbitFabric command semantics are not |
| Command primitive argument type | FPP built-in primitive parameter types | PARTIAL | pending PR3 | same proven primitive type subset as telemetry; argument-name validity must be checked before rendering |
| Command allowed modes / preconditions / timeout / risk | no direct generic command-declaration equivalent | TARGET_UNSUPPORTED | n/a | must not be converted into hidden runtime behavior |
| Command acknowledgement / expected effects / emitted events | potential runtime or evidence relationships, not equivalent declaration fields | OUT_OF_SCOPE | n/a | require a separate evidence-backed target contract before widening scope |
| Event declaration | FPP event declaration | PARTIAL | pending PR3 | target symbol, local id and explicit F Prime severity are representable; OrbitFabric severity is not assumed equivalent |
| Event severity | Profile-authored F Prime severity | PARTIAL | pending PR3 | F Prime and OrbitFabric severity vocabularies are not treated as one-to-one; target severity is explicit intent |
| Event persistence / downlink priority | no direct equivalent in the generated FPP event declaration | TARGET_UNSUPPORTED | n/a | preserve in OrbitFabric coverage diagnostics |
| Telemetry packet membership | FPP telemetry packet specifier composed inside a project-owned packet set | PARTIAL | pending PR3 | member identity is meaningful after telemetry target resolution; adapter does not own the enclosing topology packet-set policy |
| Packet type / max payload / period | no direct equivalent in the packet specifier fragment | TARGET_UNSUPPORTED | n/a | no implicit scheduling, completeness or payload policy is generated |
| Data products | F Prime records/containers are possible candidates but are not one-to-one with OrbitFabric products | OUT_OF_SCOPE | n/a | explicitly deferred from v0.1.0 |
| Fault / FDIR model | no single generic F Prime declaration equivalent | TARGET_UNSUPPORTED | n/a | a future integration would need concrete F Prime component/runtime semantics, not a guessed mapping |
| OrbitFabric subsystem -> F Prime component | F Prime component architecture is project-owned | NOT_APPLICABLE | n/a | direct inference is explicitly forbidden |
| OrbitFabric mode -> F Prime state machine | F Prime state-machine/runtime architecture is project-owned | NOT_APPLICABLE | n/a | direct inference is explicitly forbidden |
| OrbitFabric relationship -> F Prime topology/port connection | F Prime topology is project-owned | NOT_APPLICABLE | n/a | direct inference is explicitly forbidden |
| F Prime component placement | explicit Profile `host_component` / `host_instance` target intent | FULL | pending PR3 | placement is adapter/Profile-owned and may change without changing OrbitFabric source identity |
| F Prime local allocation | explicit Profile local id/opcode and packet allocation | FULL | pending PR3 | adapter must reject local collisions before generation; downstream build remains final authority |
| Globally resolved F Prime identity | generated F Prime dictionary | FULL | pending PR5 | adapter must consume downstream-produced resolution evidence rather than concatenate names to manufacture identity |

## Initial release interpretation

The initial product intentionally centers on four projection families:

```text
telemetry
commands
events
telemetry packet specifiers
```

All four are `PARTIAL` because OrbitFabric carries mission-level semantics that are richer than the corresponding FPP declaration fragment. The adapter is expected to report unrepresented source semantics rather than silently discard them or invent F Prime behavior.

## Evidence state

Historical PoC evidence is sufficient to define this initial boundary, including native F Prime generation, build, dictionary conformance and a GDS runtime closed loop against the exact historical baseline.

That historical evidence does **not** make the canonical adapter PASS. The canonical repository must independently re-establish:

1. projection implementation equivalence;
2. Core Integration Result and Coverage behavior;
3. exact F Prime/FPP native generation and build;
4. dictionary conformance;
5. runtime/GDS acceptance where retained;
6. consumer Reference Example acceptance.

Until those gates close, the `Canonical implementation` column remains the authoritative product-readiness qualifier.
