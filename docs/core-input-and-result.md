# Core Input and Integration Result Boundary

The canonical adapter consumes OrbitFabric through the public Core Integration Input Set contract.

It does not read Mission Model YAML directly and it does not depend on private OrbitFabric Python APIs for mission semantics.

## Required Core surfaces

The first operation requires the coherent input-set manifest plus these Core-owned surfaces:

```text
mission_snapshot
entity_index
relationship_manifest
lint_report
```

`model_summary` remains the canonical companion surface. Its absence does not by itself block projection.

The supported compatibility identifiers are:

```text
Integration Input Set      0.1-candidate
entity_index               0.1
lint_report                v1
mission_snapshot           0.1-candidate
model_summary              0.1
relationship_manifest      0.1-candidate
```

## Input integrity gates

Before projection, the adapter verifies:

1. the Integration Input Set kind and version;
2. `load_result = loaded`;
3. lint state is `passed` or `passed_with_warnings`;
4. the canonical role inventory is complete;
5. required surface availability;
6. role, kind and format-version compatibility;
7. the Core `input_set_sha256` using RFC 8785 JSON Canonicalization Scheme bytes;
8. every available surface SHA-256;
9. safe relative surface paths that remain inside the input-set root;
10. required surface identity after loading;
11. every Profile source resolves in the Core Entity Index.

There is no raw-YAML fallback when one of these gates fails.

## Projection input

After Core input validation, the adapter passes only the loaded Mission Snapshot model plus the validated F Prime Projection Profile to the pure projection engine.

This preserves the separation introduced by PR 3:

```text
Core contract loading and integrity
        -> execution layer

FPP projection semantics
        -> pure projection engine
```

The execution layer does not reinterpret FPP semantics and the projection engine does not know how the Core bundle is stored on disk.

## Integration Result

A successful run writes `integration_result.json` last, after all FPP artifacts have been generated.

The Result records:

- adapter, integration and operation identity;
- Mission identity copied from the Core Input Set;
- exact Core Input Set digest;
- exact consumed Profile digest;
- exercised capabilities;
- generated artifact paths and SHA-256 values;
- OrbitFabric source to F Prime target mappings;
- integration-owned diagnostics for represented gaps;
- execution-backed projection coverage;
- input-integrity and Profile-validation evidence records.

The Result uses generic target references with namespace `fprime`. Generic OrbitFabric consumers must treat the target id as opaque.

## Coverage meaning

For a successful projection operation, `coverage.status` is `complete` because the Result contains coverage records for the entire set of mappings exercised by that run.

This does not mean the OrbitFabric semantics are fully represented in FPP.

Each current mapping record therefore carries:

```text
semantic_disposition: PARTIAL
```

and lists source fields that were present but are not represented by the first FPP contract-projection surface.

This keeps two questions separate:

```text
Is execution coverage recorded completely?

Does FPP represent the entire source semantic object?
```

The first can be true while the second remains partial.

## Failure behavior

When execution fails and the output directory remains writable, the CLI writes a failed Integration Result on a best-effort basis.

Failed Results do not invent Core or Profile provenance. Unknown provenance fields remain null and the integration-owned error explains the failure.

## What PR 4 still does not prove

This boundary does not invoke F Prime or FPP tooling.

Therefore it does not yet establish:

- FPP parser acceptance;
- `fprime-util generate` acceptance;
- F Prime build acceptance;
- generated dictionary conformance;
- resolved downstream ids;
- F Prime runtime or GDS behavior.

Those facts must come from the exact downstream toolchain in the native acceptance gates.
