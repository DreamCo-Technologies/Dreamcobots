# Buddy Personal Communication Twin

## Purpose

Buddy Personal Communication Twin is a governed communications capability inside Buddy OS. It can learn owner-approved writing preferences, retrieve authorized conversation context, prepare drafts, and operate approved communication workflows. It is not a human impersonation system.

## Existing capabilities to reuse

- `server/communication-behavior.ts` and `config/buddy-communication-behavior.json` remain the canonical writing-style and communication-preference layer.
- Existing Buddy memory, autonomy, connection, secret-intake, approval-notification, and provider-integration systems remain the integration boundaries.
- This feature must not introduce a second identity store, credential vault, vector database, or outbound dispatcher.

## Initial code-backed scope

- Typed channel, relationship, contact-permission, and autonomy contracts.
- Fail-closed authorization decisions for read, draft, send, routine auto-reply, call answering, and owner-voice synthesis.
- Source ingestion requires both owner authorization and explicit source consent.
- Raw message retention is disabled in the ingestion result contract.
- Communication content is never included in the audit event contract.
- High-impact content is blocked from autonomous send/reply paths.
- Voice workflows require owner voice consent where applicable, AI disclosure, and human takeover availability.
- Training eligibility is explicitly not granted by ingestion.

## Autonomy defaults

1. `draft_only` is the default.
2. Sending requires per-action owner approval.
3. Routine auto-replies require `allowlisted_routine`, contact-level send and auto-reply permission, and an explicit low-stakes classification.
4. Unknown contacts are denied.
5. Financial, credential, contractual, medical, and legal content is blocked from autonomous handling.
6. AI disclosure and a human takeover path are mandatory for voice workflows.

## Provider integration sequence

1. Connect OAuth through the existing connection center; request least-privilege scopes.
2. Verify provider webhook signatures and replay protection.
3. Normalize provider events into an internal envelope with provider IDs, timestamps, channel, and contact identity.
4. Resolve contact permissions before retrieving content or generating a draft.
5. Reuse the existing communication behavior profile for style guidance.
6. Generate a draft and store it using the existing approved storage boundary.
7. Require owner approval before invoking a send adapter.
8. Record a content-free audit event and provider delivery receipt.

No provider adapter, credential, webhook endpoint, external send, or voice call is enabled by this foundation.

## Data and privacy rules

- Import only sources explicitly authorized by the owner and covered by applicable participant consent.
- Do not ingest third-party conversations merely because a device export is available.
- Minimize content, redact secrets, and prefer derived preference summaries over raw transcript retention.
- Do not use communication data for model training or fine-tuning without a separate, source-specific rights and owner authorization workflow.
- Support export, correction, revocation, and deletion through the existing privacy controls.
- Encrypt provider tokens and never expose them to prompts, logs, or browser clients.

## Production gates not satisfied by this foundation

- Provider OAuth scopes and account ownership verification.
- Gmail / Microsoft Graph adapter implementation and verified webhook handling.
- SMS provider registration, opt-in/opt-out handling, and delivery receipts.
- Local messaging bridge packaging and device authorization.
- Voice provider selection, voice-clone rights verification, jurisdiction-aware disclosure/recording policy, and human escalation.
- Durable contact permissions and revocation propagation.
- Secret redaction, retention/deletion jobs, encryption review, rate limits, abuse monitoring, and incident response.
- Staging end-to-end tests using dedicated test accounts and numbers.
- Security review and owner acceptance before any autonomous operation.

## Validation

Run:

```bash
node --import tsx --test tests/communication-twin.test.ts
npm run check
```

The tests exercise the policy engine only. They do not prove provider connectivity, account ownership, production delivery, call handling, or legal compliance.
