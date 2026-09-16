# Examples

This directory contains the public, executable integration stories for the OrbitFabric F Prime Adapter.

The examples are intentionally small at the contract level. They focus on the question being demonstrated, while native F Prime project materialization and downstream acceptance harnesses live under [`native_acceptance/`](../native_acceptance/README.md).

## Reference Example: contract evolution

[`reference-contract-evolution/`](reference-contract-evolution/README.md) demonstrates that one stable OrbitFabric mission contract can be projected into two different explicit F Prime placements.

```text
same OrbitFabric mission contract
    -> Profile A -> monolithic F Prime placement
    -> Profile B -> split F Prime placement
```

The example directory contains the two Projection Profiles and the consumer proof. The corresponding native F Prime materializer and full generate/build/dictionary acceptance runner live under [`native_acceptance/reference_example/`](../native_acceptance/reference_example/).

## Reference Example: semantic reconciliation

[`reference-semantic-reconciliation/`](reference-semantic-reconciliation/README.md) demonstrates provider-native traceability after projection.

```text
OrbitFabric intent
    -> adapter projection
    -> native FPP composition
    -> FPP semantic observation
    -> reconciliation evidence
```

It uses the same mission contract and Profiles as the contract-evolution example, then reconciles them against the provider-native FPP semantic model.

## Which example should I start with?

Start with **contract evolution** if you want to understand the architectural value of keeping mission identity stable while the F Prime implementation changes.

Continue with **semantic reconciliation** if you want to see how the projected intent is checked against what FPP actually understood.
