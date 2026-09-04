# Target compatibility

The first stable F Prime adapter release claims one exact downstream lane.

## Accepted lane

```text
F Prime
  version: v4.2.2
  commit:  8a62e455a90b6d4f498c332d45d65a2a819988d8

FPP
  version: 3.2.0
  commit:  93f484b7521a8e8894cba25b26e633cc87d8e37a
```

The same information is packaged in machine-readable form at:

```text
orbitfabric_fprime_adapter/compatibility/fprime-v4.2.2-fpp-3.2.0.json
```

## Canonical evidence status

Canonical CI has observed:

```text
adapter wheel installation
-> fpp_contract_projection
-> generated FPP fragments
-> fprime-util generate
-> fprime-util build
-> generated F Prime dictionary conformance
-> fprime-gds
-> projected command
-> projected telemetry + projected event
-> command completion
```

The live runtime acceptance uses an evidence-only Ref fixture. It sends:

```text
Ref.pingRcvr.OF_SetMode(mode=2)
```

and observes:

```text
Ref.pingRcvr.OF_Temperature = 22.0
Ref.pingRcvr.OF_ModeChanged
command completion = OK
```

The synthetic mode-to-temperature behavior belongs only to the acceptance fixture. It is not OrbitFabric mission semantics and is not generated runtime behavior owned by the adapter.

The Reference Example adds a separate native architecture-evolution proof. One stable Core Integration Input Set is projected through two explicit F Prime Profiles. Both monolithic and split placements pass native F Prime generation and build, both generated dictionaries resolve the projected entities, packet membership follows telemetry placement, and the OrbitFabric source identity set remains unchanged while F Prime resolved identity evolves with the Profile.

## Release and greenfield status

`v0.1.0` is published as a stable GitHub Release. The published release assets have passed published-byte verification and clean external greenfield installation/execution.

The greenfield native acceptance independently re-established the exact F Prime and FPP source commits above, generated and built both Reference Example layouts, and verified the resulting dictionaries.

## Version policy for v0.1.0

No compatibility range is claimed.

The stable `0.1.0` release claims only the exact pair above. Forward compatibility, backward compatibility and other F Prime/FPP combinations remain unclaimed until separately evidenced.

Changing the pinned downstream baseline is therefore an evidence change, not a documentation-only change.
