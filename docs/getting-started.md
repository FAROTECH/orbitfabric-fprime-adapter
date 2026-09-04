# Getting Started

This guide is for **users of the adapter**.

It covers the normal consumer path:

```text
install OrbitFabric Core
    -> obtain the published adapter release
    -> verify the published bytes
    -> install through Adapter Manager
    -> verify the installed instance
    -> generate a Core Integration Input Set
    -> execute fpp_contract_projection
```

You do **not** need to install this repository in editable mode, build a wheel or use publisher tooling.

If you want to modify the adapter, use [Development and verification](development.md).

## Published release

`v0.1.0` is the first stable published release.

It has passed:

- published-byte verification;
- clean external greenfield installation and execution;
- consumer Reference Example acceptance;
- exact-lane native F Prime generate/build/dictionary acceptance;
- canonical GDS closed-loop runtime acceptance.

The validated downstream lane is exact:

| System | Validated baseline |
| --- | --- |
| OrbitFabric Core | `4377d6656c62aa1dc19a7ed81d2de872b6b22ccd` |
| F Prime | `v4.2.2`, commit `8a62e455a90b6d4f498c332d45d65a2a819988d8` |
| FPP | `3.2.0`, commit `93f484b7521a8e8894cba25b26e633cc87d8e37a` |

No broader F Prime or FPP compatibility range is currently claimed.

## 1. Create a clean consumer environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
```

For an isolated Adapter Manager state directory:

```bash
export ORBITFABRIC_STATE_DIR="$PWD/.orbitfabric-state"
```

## 2. Install the validated OrbitFabric Core baseline

```bash
python -m pip install \
  "git+https://github.com/FAROTECH/orbitfabric.git@4377d6656c62aa1dc19a7ed81d2de872b6b22ccd"
```

Check that Core and Adapter Manager are available:

```bash
orbitfabric --help
orbitfabric adapter list
```

## 3. Obtain the published adapter release assets

Download these exact assets from the [GitHub Release v0.1.0](https://github.com/FAROTECH/orbitfabric-fprime-adapter/releases/tag/v0.1.0):

```text
orbitfabric_fprime_adapter-0.1.0-py3-none-any.whl
adapter-release.json
SHA256SUMS
```

Keep them together in one directory and verify the downloaded bytes:

```bash
sha256sum -c SHA256SUMS
```

A normal consumer should use the published wheel rather than rebuilding it from repository source.

## 4. Install through OrbitFabric Adapter Manager

From the directory containing the release assets:

```bash
orbitfabric adapter install \
  adapter-release.json \
  --artifact orbitfabric_fprime_adapter-0.1.0-py3-none-any.whl
```

Inspect the installed inventory:

```bash
orbitfabric adapter list
orbitfabric adapter list --json
```

Record the returned instance ID:

```bash
export ORBITFABRIC_ADAPTER_INSTANCE_ID=<instance-id>
```

Verify the managed installation:

```bash
orbitfabric adapter inspect "$ORBITFABRIC_ADAPTER_INSTANCE_ID"
orbitfabric adapter verify "$ORBITFABRIC_ADAPTER_INSTANCE_ID"
```

A valid installation must finish with:

```text
Result: PASSED
```

## 5. Produce a Core Integration Input Set

The adapter consumes a coherent Core Integration Input Set rather than Mission Model YAML as a private adapter API.

```bash
orbitfabric export integration-input-set \
  <mission-directory> \
  --output-dir <core-input-directory>
```

The handoff manifest is:

```text
<core-input-directory>/integration_input_manifest.json
```

## 6. Execute `fpp_contract_projection`

Provide an explicit F Prime Projection Profile describing target placement and local allocation choices:

```bash
orbitfabric adapter execute "$ORBITFABRIC_ADAPTER_INSTANCE_ID" \
  --operation fpp_contract_projection \
  --input-set-manifest <core-input-directory>/integration_input_manifest.json \
  --profile <fprime-profile.yaml> \
  --output-dir <output-directory>
```

Representative outputs are:

```text
components/<component>/OF_Commands.fppi
components/<component>/OF_Events.fppi
components/<component>/OF_Telemetry.fppi
topology/<packet-set>/OF_Packets.fppi
integration_result.json
```

The generated FPP files are declaration fragments for explicit composition inside an existing F Prime project. The adapter does not generate the F Prime project, component architecture or topology.

## 7. Try the Reference Example

The best first evaluation path is the [Reference Example](reference-example.md).

It keeps one OrbitFabric mission contract stable while changing explicit downstream placement from a monolithic F Prime component layout to a split controller/monitor layout.

The example proves that:

- OrbitFabric source identities remain unchanged;
- target placement changes only where the Profile changes;
- packet membership follows telemetry placement;
- both layouts generate and build as native F Prime projects;
- generated dictionaries resolve the projected downstream identities.

For a released version, use the matching `v0.1.0` source archive only to access the Reference Example files and runner scripts. Keep the adapter product itself installed from the published release wheel.

## Where to go next

As a user:

- [Reference Example](reference-example.md)
- [F Prime Projection Profile](projection-profile.md)
- [Core input and result boundary](core-input-and-result.md)
- [Integration Coverage](integration-coverage.md)

If you are changing the source:

- [Development and verification](development.md)

For the exact downstream evidence boundary:

- [Target compatibility](target-compatibility.md)
