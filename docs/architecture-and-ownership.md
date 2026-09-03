# Architecture and ownership

The adapter exists at a deliberate boundary between OrbitFabric mission semantics and F Prime project semantics.

## OrbitFabric owns

- mission-level entities and canonical `{domain, id}` identity;
- Core Integration Input Set contracts;
- generic adapter execution and Integration Result contracts;
- Adapter Manager lifecycle behavior.

## The F Prime adapter owns

- target-specific FPP projection;
- explicit source-to-target binding;
- FPP-safe target symbols and target-local allocations;
- target-specific diagnostics and coverage;
- validation of adapter assumptions against F Prime-produced evidence.

## F Prime owns

- component definitions and instances;
- topology and port wiring;
- scheduling, rate groups, threads and queues;
- FPP interpretation and autocoding;
- globally resolved command, event and telemetry identity;
- generated dictionaries;
- native build and runtime behavior.

## Non-inference rule

The adapter must not manufacture generic mappings such as:

```text
OrbitFabric subsystem     -> F Prime component
OrbitFabric relationship  -> F Prime topology connection
OrbitFabric mode          -> F Prime state machine
```

Target placement belongs to explicit adapter configuration, not to hidden interpretation of mission semantics.

## Evidence boundary

Adapter-generated FPP and OrbitFabric Integration Results are product artifacts.

F Prime-generated dictionaries, native build outcomes and runtime observations are downstream evidence. The adapter may validate and preserve that evidence, but it does not become the authority that produced it.
