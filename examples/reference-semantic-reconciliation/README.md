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

## Run a clean local greenfield

The permanent CI workflow is the canonical automated proof. The following path is intended for someone who wants to reproduce the same semantic-reconciliation flow personally from clean checkouts and an isolated Python environment.

### Prerequisites

Use a Linux or WSL environment with:

```text
Git
Python 3.12 with venv support
CMake and a normal native C/C++ build toolchain
Java 11 JDK with java available on PATH
```

`syft` is optional for this example. F Prime may warn that SBOM generation is skipped when `syft` is not installed; that does not affect semantic reconciliation.

### 1. Create a clean workspace and clone the exact inputs

```bash
mkdir orbitfabric-fprime-semantic-greenfield
cd orbitfabric-fprime-semantic-greenfield

git clone https://github.com/OrbitFabric/orbitfabric-fprime-adapter.git adapter
git -C adapter checkout v0.1.2

git clone https://github.com/OrbitFabric/orbitfabric.git core
git -C core checkout 4377d6656c62aa1dc19a7ed81d2de872b6b22ccd

git clone --recursive https://github.com/nasa/fprime.git fprime
git -C fprime checkout 8a62e455a90b6d4f498c332d45d65a2a819988d8
git -C fprime submodule update --init --recursive

git clone https://github.com/nasa/fpp.git fpp
git -C fpp checkout 93f484b7521a8e8894cba25b26e633cc87d8e37a

git clone https://github.com/fprime-community/fprime-python-model.git python-model
git -C python-model checkout 934d79ddbe4ad1286e56a5575fed34fb0c44a1bb
```

For development against unreleased adapter source, replace the release tag with the branch or commit you intend to verify. The standalone FPP checkout mirrors the source pin used by CI. The `fpp-to-json` and `fpp-depend` commands used below are installed through the pinned F Prime requirements and must report FPP 3.2.0.

### 2. Create an isolated Python 3.12 environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install build
python -m pip install -r ./fprime/requirements.txt
python -m pip install ./core

(
  cd adapter
  python -m build --wheel
  python -m pip install --force-reinstall dist/*.whl
)

python -m pip install ./python-model
```

Check that the tools come from the clean environment and that the supported FPP lane is active:

```bash
which python
which fprime-util
which fpp-to-json
which fpp-depend

java -version
fpp-to-json --help | head
fpp-depend --help | head

python - <<'PY'
import importlib.metadata as metadata

print("fprime-fpp", metadata.version("fprime-fpp"))
print("fprime-python-model", metadata.version("fprime-python-model"))
print("orbitfabric-fprime-adapter", metadata.version("orbitfabric-fprime-adapter"))

assert metadata.version("fprime-fpp") == "3.2.0"
assert metadata.version("orbitfabric-fprime-adapter") == "0.1.2"
PY
```

Also verify the exact source baselines:

```bash
test "$(git -C adapter describe --tags --exact-match)" = "v0.1.2"
test "$(git -C core rev-parse HEAD)" = "4377d6656c62aa1dc19a7ed81d2de872b6b22ccd"
test "$(git -C fprime rev-parse HEAD)" = "8a62e455a90b6d4f498c332d45d65a2a819988d8"
test "$(git -C fpp rev-parse HEAD)" = "93f484b7521a8e8894cba25b26e633cc87d8e37a"
test "$(git -C python-model rev-parse HEAD)" = "934d79ddbe4ad1286e56a5575fed34fb0c44a1bb"
```

### 3. Produce the two OrbitFabric projections and native F Prime layouts

Run from the greenfield workspace root:

```bash
ROOT="$PWD"
ADAPTER="$ROOT/adapter"
WORK="$ADAPTER/.semantic-reconciliation-work"

cd "$ADAPTER"
rm -rf "$WORK"
mkdir -p "$WORK/semantic/layout-a" "$WORK/semantic/layout-b" "$WORK/evidence"

python examples/reference-contract-evolution/verify_reference_example.py \
  --core-root "$ROOT/core" \
  --work-dir "$WORK/consumer"

for L in a b; do
  python native_acceptance/reference_example/materialize_layout.py \
    --fprime-root "$ROOT/fprime" \
    --projection "$WORK/consumer/layout-$L" \
    --layout "$L" \
    --output-project "$WORK/native-$L"
done
```

### 4. Let F Prime and FPP produce the provider-native semantic models

```bash
for L in a b; do
  pushd "$WORK/native-$L/Ref"

  fprime-util generate -DFPRIME_ENABLE_JSON_MODEL_GENERATION=ON

  cd Top
  DEPENDENCIES=$(fpp-depend ../build-fprime-automatic-native/locs.fpp *.fpp)
  fpp-to-json \
    -d "$WORK/semantic/layout-$L" \
    ${DEPENDENCIES} *.fpp

  popd
done
```

Each semantic directory should now contain:

```text
fpp-ast.json
fpp-loc-map.json
fpp-analysis.json
```

### 5. Reconcile explicit OrbitFabric intent against provider-native observation

```bash
python examples/reference-semantic-reconciliation/verify_semantic_reconciliation.py \
  --layout-a-ast "$WORK/semantic/layout-a/fpp-ast.json" \
  --layout-a-locations "$WORK/semantic/layout-a/fpp-loc-map.json" \
  --layout-a-analysis "$WORK/semantic/layout-a/fpp-analysis.json" \
  --layout-b-ast "$WORK/semantic/layout-b/fpp-ast.json" \
  --layout-b-locations "$WORK/semantic/layout-b/fpp-loc-map.json" \
  --layout-b-analysis "$WORK/semantic/layout-b/fpp-analysis.json" \
  --profile-a examples/reference-contract-evolution/profile-a-monolithic.yaml \
  --profile-b examples/reference-contract-evolution/profile-b-split.yaml \
  --result-a "$WORK/consumer/layout-a/integration_result.json" \
  --result-b "$WORK/consumer/layout-b/integration_result.json" \
  --input-set-manifest "$WORK/consumer/input-set/integration_input_manifest.json" \
  --output "$WORK/evidence/semantic-reconciliation-proof.json"
```

A successful run produces:

```text
.semantic-reconciliation-work/evidence/semantic-reconciliation-proof.json
```

and reports a passing proof with all six stable OrbitFabric source identities reconciled across both layouts.

The proof intentionally keeps:

```text
provider_global_identity_closure = false
```

because FPP 3.2 does not expose the final global dictionary identity through `dictionaryMap`.

### Reproducibility notes

A clean local run should reproduce the semantic result, but three environment-sensitive details should not be mistaken for semantic drift:

1. `input_set_sha256` identifies the exact coherent Core Integration Input Set, not semantic equivalence between independently generated sets. Core surfaces include provenance such as the resolved mission directory, so relocating the same Mission Model can change exact surface bytes and therefore the input-set digest.
2. The proof also retains source and provenance paths. Raw proof bytes can therefore differ across workspace locations even when every semantic reconciliation record is equivalent.
3. `fprime-python-model` derives its package version from Git metadata through `setuptools_scm`. A full tag-aware clone at the pinned commit can report `3.2.0`, while a shallow or tagless checkout can report a development-form version. The authoritative compatibility anchor for this example is the pinned commit `934d79ddbe4ad1286e56a5575fed34fb0c44a1bb`.

These differences do not widen the supported lane and do not change the meaning of a passing semantic reconciliation proof.

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
