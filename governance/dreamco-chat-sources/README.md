# DreamCo conversation source intake

This directory is the explicit bridge between ChatGPT project conversations and the repository's traceability system.

## Intake rules
1. Export or copy only DreamCo project conversations the owner intends to preserve.
2. Keep original conversation identifiers, timestamps, titles, and message order where available.
3. Save Markdown, JSON, or text exports in this directory. Prefer one file per conversation.
4. Never include passwords, API keys, session tokens, private personal data, or unrelated conversations.
5. Do not rewrite the source transcript during ingestion. Add normalized requirements and links in the evidence ledger separately.
6. Re-run `python tools/dreamco_global_reconciliation.py` after adding sources.

The scanner inventories approved exports and their hashes. It does not have direct access to private ChatGPT conversation storage, and it does not pretend that an unexported chat was scanned.
