# Target compatibility

The first F Prime adapter release starts from one exact downstream candidate lane.

## Candidate lane

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

## Current evidence status

This pair has strong historical PoC evidence, including native generation, native build, F Prime dictionary conformance and a GDS runtime closed loop.

The canonical adapter has **not yet** re-established those target-native results. Its packaged compatibility declaration therefore uses:

```text
status: historical_evidence_candidate
canonical_source_acceptance: pending
canonical_native_acceptance_gate: PR5
```

This distinction is deliberate. Historical evidence justifies selecting the lane; it does not justify claiming that the new product source has already passed it.

## Version policy for v0.1.0

No compatibility range is claimed.

The first stable release must prove the exact pair above against the exact canonical source candidate that will be released. Forward and backward compatibility remain unclaimed until separately evidenced.
