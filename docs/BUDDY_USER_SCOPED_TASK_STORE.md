# Buddy user-scoped task state

This module is a persistence primitive for long-running Buddy tasks. It is not yet an authenticated API, scheduler, agent executor, or dashboard integration.

## Trust boundary
- The host must supply an opaque authenticated subject ID. Never accept an owner ID from an HTTP request body or query string.
- Every task lookup, state transition, list, and audit-history query is scoped by that owner ID.
- New tasks begin as \`proposed\`. Execution requires a separate host approval and state transition.
- Status transitions are conditional on the expected current state; each transition writes an append-only event in the same SQLite transaction.
- SQLite files are created under a private directory where possible and chmodded to owner read/write (\`0600\`).
- Credential fields and common API-key, bearer-token, and private-key patterns are rejected. Store secrets in a dedicated secret manager, never in task payloads.
- Store references and minimal task summaries rather than raw chats, files, credentials, or unnecessary personal data.

## State lifecycle
\`proposed -> approved -> running -> verified\`

\`proposed -> rejected\`, \`approved -> rejected\`, and \`running -> needs_review -> approved|rejected\` are supported. There is no automatic execution, external write, payment, deployment, or model-training action in this package.

## Current limitations
- This PR does not mount the store into \`/api\`, Buddy's runtime, or the user dashboard.
- A production deployment still needs authenticated host integration, durable encrypted storage, backup/retention policy, deletion handling, rate limits, and security review.
- SQLite on one host is a local persistence layer, not a multi-region or horizontally shared database.
- The task store records workflow state; it does not run the task or prove the result.
