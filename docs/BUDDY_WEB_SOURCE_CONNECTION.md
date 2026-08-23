# Buddy Web Source Connection

The initial 50-source registry is now defined at `config/buddy-web-source-registry.json`.

## Runtime contract

Buddy should connect every registry entry through an adapter selected by source type:

- official API/feed when available;
- permitted documentation/page fetch when appropriate;
- research metadata/API for scholarly sources;
- repository/API access for GitHub resources;
- archive/discovery access for Common Crawl.

The connector must preserve source ID, canonical URL, retrieval time, content hash, publisher, source tier, extracted claims and lineage.

## Important boundary

Registering a source does **not** mean continuously crawling it, trusting it, or executing its content. The source becomes a candidate knowledge provider. The web-learning policy controls acquisition, isolation, verification and promotion.

## Refresh strategy

High-change technical sources should be refreshed more frequently than stable educational material. Material changes invalidate dependent knowledge for re-evaluation rather than silently replacing trusted conclusions.

## GitHub connection

GitHub is both a learning source and a system-of-record integration. Repository changes should be analyzed as evidence and routed through the same sandbox/evaluation/promotion pipeline before becoming durable Buddy improvements.
