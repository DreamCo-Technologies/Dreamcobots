# Resource-Scaled Dynamic Bot Fleet

## Decision

The DreamCo bot system has **no fixed bot-count ceiling**. Historical counts such as 1,051 are snapshots of discovered modules/capability implementations, not architectural limits and not the definition of the fleet.

## Architecture

Bots are modular capability providers. Superbots are compositional orchestrators that can dynamically discover and invoke those modules. Buddy is the routing and reasoning control plane.

```text
Resources
  -> Discovery
  -> Module Registry
  -> Capability Graph
  -> Superbot Composition
  -> Buddy Router
  -> 10 Actions
  -> Verification / Observability
```

## Resource-scaled behavior

Fleet size should be determined by available and authorized resources, including compute, memory, storage, model/provider capacity, concurrency, latency budgets, task demand, quotas, and governance constraints.

The system may add, retire, shard, consolidate, or recompose modules dynamically. No implementation should use a hard-coded maximum such as 1,051, 3,000, 10,000, or any other arbitrary fleet ceiling.

## Module versus Superbot

- **Module:** focused capability provider with a stable contract.
- **Superbot:** composition/orchestration layer that combines modules and capabilities for a domain or mission.
- **Buddy:** global router/reasoning coordinator that chooses appropriate superbots/modules and verification paths.
- **Action:** stable user-facing control-plane facade; exactly ten top-level Actions remain the UI contract.

The 1,051 existing bot profiles should therefore be treated as reusable modules/capability assets and progressively registered into the Superbot graph rather than treated as 1,051 permanent peer-level UI bots.

## Dynamic lifecycle

`DISCOVER -> REGISTER -> CLASSIFY -> CONNECT -> TEST -> OBSERVE -> VERIFY -> COMPOSE -> SCALE -> RETIRE/RECOMPOSE`

## Scaling policy

Scale out when demand and resources justify additional module instances. Scale down when idle. Consolidate overlapping modules when a stronger composition is more efficient. Never duplicate modules solely to increase a count.

## Failure behavior

A module failure should not automatically fail the whole system when an equivalent verified fallback exists. The router should record the failure, select a safe fallback when policy permits, verify the replacement path, and surface the event through the Actions page.

## Capacity reporting

Actions-page reporting must show dynamic counts such as:
- discovered modules
- registered modules
- routable modules
- verified modules
- active instances
- available capacity
- failed modules
- blocked modules
- retired modules
- superbot compositions

These are telemetry values, not fixed architectural limits.

## Compatibility requirement

Existing bot-accounting, Actions health, failure-watch, failure-sweep, debugging, and governance workflows should consume dynamic discovery/registry data rather than assumptions about a fixed fleet size.
