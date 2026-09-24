# Reference Example: Stable Mission Contract, Evolving F Prime Architecture

This example demonstrates why an OrbitFabric mission contract can be useful upstream of a native F Prime project.

The central property is simple:

```text
same OrbitFabric mission contract
    -> Profile A
    -> monolithic F Prime placement

same OrbitFabric mission contract
    -> Profile B
    -> split F Prime placement
```

The OrbitFabric entity identities do not change. The F Prime architecture is free to evolve.

This example is part of the accepted `0.1` product surface. Both layouts have passed native F Prime generation, build and generated dictionary verification against the exact supported F Prime/FPP lane.

## Where the example lives

The public example is intentionally split by responsibility:

```text
examples/reference-contract-evolution/
    README.md
    profile-a-monolithic.yaml
    profile-b-split.yaml
    verify_reference_example.py

native_acceptance/reference_example/
    materialize_layout.py
    run_native.sh
    verify_native_layouts.py
```

The `examples/` side contains the story, explicit Projection Profiles and consumer proof. The `native_acceptance/` side materializes those projections into real F Prime projects and runs provider-native generate, build and dictionary verification.

This separation keeps the example readable without hiding the concrete F Prime acceptance path.

## Upstream contract

The example deliberately uses the `demo-3u` reference mission from the exact OrbitFabric Core baseline accepted by this adapter:

```text
4377d6656c62aa1dc19a7ed81d2de872b6b22ccd
```

Core produces one coherent Integration Input Set from that mission.

The example projects these stable OrbitFabric entities:

```text
telemetry  payload.acquisition.active
command    payload.start_acquisition
command    payload.stop_acquisition
event      payload.acquisition_started
event      payload.acquisition_stopped
packet     payload_status
```

OrbitFabric remains authoritative for those mission-level identities and their source semantics.

## Layout A: prototype architecture

Profile A represents an early project architecture where payload command, event and telemetry declarations are hosted by one component:

```text
Reference.PayloadComponent
    instance: payload

    OF_StartAcquisition
    OF_StopAcquisition
    OF_AcquisitionStarted
    OF_AcquisitionStopped
    OF_AcquisitionActive
```

The generated packet specifier refers to:

```text
payload.OF_AcquisitionActive
```

## Layout B: evolved architecture

Profile B represents a later project architecture where control and monitoring responsibilities are split:

```text
Reference.PayloadController
    instance: payloadController

    OF_StartAcquisition
    OF_StopAcquisition
    OF_AcquisitionStarted
    OF_AcquisitionStopped

Reference.PayloadMonitor
    instance: payloadMonitor

    OF_AcquisitionActive
```

The generated packet specifier now refers to:

```text
payloadMonitor.OF_AcquisitionActive
```

No OrbitFabric mission entity is renamed or redefined to make that F Prime refactoring possible.

## What changes and what stays stable

| Concern | Layout A | Layout B | Owner |
| --- | --- | --- | --- |
| `payload.acquisition.active` | stable | stable | OrbitFabric |
| `payload.start_acquisition` | stable | stable | OrbitFabric |
| `payload.stop_acquisition` | stable | stable | OrbitFabric |
| F Prime host component | `Reference.PayloadComponent` | `Reference.PayloadController` or `Reference.PayloadMonitor` | F Prime project + Profile |
| F Prime instance | `payload` | `payloadController` or `payloadMonitor` | F Prime project + Profile |
| FPP symbol | explicit | explicit | Profile |
| F Prime topology | project-owned | project-owned | F Prime project |
| scheduling and runtime behavior | project-owned | project-owned | F Prime project |

The adapter does not infer a component architecture from OrbitFabric subsystems. The two layouts are explicit engineering choices expressed by two Projection Profiles.

## Run the consumer proof

Install the released adapter product and the exact Core baseline, then obtain the matching `v0.1.2` repository source for the example files and execute:

```bash
python examples/reference-contract-evolution/verify_reference_example.py \
  --core-root /path/to/orbitfabric \
  --work-dir /tmp/orbitfabric-fprime-reference-example
```

The script performs this path:

```text
Core demo-3u Mission Model
    -> orbitfabric export integration-input-set
    -> one Core Integration Input Set
    -> Profile A
    -> installed orbitfabric-fprime product
    -> Layout A FPP + Integration Result

same Core Integration Input Set
    -> Profile B
    -> installed orbitfabric-fprime product
    -> Layout B FPP + Integration Result
```

It fails unless all of these properties are observed:

1. Both projections succeed.
2. Mission identity is identical in both Integration Results.
3. The Core Integration Input Set digest is identical inside the run.
4. The projected OrbitFabric source identity set is identical.
5. F Prime placement changes exactly where the profiles say it should.
6. Packet membership follows the new telemetry placement.
7. Coverage remains explicit and complete for the exercised mappings.
8. Profile-owned target choices remain recorded with `origin: profile`.

The script writes a machine-readable proof:

```text
reference-example-proof.json
```

## Run the full native example locally

The permanent CI workflow is the canonical automated acceptance. The repository also includes one runner for users who want to reproduce the complete two-layout proof from clean checkouts.

### Prerequisites

Use a Linux or WSL environment with:

```text
Git
Python 3.12 with venv support
CMake and a native C/C++ build toolchain
Java 11 JDK with java available on PATH
```

`syft` is optional. F Prime may report that SBOM generation is skipped when `syft` is not installed. That warning does not affect this example.

### 1. Create clean checkouts

```bash
mkdir orbitfabric-fprime-contract-greenfield
cd orbitfabric-fprime-contract-greenfield

git clone https://github.com/OrbitFabric/orbitfabric-fprime-adapter.git adapter
git clone https://github.com/OrbitFabric/orbitfabric.git core
git clone --recursive https://github.com/nasa/fprime.git fprime
git clone https://github.com/nasa/fpp.git fpp

git -C adapter checkout v0.1.2
git -C core checkout 4377d6656c62aa1dc19a7ed81d2de872b6b22ccd
git -C fprime checkout 8a62e455a90b6d4f498c332d45d65a2a819988d8
git -C fprime submodule update --init --recursive
git -C fpp checkout 93f484b7521a8e8894cba25b26e633cc87d8e37a
```

For development against unreleased source, the adapter checkout may instead stay on the intended branch or commit. For release reproduction, use the exact release tag.

### 2. Create an isolated Python environment

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
```

Check the important package versions:

```bash
python - <<'PY'
import importlib.metadata as metadata

print("orbitfabric", metadata.version("orbitfabric"))
print("orbitfabric-fprime-adapter", metadata.version("orbitfabric-fprime-adapter"))
print("fprime-fpp", metadata.version("fprime-fpp"))

assert metadata.version("orbitfabric-fprime-adapter") == "0.1.2"
assert metadata.version("fprime-fpp") == "3.2.0"
PY
```

### 3. Run the complete native proof

From the greenfield workspace root:

```bash
ROOT="$PWD"

./adapter/native_acceptance/reference_example/run_native.sh \
  "$ROOT/fprime" \
  "$ROOT/fpp" \
  "$ROOT/core"
```

A successful run ends with:

```text
PASS: Reference Example native two-layout acceptance
```

and writes evidence under:

```text
adapter/.reference-example-native-work/evidence/
    layout-a-dictionary.json
    layout-b-dictionary.json
    reference-example-native-acceptance.json
```

The final acceptance requires both native generate/build paths to pass, both dictionaries to resolve the projected command, event, telemetry and packet identities, the OrbitFabric source identity set to remain stable, F Prime resolved placement to evolve with the Profile, and packet membership to follow the telemetry placement.

### Reproducibility note

`core_input_set_sha256` identifies the exact generated Core Integration Input Set. Core surfaces retain provenance such as resolved source paths, so the digest can differ across independent workspace locations even when the mission semantics are equivalent. The proof inside one run still requires Layout A and Layout B to consume the same exact input set.

## Native F Prime acceptance

The validated downstream lane is exact:

```text
F Prime  v4.2.2  @ 8a62e455a90b6d4f498c332d45d65a2a819988d8
FPP      3.2.0   @ 93f484b7521a8e8894cba25b26e633cc87d8e37a
```

The canonical acceptance path performs:

```text
OrbitFabric Integration Input Set
    -> adapter projection
    -> FPP fragments
    -> explicit composition in repo-owned Reference components/topology
    -> fprime-util generate
    -> fprime-util build
    -> generated F Prime dictionary
    -> native two-layout verification
```

This native proof is a permanent CI gate for the adapter.

## Relationship to semantic reconciliation

This example answers:

> Can the native F Prime architecture evolve while OrbitFabric mission identity stays stable?

The complementary [`reference-semantic-reconciliation`](../reference-semantic-reconciliation/README.md) example answers:

> Did the provider-native FPP semantic model interpret the explicit projected intent as expected?

Together they show architectural decoupling and provider-native traceability on the same supported lane.

## Why this matters to an F Prime user

This example is not intended to show that OrbitFabric can replace FPP or model an F Prime topology.

It shows a different value:

> Keep mission-level contract identity stable while allowing the native F Prime implementation architecture to evolve independently.

F Prime remains the downstream authority for components, instances, topology, FPP interpretation, build behavior, generated dictionary identity and runtime semantics.

The adapter provides an explicit and reviewable bridge between the stable mission contract and those native project choices.
