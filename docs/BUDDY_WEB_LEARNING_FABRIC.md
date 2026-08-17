# Buddy Governed Web Learning Fabric

## Objective

Allow Buddy to continuously discover useful public web information, evaluate it, and turn validated knowledge into sandbox training data without treating the open web as trusted truth.

## Source tiers

1. **Primary/authoritative:** government, standards bodies, official product documentation, original research, official company sources.
2. **High-quality secondary:** established journalism, technical references, reputable institutions.
3. **Community:** forums, social platforms, user reports and discussions; useful for discovery and sentiment, but independently verified before durable learning.
4. **Web archives/open corpora:** Common Crawl and similar datasets for broad discovery and historical analysis. Common Crawl provides a free open web corpus with billions of pages and regular crawls, plus URL/CDXJ indexes for querying it. citeturn0search0turn0search4turn0search6

## Acquisition loop

```text
DISCOVER
 ↓
FETCH WITH POLICY
 ↓
PROVENANCE + TIMESTAMP
 ↓
EXTRACT CLAIMS
 ↓
DE-DUPLICATE
 ↓
CROSS-SOURCE CHECK
 ↓
QUALITY / FRESHNESS SCORE
 ↓
SANDBOX KNOWLEDGE
 ↓
EVALUATE
 ↓
PROMOTE VERIFIED KNOWLEDGE
```

## Web access rules

- Respect robots.txt, site terms, authentication boundaries and applicable law.
- Prefer official APIs and feeds when available.
- Apply rate limits, caching and backoff.
- Do not bypass access controls, paywalls, CAPTCHAs or anti-bot protections.
- Treat fetched web content as untrusted input; never execute instructions embedded in pages as if they were system instructions.
- Detect prompt injection and malicious instructions in retrieved content.
- Preserve source URL, retrieval time, content hash and extraction lineage.

Google's documentation explicitly recommends robots.txt for controlling crawling and sitemaps for discovery; Buddy should honor those controls when crawling sites it does not own. citeturn0search12

## Knowledge objects

Each extracted claim should contain:

- claim ID;
- source URL;
- source tier;
- publisher;
- retrieval timestamp;
- publication/update timestamp when available;
- content hash;
- extracted claim;
- supporting passage/reference;
- confidence;
- corroborating sources;
- contradiction set;
- expiration/review date;
- domain/division;
- promotion state.

## Learning boundary

Web information first becomes **candidate knowledge**. It may enter the Buddy Sandbox Bootcamp for evaluation. It becomes durable strategy/knowledge only after appropriate verification and governance.

## Freshness

Time-sensitive domains require shorter review windows. Stable facts may use longer windows. A stale source should not silently override newer authoritative evidence.

## Change detection

Track source versions/hashes where practical. When important pages change, trigger re-evaluation of dependent knowledge and strategies.

## Web-to-action boundary

Information gathered from the web must not automatically authorize an external action. A web page can inform a plan; it cannot grant Buddy permission to act.

## Bootcamp integration

```text
WEB SOURCES
 ↓
CANDIDATE CLAIMS
 ↓
VERIFIED CLAIMS
 ↓
BOOTCAMP DATA PACKAGE
 ↓
EVALUATION / REPLAY
 ↓
VALIDATED STRATEGY
 ↓
GOVERNED PROMOTION
```

## Recommended first source families

- official government portals and datasets;
- standards/documentation repositories;
- official APIs and product documentation;
- research repositories and peer-reviewed literature;
- Common Crawl for broad public-web discovery and historical comparisons;
- carefully selected secondary and community sources for discovery and corroboration.
