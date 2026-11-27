# freeCodeCamp study-guide human review policy

A video metadata entry or an authorized transcript does not make a study guide approved. The detailed guide builder requires separate study, derivative-summary, and evaluation permissions, a verified transcript hash, and all required guide sections.

For a guide to be marked `APPROVED`, its `review` record must also include:

- `review_status: approved`
- A named `reviewer`
- A timezone-aware ISO-8601 `reviewed_at` timestamp
- A `review_evidence_ref` that points to the human review record

A missing reviewer, timestamp, or evidence reference keeps the guide in `NEEDS_REVIEW`. This does not grant transcript redistribution or model-training rights. The catalog refresh workflow remains metadata-only and does not download captions, transcripts, or media.
