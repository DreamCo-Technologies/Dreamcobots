# Bootcamp source catalog and policy gates (stages 00–01)

This first implementation establishes an append-only metadata ledger and a fail-closed source policy gate. It does not download media, captions, or transcripts and does not train models.

The append-only ledger is data/manifests/source_catalog.jsonl. Each record stores source ID and URL, video ID, publication date, duration, item license tag, transcript status, observation timestamp, and SHA-256 content hash. Identical observations are skipped. Changed metadata appends a new record; existing lines are never rewritten.

Install PyYAML and yt-dlp, then run:
python -m stages.00_catalog_sync.catalog_sync --source freecodecamp=https://www.youtube.com/@freecodecamp

The cataloger invokes yt-dlp --flat-playlist --dump-json. Source URLs must match a configured metadata-catalog domain.

Domain classification is not a substitute for item-level rights. Missing item license evidence blocks transcript extraction. FACT_EXTRACTION_ONLY does not permit transcript extraction or commercial model training. PUBLIC_DOMAIN and PERMISSIVE_COMMERCIAL require explicit item-level evidence and purpose authorization.

Clean-room synthesis, learner state, sandbox grading, division coverage, cryptographic holdouts, model evaluation, and the evidence dashboard remain subsequent implementation stages and are not claimed complete.
