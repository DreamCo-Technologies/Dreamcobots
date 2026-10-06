# Buddy multi-source trainer: scope map (evidence)

Repo: DreamCo-Technologies/Dreamcobots at tree `2ccd678e5a242e085285cae1f7cf6818b5557f70` (read via authenticated gh API, read-only, 2026-09-28).

## What exists
| Area | Path | What it actually does | Status |
|---|---|---|---|
| Fabric contract | config/buddy_multimodal_learning_fabric.json, docs/multimodal-learning-fabric.md | Declares media types books, videos, websites, repositories; shared discover-to-learn loop; evidence pointer rules (page, timestamp, URL, path+rev); safety says no copying protected works | config/doc only |
| Training-data policy | config/buddy-training-data-provenance-policy.json | 9 ownership classes, 17 required metadata fields, block unknown assets from commercial packages | policy only; no code references it (code search hits only the file itself) |
| Evidence provenance | config/evidence_provenance_schema.json | Required fields for benchmark evidence (source, license_or_usage_basis, transformation, integrity_hash) | schema-like config |
| Consent registry | buddy/media/consent.py | Hash-bound consent records for voice/image cloning, scope, expiry, revoke, blocks minors | real code, tests/test_buddy_media.py |
| Output provenance | buddy/media/provenance.py | Keyed audio/image watermark, sidecar manifest, append-only ledger | real code |
| Video pipeline | config/buddy_video_*.json, tools/video_*.py, docs/video-*.md | Video scan/evidence/package compiler; quality gate requires source+license+hash | configs + tools |
| Data packages API | server/routes.ts (~L1050, L1738) | Planning templates only; states nothing is listed or sold; names ownership receipt, consent receipt, provenance record | contract stub |

## Gaps (per source)
- **Web**: robots/access policy declared in fabric config; no enforced provenance record per page. Missing enforcement.
- **Books**: fabric lists extraction steps; no license/ownership check before a book-derived artifact enters a package. Missing.
- **Movies**: not a media type in the fabric config at all (only "videos"). Missing.
- **Video**: quality gate config requires license + hash; enforcement not confirmed in code. Partial.
- **User uploads**: not a media type in the fabric; consent.py covers only voice/image cloning, not upload ownership attestation for training or resale. Missing.
- **Cross-cutting**: nothing maps a lesson's provenance through to LP-/RP-/DP- package sellability. This is the core gap.
