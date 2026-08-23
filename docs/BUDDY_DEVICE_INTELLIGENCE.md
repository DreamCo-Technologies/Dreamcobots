# Buddy Device Intelligence

## Purpose

Turn the Universal Device Fabric into a capability-aware device intelligence layer. Buddy should reason about *what can be done* with authorized devices, not merely whether a device is connected.

## Capability graph

Each device is represented as:

```text
Device
 ├── identity
 ├── trust / authorization
 ├── transport
 ├── services
 ├── capabilities
 ├── state
 ├── quality
 └── constraints
```

Capabilities should be normalized into machine-readable contracts such as:

- `audio.output`
- `audio.input`
- `display.video`
- `display.screen_mirroring`
- `camera.capture`
- `microphone.capture`
- `input.controller`
- `input.keyboard`
- `input.pointer`
- `file.transfer`
- `print.output`

Actual support must be verified through the platform adapter.

## Task-to-device planning

```text
USER REQUEST
 ↓
TASK REQUIREMENTS
 ↓
CAPABILITY MATCH
 ↓
AUTHORIZED DEVICE SET
 ↓
QUALITY / PRIVACY / AVAILABILITY RANKING
 ↓
PLAN
 ↓
CONNECT
 ↓
VERIFY
 ↓
EXECUTE
 ↓
MONITOR
```

## Multi-device compositions

Buddy should support plans involving multiple devices when authorized. Example:

```text
Laptop → video source
TV → video display
Headphones → private audio output
Controller → input
```

The planner should understand dependencies between these capabilities rather than treating each device independently.

## Adaptive routing

If a device becomes unavailable, Buddy should re-plan using other authorized compatible devices. The replacement should be verified before use.

## Capability confidence

Distinguish:

- declared capability;
- observed capability;
- verified capability;
- temporarily unavailable capability;
- unsupported capability.

A device's marketing name is never sufficient evidence of capability.

## Privacy-aware selection

For sensitive tasks, Buddy should prefer the least-privileged suitable device. Examples include private audio, camera use, microphone input and screen sharing.

## Future adapters

The architecture can accommodate new transports and protocols without changing Buddy's core planner. New adapters publish normalized capabilities to the same registry.
