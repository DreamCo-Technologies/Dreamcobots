# evidence/frontier/f0

F0 Baseline packets only.

- Store signed packets in `packets/f0-*.json` matching `schemas/buddy-f0-evidence-packet.schema.json`.
- `claim_boundary.frontier_claim_allowed` is always false on F0 packets.
- Empty `evidence/frontier/current-status.bundle.json` runs means baseline not yet executed — not a pass.
