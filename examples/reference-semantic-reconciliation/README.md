# Reference Example: Provider-Native Semantic Reconciliation

This example demonstrates a different property from the existing [Reference Example: Stable Mission Contract, Evolving F Prime Architecture](../reference-contract-evolution/README.md).

The first example asks:

```text
Can the native F Prime architecture evolve while OrbitFabric mission identity stays stable?
```

This example asks:

```text
Did the provider-native FPP semantic model actually understand
our explicit projection intent the way we expected?
```

The proof path is:

```text
OrbitFabric mission contract
    -> explicit F Prime Projection Profile
    -> adapter FPP projection
    -> project-owned native FPP composition
    -> fpp-to-json
    -> fprime-python-model
    -> semantic reconciliation
    -> semantic-reconciliation-proof.json
```

The important boundary is that OrbitFabric and FPP remain separate semantic authorities.

```text
OrbitFabric
    owns mission-level source identity and semantics

F Prime / FPP
    owns native components, instances, topology, semantic interpretation,
    generated dictionary identity and runtime behavior

this example
    compares explicit OrbitFabric-to-target intent with provider-native observation
```

It does not reconstruct an OrbitFabric Mission Model from FPP and it does not infer F Prime architecture from OrbitFabric semantics.

## Same mission, same Profiles, different question

The example deliberately reuses the exact mission and Profiles from `reference-contract-evolution`:

```text
Core demo-3u mission
    + Profile A: monolithic payload placement
    + Profile B: split controller / monitor placement
```

This avoids creating a second synthetic story merely to demonstrate the semantic-observation layer.

The projected OrbitFabric sources are:

```text
telemetry  payload.acquisition.active
command    payload.start_acquisition
command    payload.stop_acquisition
event      payload.acquisition_started
event      payload.acquisition_stopped
packet     payload_status
```

The same OrbitFabric source identities are reconciled in both layouts.

## What gets reconciled

For commands, events and telemetry the verifier combines:

```text
Integration Result source -> target mapping
    + explicit Profile binding
    + FPP semantic component
    + FPP semantic instance
    + local opcode / local ID
    + FPP symbol
    + source location / include provenance
```

For the packet it combines:

```text
Integration Result packet target
    + explicit packet Profile binding
    + FPP telemetry packet AST node
    + packet ID / group
    + provider-observed telemetry membership
    + generated OF_Packets.fppi provenance
```

The correlation is exact. There is no fuzzy matching and no heuristic selection between ambiguous candidates.

## What the proof means

A passing proof means:

> The provider-native FPP model resolved the projected declarations in the component, instance, local allocation and packet relationships explicitly requested by the Projection Profile, and the observed semantic entities retain provenance back to the adapter-generated FPP fragments.

This is deliberately narrower than saying that the whole F Prime application is correct.

Other evidence layers keep their own roles:

```text
generated FPP fragments
    show what the adapter emitted

semantic reconciliation
    shows what the provider-native FPP model understood

generated F Prime dictionary
    shows final provider-resolved operational identities

native build / GDS
    show downstream build and selected runtime behavior
```

The layers complement one another rather than replacing one another.

## Supported lane

The public example intentionally stays on the adapter's existing validated lane:

```text
F Prime  v4.2.2  @ 8a62e455a90b6d4f498c332d45d65a2a819988d8
FPP      3.2.0   @ 93f484b7521a8e8894cba25b26e633cc87d8e37a
```

The semantic consumer is pinned in CI to:

```text
fprime-community/fprime-python-model
v3.2.0 commit 934d79ddbe4ad1286e56a5575fed34fb0c44a1bb
```

That consumer requires Python 3.12. This is an example/evidence tooling requirement, not a new runtime requirement for `orbitfabric-fprime-adapter`.

## Why the proof stops before global F Prime IDs

FPP 3.2 semantic output does not expose `dictionaryMap`.

Therefore this example proves:

```text
OrbitFabric source identity
    -> explicit target intent
    -> native FPP semantic entity
    -> component / instance / local allocation
    -> generated-source provenance
```

but it does not claim that `fpp-to-json` 3.2 alone closes the final provider-resolved global dictionary identity.

That final identity remains covered by the adapter's existing generated-dictionary acceptance.

FPP 3.3 adds a materially stronger `dictionaryMap` capability, but it also belongs to a different F Prime/FPP semantic compatibility lane. The adapter does not widen its supported target versions through this example.

## Run the proof

The permanent CI job performs the complete path. Conceptually it does the following.

First produce the normal Reference Example projections:

```bash
python examples/reference-contract-evolution/verify_reference_example.py \
  --core-root /path/to/orbitfabric \
  --work-dir /tmp/of-fprime-semantic/consumer
```

Then materialize both project-owned F Prime layouts using the existing native Reference Example harness, enable FPP JSON model generation, and export each provider semantic model with `fpp-to-json`.

Finally run:

```bash
python examples/reference-semantic-reconciliation/verify_semantic_reconciliation.py \
  --layout-a-ast /tmp/of-fprime-semantic/semantic/layout-a/fpp-ast.json \
  --layout-a-locations /tmp/of-fprime-semantic/semantic/layout-a/fpp-loc-map.json \
  --layout-a-analysis /tmp/of-fprime-semantic/semantic/layout-a/fpp-analysis.json \
  --layout-b-ast /tmp/of-fprime-semantic/semantic/layout-b/fpp-ast.json \
  --layout-b-locations /tmp/of-fprime-semantic/semantic/layout-b/fpp-loc-map.json \
  --layout-b-analysis /tmp/of-fprime-semantic/semantic/layout-b/fpp-analysis.json \
  --profile-a examples/reference-contract-evolution/profile-a-monolithic.yaml \
  --profile-b examples/reference-contract-evolution/profile-b-split.yaml \
  --result-a /tmp/of-fprime-semantic/consumer/layout-a/integration_result.json \
  --result-b /tmp/of-fprime-semantic/consumer/layout-b/integration_result.json \
  --input-set-manifest /tmp/of-fprime-semantic/consumer/input-set/integration_input_manifest.json \
  --output /tmp/of-fprime-semantic/semantic-reconciliation-proof.json
```

The machine-readable output is:

```text
semantic-reconciliation-proof.json
```

This artifact is example-owned evidence. It is not a stable adapter API and it is not an OrbitFabric Core contract.

## Two layouts, two observed native placements

The proof requires both layouts to reconcile independently.

### Layout A

```text
Reference.PayloadComponent
    instance payload

    OF_StartAcquisition
    OF_StopAcquisition
    OF_AcquisitionStarted
    OF_AcquisitionStopped
    OF_AcquisitionActive
```

### Layout B

```text
Reference.PayloadController
    instance payloadController

    OF_StartAcquisition
    OF_StopAcquisition
    OF_AcquisitionStarted
    OF_AcquisitionStopped

Reference.PayloadMonitor
    instance payloadMonitor

    OF_AcquisitionActive
```

The packet membership must also move from:

```text
payload.OF_AcquisitionActive
```

to:

```text
payloadMonitor.OF_AcquisitionActive
```

while the OrbitFabric source identity `payload.acquisition.active` remains unchanged.

## Relationship to the other Reference Example

The two examples are complementary executable architectural stories.

| Example | Main question | Direction | Property demonstrated |
| --- | --- | --- | --- |
| `reference-contract-evolution` | Can F Prime architecture evolve independently? | OrbitFabric -> F Prime | architectural decoupling |
| `reference-semantic-reconciliation` | Did FPP interpret the projected intent as expected? | OrbitFabric -> F Prime -> observation | traceability and semantic conformance |

Together they demonstrate that OrbitFabric can stay upstream of provider architecture while still producing precise, reviewable and verifiable integration evidence.
