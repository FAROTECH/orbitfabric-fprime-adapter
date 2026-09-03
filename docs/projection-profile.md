# F Prime Projection Profile

The Profile records target projection intent that does not belong in the OrbitFabric mission model.

The canonical schema is packaged at:

```text
orbitfabric_fprime_adapter/schemas/profile-0.1.schema.json
```

## Target baseline

The initial schema accepts one exact candidate downstream pair:

```text
F Prime  v4.2.2
commit   8a62e455a90b6d4f498c332d45d65a2a819988d8

FPP      3.2.0
commit   93f484b7521a8e8894cba25b26e633cc87d8e37a
```

This is an exact candidate lane inherited from historical evidence. Canonical native acceptance is still pending and no version range is implied.

## Binding model

Each initial binding contains exactly one OrbitFabric source entity and exactly one target configuration.

The schema binds source domain to target kind directly. For example, a telemetry target config can only be paired with a `telemetry` source. Cross-domain bindings are schema-invalid.

### Telemetry target intent

```yaml
- id: tm.temperature
  sources:
    - domain: telemetry
      id: payload.temperature
  config:
    kind: telemetry
    host_component: Payload.Monitor
    host_instance: payloadMonitor
    symbol: OF_Temperature
    local_id: 16
    update: always
```

### Command target intent

```yaml
- id: cmd.start_acquisition
  sources:
    - domain: commands
      id: payload.start_acquisition
  config:
    kind: command
    host_component: Payload.Controller
    host_instance: payloadController
    symbol: OF_StartAcquisition
    local_opcode: 32
    command_kind: async
    priority: 0
    queue_full_behavior: drop
```

For an async command, `priority` and `queue_full_behavior` are mandatory. They are forbidden for `sync` and `guarded` declarations in this initial contract.

### Event target intent

```yaml
- id: evt.acquisition_started
  sources:
    - domain: events
      id: payload.acquisition_started
  config:
    kind: event
    host_component: Payload.Controller
    host_instance: payloadController
    symbol: OF_AcquisitionStarted
    local_id: 48
    severity: activity_high
```

`severity` is explicitly F Prime target intent. It is not an assertion that the OrbitFabric severity vocabulary and F Prime severity vocabulary are semantically identical.

### Packet target intent

```yaml
- id: packet.housekeeping
  sources:
    - domain: packets
      id: housekeeping
  config:
    kind: packet
    packet_set: PayloadPackets
    packet_name: OF_Housekeeping
    packet_id: 100
    group: 1
```

Packet membership comes from the OrbitFabric packet contract and is resolved through projected telemetry bindings. The adapter emits packet specifiers only; the F Prime project owns the enclosing telemetry packet set and its completeness/omit policy.

## FPP symbols

Target symbols use FPP identifier rules and reject known FPP keywords/reserved built-in names at schema validation time.

`host_component` may be a module-qualified FPP component type such as `Payload.Monitor`. `host_instance` is the project-owned instance name used for lexical target references.

Neither field authorizes the adapter to create the component or instance.

## Telemetry limit policy

OrbitFabric warning/critical limits and FPP color limits are not assumed equivalent. The Profile therefore makes the translation policy explicit:

```yaml
telemetry_limits:
  warning: yellow
  critical: red
```

Either source level may be `unmapped`. Canonical implementation must reject ambiguous cases where multiple source levels would map to the same FPP color on the same limit side.
