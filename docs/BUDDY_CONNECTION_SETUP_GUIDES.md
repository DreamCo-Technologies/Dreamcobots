# Buddy connection setup guides

This catalog gives every entry in `config/buddy-universal-connection-catalog.json` a beginner-friendly setup template. Buddy should explain what the service does, why it needs access, what scopes it requests, where credentials belong, what it may cost, and how to test or disconnect it.

## Credential safety

Never ask users to paste passwords or raw API keys into chat. Store credentials only in a host environment excluded from Git, an operating-system keychain, or a managed server vault. Repository files, browser local storage, logs, and analytics may contain references and status—not secret values.

## Safe setup sequence

1. Verify the official provider domain, current docs, terms, country availability, and pricing.
2. Explain the exact purpose and minimum requested permissions in plain language.
3. Start read-only, mock, or local; do not request write scopes by default.
4. Configure a secret reference through an approved host-side secret store if needed.
5. Run a non-destructive sandbox health check and preserve evidence.
6. Test revoked credentials, denied scopes, timeouts, rate limits, and disconnect.
7. Require exact owner approval for external writes, publishing, purchases, or spending.

## Honest status

Every profile is `guide_template_ready_live_connection_unverified`. A setup URL or secret reference is not proof of a working adapter. Current provider terms and costs must be checked before enablement. Live status requires adapter evidence, permissions, sandbox checks, and current runtime verification.

## Validate

```bash
python -m pytest -q tests/test_buddy_connection_setup_guides.py
python tools/validate_buddy_connection_setup_guides.py
```
