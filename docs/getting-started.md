# Getting Started

This is the coordinated **unpublished** Core 1.4.0 / GitHub Release Source 0.1.0 / F Prime 0.1.3 candidate. The commands below become public acceptance commands only after approved publication and the exact F Prime descriptor digest is added to the canonical Catalog. No PyPI publication is assumed.

## Install the candidate after approved publication

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -r https://github.com/OrbitFabric/orbitfabric/releases/download/v1.4.0/orbitfabric-install.txt
orbitfabric adapter install fprime --version 0.1.3
orbitfabric adapter list
orbitfabric adapter verify <instance-id>
```

The installation manifest names exact Core and GitHub Release Source wheels with SHA-256 URL fragments. Runtime Python dependencies are resolved by pip. Neither repository clones nor Git are required. Adapter descriptor and artifact downloads are automatic. No Project Lock is needed for this path.

```bash
orbitfabric adapter install orbitfabric/fprime --version 0.1.3
orbitfabric adapter install github.com/OrbitFabric:orbitfabric/fprime --version 0.1.3
orbitfabric adapter install fprime --version 0.1.3 --catalog-revision <40-character-commit-sha>
orbitfabric adapter install fprime --version 0.1.3 --catalog ./catalog.json --json
```

The default Catalog repository is `OrbitFabric/orbitfabric-adapter-catalog`. Each invocation resolves `main` to an exact commit, fetches `catalog.json` at that commit, validates it and reports repository, revision, path and byte SHA-256. A pinned revision skips mutable-ref resolution. A local snapshot makes no Catalog network request and reports its absolute path and digest. The two overrides are mutually exclusive. There is no persistent cache, refresh timer or fallback to another snapshot.

Logical selection filters by both key and exact version across Catalog records before counting matches. One match succeeds; zero or multiple matches fail closed. Bare names also require uniqueness across publishers. `openc3-cosmos --version 0.2.0` selects `github.com/OrbitFabric:orbitfabric/openc3-cosmos@0.2.0`; historical FAROTECH 0.1.0 is retained without causing ambiguity. There are no authority aliases, preferred authorities, version ranges, latest, stable or automatic upgrades. The full coordinate and exact version remain the installed identity.

Core application composition calls `GitHubReleaseSource.resolve(...)`, then `AdapterManager.install_resolved(...)`. The provider verifies the Catalog-bound descriptor digest, exact identity/version and selected artifact digest/size. Core owns acceptance, managed environment installation, inventory and verification. GitHub transport stays outside the lifecycle layer. Only one GitHub Release binding is supported for this command; no provider registry or mirror preference is introduced.

Remote `--json` output contains `installed` and `catalog_snapshot`. Existing local JSON output remains the installed record. The old explicit path remains available:

```bash
orbitfabric adapter install ./adapter-release.json --artifact ./adapter.whl
```

Project Locks remain exact reproducible project desired state. Existing ensure MATCH returns NOOP without acquisition. Snapshot provenance describes Catalog bytes; it does not turn Catalog membership into publisher authentication.


## Execution with reference inputs

The following execution guidance preserves the validated downstream F Prime/FPP baseline.

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

## 7. Try the Reference Examples

The best evaluation path is [Reference Examples](reference-example.md).

The first example keeps one OrbitFabric mission contract stable while changing explicit downstream placement from a monolithic F Prime component layout to a split controller/monitor layout.

The second reconciles the explicit projected intent against provider-native FPP semantics and source provenance.

Together they prove that:

- OrbitFabric source identities remain unchanged;
- target placement changes only where the Profile changes;
- packet membership follows telemetry placement;
- both layouts generate and build as native F Prime projects;
- generated dictionaries resolve the projected downstream identities;
- provider-native FPP semantic observation agrees with the explicit Projection Profile and Integration Result intent.

For a released version, use the matching `v0.1.2` source archive or checkout to access the Reference Example files and runner scripts. Keep the adapter product itself installed from the published release wheel.

## Where to go next

As a user:

- [Reference Examples](reference-example.md)
- [F Prime Projection Profile](projection-profile.md)
- [Core input and result boundary](core-input-and-result.md)
- [Integration Coverage](integration-coverage.md)

If you are changing the source:

- [Development and verification](development.md)

For the exact downstream evidence boundary:

- [Target compatibility](target-compatibility.md)
