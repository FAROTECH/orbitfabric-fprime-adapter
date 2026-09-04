# F Prime Adapter Integration Coverage

Status: **canonical `0.1.0.dev0` implementation and exact-lane native acceptance established; publication and external greenfield acceptance remain before stable `0.1.0`.**

This matrix defines the semantic denominator for the first maintained OrbitFabric F Prime adapter. It records what is meaningful for F Prime, what the first product projects, and where OrbitFabric semantics intentionally remain outside the FPP declaration surface.

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
| Mission identity and source entity identity | Integration Result mappings plus preserved `{domain,id}` source identity | FULL | accepted | Core identity remains authoritative; Reference Example proves stable source identity across two F Prime placements |
| Core Integration Input Set provenance | adapter input/provenance boundary, not an FPP declaration | FULL | accepted | canonical execution verifies the coherent Core Input Set, supported surfaces and digests |
| Telemetry declaration | FPP telemetry declaration inside a project-owned component | PARTIAL | accepted | type, target symbol, local id, update policy and selected numeric limits are projected; mission-level fields remain outside FPP |
| Telemetry primitive type | FPP built-in primitive types | PARTIAL | accepted | bool, unsigned/signed 8/16/32-bit integers and float32/float64 are implemented; enum/string are not claimed |
| Telemetry unit | no equivalent field in the generated FPP telemetry declaration used by this adapter | TARGET_UNSUPPORTED | n/a | preserve in OrbitFabric; do not manufacture a target annotation as equivalent semantics |
| Telemetry limits | FPP yellow/orange/red low/high limits via explicit Profile policy | PARTIAL | accepted | warning/critical vocabulary is not identical to FPP color levels; mapping remains explicit |
| Telemetry sampling / persistence / downlink priority / quality | no direct equivalent in the generated declaration slice | TARGET_UNSUPPORTED | n/a | these remain mission semantics rather than implicit F Prime runtime policy |
| Command declaration | FPP sync/guarded/async command declaration | PARTIAL | accepted | symbol, local opcode, command kind and primitive arguments are projected; broader OrbitFabric command semantics are not |
| Command primitive argument type | FPP built-in primitive parameter types | PARTIAL | accepted | same implemented primitive type subset as telemetry; argument-name validity is checked before rendering |
| Command allowed modes / preconditions / timeout / risk | no direct generic command-declaration equivalent | TARGET_UNSUPPORTED | n/a | must not be converted into hidden runtime behavior |
| Command acknowledgement / expected effects / emitted events | potential runtime or evidence relationships, not equivalent declaration fields | OUT_OF_SCOPE | n/a | require a separate evidence-backed target contract before widening scope |
| Event declaration | FPP event declaration | PARTIAL | accepted | target symbol, local id and explicit F Prime severity are projected; OrbitFabric severity is not assumed equivalent |
| Event severity | Profile-authored F Prime severity | PARTIAL | accepted | F Prime and OrbitFabric severity vocabularies are not treated as one-to-one; target severity is explicit intent |
| Event persistence / downlink priority | no direct equivalent in the generated FPP event declaration | TARGET_UNSUPPORTED | n/a | preserve in OrbitFabric coverage diagnostics |
| Telemetry packet membership | FPP telemetry packet specifier composed inside a project-owned packet set | PARTIAL | accepted | member identity is resolved through projected telemetry; adapter does not own the enclosing topology packet-set policy |
| Packet type / max payload / period | no direct equivalent in the packet specifier fragment | TARGET_UNSUPPORTED | n/a | no implicit scheduling, completeness or payload policy is generated |
| Data products | F Prime records/containers are possible candidates but are not one-to-one with OrbitFabric products | OUT_OF_SCOPE | n/a | explicitly deferred from v0.1.0 |
| Fault / FDIR model | no single generic F Prime declaration equivalent | TARGET_UNSUPPORTED | n/a | a future integration would need concrete F Prime component/runtime semantics, not a guessed mapping |
| OrbitFabric subsystem -> F Prime component | F Prime component architecture is project-owned | NOT_APPLICABLE | n/a | direct inference is explicitly forbidden |
| OrbitFabric mode -> F Prime state machine | F Prime state-machine/runtime architecture is project-owned | NOT_APPLICABLE | n/a | direct inference is explicitly forbidden |
| OrbitFabric relationship -> F Prime topology/port connection | F Prime topology is project-owned | NOT_APPLICABLE | n/a | direct inference is explicitly forbidden |
| F Prime component placement | explicit Profile `host_component` / `host_instance` target intent | FULL | accepted | Reference Example proves placement may change without changing OrbitFabric source identity |
| F Prime local allocation | explicit Profile local id/opcode and packet allocation | FULL | accepted | adapter rejects local collisions before generation; exact-lane native build provides downstream authority |
| Globally resolved F Prime identity | generated F Prime dictionary | FULL | accepted | canonical dictionary conformance consumes downstream-produced identity rather than manufacturing it |

## Initial release interpretation

The initial product intentionally centers on four projection families:

```text
telemetry
commands
events
telemetry packet specifiers
```

All four remain `PARTIAL` because OrbitFabric carries mission-level semantics that are richer than the corresponding FPP declaration fragment. The adapter reports unrepresented source semantics rather than silently discarding them or inventing F Prime behavior.

## Evidence state

The canonical repository has independently established:

1. projection implementation and regression coverage;
2. Core Integration Input Set consumption, Integration Result and execution-backed Coverage;
3. exact F Prime v4.2.2 / FPP 3.2.0 generation and build;
4. generated dictionary conformance and resolved target identity;
5. GDS runtime closed-loop acceptance through projected command, telemetry, event and command completion;
6. consumer Reference Example acceptance with one stable OrbitFabric contract across two F Prime placements;
7. managed Adapter Manager lifecycle and provider-neutral release proof.

Publication of immutable release bytes and external greenfield acceptance are deliberately tracked as later release gates and are not implied by this matrix.
