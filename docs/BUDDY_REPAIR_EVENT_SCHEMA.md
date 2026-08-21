# Buddy Repair Event Schema

A normalized event model for connecting Issues, Actions, Agents, Council and verification.

## Required event fields

```json
{
  "event_id": "unique-id",
  "incident_id": "canonical-incident-id",
  "source": "issue|action|agent|monitor",
  "event_type": "detected|triaged|diagnosed|planned|approved|repair_started|test_result|council_result|verified|resolved|escalated",
  "occurred_at": "ISO-8601",
  "repository": "owner/repository",
  "ref": "branch-or-commit",
  "actor": "service-or-agent",
  "status": "success|failure|blocked|unknown",
  "confidence": 0.0,
  "evidence": [],
  "affected_components": [],
  "next_action": null
}
```

## Rules

- `event_id` is unique.
- `incident_id` links related events.
- Evidence references must be traceable.
- Confidence is an estimate, never proof.
- Unknown values remain unknown.
- Events are append-oriented; corrections create a new event rather than erasing history.

## Why this matters

Without a common event model, the Issues page, Actions page and Agents page can disagree about what happened. The event model gives Buddy a shared timeline for diagnosis, repair, verification and learning.

## Example timeline

```text
DETECTED
  -> TRIAGED
  -> DIAGNOSED
  -> PLANNED
  -> APPROVED
  -> REPAIR_STARTED
  -> TEST_RESULT
  -> COUNCIL_RESULT
  -> VERIFIED
  -> RESOLVED
```

The UI can render this timeline for beginners while advanced users can inspect the underlying evidence.
