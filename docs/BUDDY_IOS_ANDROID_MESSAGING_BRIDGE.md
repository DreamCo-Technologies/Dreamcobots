# Buddy iOS + Android Messaging Bridge

## iPhone / iMessage / SMS
Use an owner-controlled Mac running an authorized BlueBubbles server as the iMessage relay. The Mac relay forwards only owner-authorized inbound events to Buddy's signed webhook envelope. iMessage uses the `messaging` channel; SMS uses `sms`. The relay must be paired to one registered device ID and owner account.

## Android / SMS
Use an owner-installed Buddy Android companion or approved gateway. Grant only the OS permissions needed for the chosen feature. The initial Android contract supports SMS. Other app notifications require separate app-specific adapters and permissions; notification access is not blanket permission to read every conversation.

## Shared security contract
- HMAC-SHA256 signs `timestampSeconds.rawRequestBody`; reject stale signatures (five-minute default).
- Event IDs are replay-protected. The included in-memory store is for tests/development only; production must inject a durable atomic replay store.
- Device ID, platform, provider, contact mapping, source consent, and owner/contact permissions are checked before Buddy receives message content.
- Unknown and non-allowlisted contacts are denied.
- Inbound message bodies are returned for ephemeral processing and are not persisted by this module.
- Outbound messages reuse the communication-twin policy. Draft-only is the default; sends require explicit approval. Autonomous replies require allowlisted-routine mode, explicit contact permissions, and a low-stakes classification.
- High-impact financial, credential, contractual, medical, and legal content is blocked from autonomous replies.
- Transport is dependency-injected. The webhook transport sends only to configured HTTPS relay endpoints and uses secret references; it does not connect to a real phone until the relay is installed, enrolled, and configured.

## Production integration gates
1. Implement and sign the iOS Mac relay and Android companion packages.
2. Add owner-authenticated device enrollment, revocation, and durable contact identity mapping.
3. Replace the in-memory replay store with a durable unique-key store and atomic claim.
4. Add webhook body-size limits, rate limits, redacted audit receipts, and provider delivery reconciliation.
5. Store relay secrets in an OS keychain or managed vault and rotate/revoke on unlink.
6. Complete permission UX, participant-consent guidance, retention/deletion workflows, and security review.
7. Test with dedicated owner-controlled devices and numbers before enabling production delivery.

## Validation
```bash
node --import tsx --test tests/mobile-messaging-bridge.test.ts
npm run check
npm run test:governed
```
