# Native Acceptance

This directory contains provider-native acceptance harnesses for the OrbitFabric F Prime Adapter.

The product itself lives under `src/`. Public integration stories live under [`examples/`](../examples/README.md). This directory takes selected projected artifacts into real F Prime projects and asks the downstream toolchain to resolve, generate, build and, where applicable, execute them.

## Reference Example native acceptance

[`reference_example/`](reference_example/) is the native realization of [`examples/reference-contract-evolution`](../examples/reference-contract-evolution/README.md).

Its main entry point is:

```bash
native_acceptance/reference_example/run_native.sh \
  /path/to/fprime \
  /path/to/fpp \
  /path/to/orbitfabric-core
```

The runner:

```text
creates one Core Integration Input Set
    -> projects Profile A and Profile B
    -> materializes two native F Prime projects
    -> runs fprime-util generate
    -> runs fprime-util build
    -> collects generated dictionaries
    -> verifies stable OrbitFabric identity and evolved F Prime resolution
```

See the [Reference Example README](../examples/reference-contract-evolution/README.md) for the clean local reproduction path and exact supported pins.

## Other acceptance harnesses

The remaining scripts exercise additional product evidence layers, including native static conformance and the F Prime GDS closed-loop runtime path.

These harnesses support product verification. They are not additional adapter operations and do not widen the documented compatibility lane.
