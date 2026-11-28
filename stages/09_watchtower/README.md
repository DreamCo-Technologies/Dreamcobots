# Universal Watchtower — Stage 09

The Watchtower is a policy-first monitoring pipeline. It separates collection,
normalization, matching, scoring, deduplication, and alert persistence.

## Current implementation boundary

- JSON rule catalog with strict validation.
- Provider-neutral normalized observations.
- Deterministic keyword/price/currency filters and scoring.
- Fingerprint-based duplicate suppression.
- Atomic JSON state and alert output.
- Optional public HTTPS JSON-feed adapter with strict SSRF protections,
  response-size limits, timeouts, content-type checks, and redirects disabled.

This first slice does **not** scrape authenticated websites, bypass CAPTCHAs,
access sportsbook accounts, execute trades, bid at auctions, or send external
notifications. Those require separately reviewed provider adapters, user
credentials stored in a secret manager, explicit permissions, and live tests.

## Rule example

\`\`\`json
[
  {
    "rule_id": "grocery-deals",
    "name": "Grocery public feed",
    "adapter": "json_feed",
    "target": "https://example.org/public/deals.json",
    "enabled": true,
    "interval_seconds": 900,
    "min_score": 50,
    "include_any": ["eggs", "milk", "chicken"],
    "exclude": ["expired"],
    "max_price": 8.0,
    "currency": "USD",
    "cooldown_seconds": 3600,
    "max_items": 100
  }
]
\`\`\`

Targets must be public HTTPS endpoints. Private IPs, local hosts, non-standard
ports, redirects, credentials embedded in URLs, and oversized responses are
rejected.

## CLI

Validate a catalog:

\`\`\`bash
python -m stages.09_watchtower.cli validate --rules config/watchtower/rules.json
\`\`\`

Evaluate fixture observations:

\`\`\`bash
python -m stages.09_watchtower.cli evaluate \\
  --rules config/watchtower/rules.json \\
  --observations config/watchtower/observations.example.json \\
  --state .dreamco/watchtower-state.json \\
  --output reports/watchtower-alerts.json
\`\`\`

Use a scheduler or a separately permissioned job runner to invoke collection.
Do not put API keys in rule files or fixture JSON.
