# Buddy OS Shell — event bus (observability slice)

Minimal contract so OS observability tiles align with the shell without a parallel control plane.

## Events

| Event | Direction | Payload (safe) |
|-------|-----------|----------------|
| `dreamco:observability.publish` | producer → shell | `{ commit, environment, artifact_path, evidence_complete }` |
| `dreamco:observability.tile_state` | Pages loader → shell | `{ production_ready: false, aggregate, evidence_complete }` |

Emitted by `website/os-observability.js` after load (or fail-closed).

## Rules

1. Fail closed: no artifact ⇒ yellow tiles, never green.
2. Yellow ≠ green for any aggregate percentage.
3. Do not flip `production_ready` from the shell event bus.
4. Tiles live on `actions.html` and `os.html` only — no extra nav empire.
