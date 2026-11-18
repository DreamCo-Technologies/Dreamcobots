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

## Dataset study and Buddy's research position

Hugging Face and other catalogs are discovery sources, not blanket grants of download or training rights. Run `python3 tools/buddy_discover_hf_dataset.py NAMESPACE/DATASET main` to fetch public metadata and resolve a branch/tag to a full immutable commit SHA. To inspect a public split before obtaining files, first select a config/split from the dataset page, then run `python3 tools/buddy_discover_hf_dataset.py NAMESPACE/DATASET main --preview --config CONFIG --split SPLIT`. This calls the [Dataset Viewer API](https://huggingface.co/docs/dataset-viewer/quick_start) for split metadata and a schema/sample preview. It checks up to 100 returned rows for schema mismatch, missingness, duplicates, mixed types, empty columns, likely emails/phone numbers/SSNs/payment card numbers/credentials, active HTML/script markers, and prompt-injection phrases. The report keeps aggregate findings and field names/types but discards raw example values. It also flags sensitive-looking columns, unsupported formats, and dataset scripts. These pattern checks can miss sensitive content and can raise false positives. The Dataset Viewer preview endpoint is not commit-pinned, so users must recheck the preview against the exact commit before any later download. Preview success is not a safety, privacy, representativeness, or legal review, and no scan can prove a dataset safe for all intended use.

Trust checks are shown as evidence and unresolved work, not as a single “trusted” badge: publisher identity and track record; immutable commit and file inventory; dataset card and license/terms; gated-use conditions; source provenance; file type and size; script presence (never execute these scripts); sample schema and sensitive-field screening; and a user review of the sample and intended use. A file/hash scan or platform preview cannot prove malware-free content, rights, or data quality. An unavailable preview is a reason to pause for a user-selected local review path, not to silently skip checks. Users choose whether to continue, and download rights remain a separate explicit decision.

`buddy.learning.data_study.create_data_use_record` records a dataset digest, source, license review, and a set of explicit use scopes. Its defaults grant no access. Private study, private retrieval, private Buddy training, shared fleet training, export/publication, and redistribution are separate decisions. A user's upload stays user-owned by default; a Buddy receives only the opted-in service permissions. Shared use with a user's Buddy is not a claim of joint legal ownership. Third-party ownership and license terms remain attached to their material.

To perform a local structural study, obtain a dataset file only after reviewing the preflight and approving download rights through the authorized source route. Verify the downloaded file's hash and compare it with the selected revision's file inventory before opening it. Then run `python3 tools/buddy_study_dataset.py ./dataset.csv --owner-id user-123 --buddy-id buddy-123 --source-url https://huggingface.co/datasets/OWNER/NAME --source-family hugging_face --license CC-BY-4.0 --rights-reviewed --terms-checked --private-study`. Add `--owner-created --consent-receipt RECEIPT-ID` for user-created data. The current runner accepts UTF-8 CSV and JSONL/NDJSON up to 20 MB and 100,000 rows. It outputs aggregate schema, missingness, type, duplicate, and hash evidence only; unsupported files, sensitive column names, unreviewed rights, and mismatched hashes are blocked. Neither metadata discovery nor preview downloads the dataset files, runs dataset code, or trains model weights. Training needs its own eligibility review and explicit consent; this repository does not implement a weight trainer for this flow.

`buddy.learning.data_study.position_on_dataset_study` creates a cautious first position from that profile; a single dataset remains provisional. `build_buddy_position` supports a broader revisable synthesis from versioned source references, independent source families, evidence quality, and supporting/challenging/context stances. These records keep source references and digests rather than raw rows or copied passages, surface conflicts, and require human review. Their numeric confidence is a simple heuristic, not a calibrated probability. They do not fine-tune model weights or convert an opinion into a verified fact.

For user-created datasets, the owner may export and request deletion. Training consent is independent from permission to study or retrieve the data, and private training does not imply shared-fleet training or publication. Revocation blocks future processing. Any shared model trained on user data requires a separately disclosed remediation policy because deleting source files alone cannot erase their influence from released weights.
