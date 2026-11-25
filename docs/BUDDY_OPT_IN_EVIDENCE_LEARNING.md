# Buddy opt-in evidence learning

This package is a host-mediated learning proposal layer. It does not passively observe users, access the network, execute adapters, train weights, promote models, or start background workers.

## Consent and privacy
- An authenticated host supplies tenant identity and explicit capture consent.
- Events must be redacted and independently verified before recording.
- Common credential patterns are rejected from learning-event text.
- Private SQLite persistence creates a private directory and owner-only database file where supported.
- Tenant deletion removes that tenant's local event rows; the host must propagate deletion to backups and any other stores.
- Store minimal redacted outcomes and references, not raw chats, screenshots, credentials, hidden reasoning, or private holdout answers.

## Learning and capability boundaries
- Recommendations use only each tenant's training split. Validation and holdout records are not used for recommendations.
- SOP candidates are drafts with empty steps until a human reviews source evidence.
- Adapter discovery is descriptive only. Risky capabilities cannot be registered in this registry; they require a separate host authorization path.
- Benchmark thresholds can identify candidates for independent review but never authorize promotion.
- Scheduled projects are proposals only; no task is enqueued.

## Current limitations
- The bridge wraps the existing task runner but does not create a background worker or 24/7 execution service.
- No model weights, adapters, or checkpoints are trained or updated.
- Production deployment still needs authenticated API integration, encryption/key management, backup and deletion propagation, retention policy, rate limits, and a security review.
