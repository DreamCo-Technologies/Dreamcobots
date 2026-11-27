# Hugging Face module review readiness

The repository contains 12 official course references and 18 original ecosystem-module guide drafts. The drafts are not official course transcripts and are not yet evidence that Buddy has completed the material.

A module is ready for study only when the review manifest points to three existing, SHA-256-verified repository artifacts under `docs/bootcamp/huggingface/`:

- A readable authored guide
- A hands-on lab
- An assessment

It must also include dated HTTPS citations with rights evidence, an approved rights review, and a named human reviewer with a timestamp. The audit reports missing artifacts and review gaps per module.

## Run

```bash
python -m unittest tests.test_huggingface_module_review_readiness
python tools/audit_huggingface_module_review_readiness.py
```

Transcript permissions remain ungranted, and official course content is not authorized as training data. Original DreamCo study materials may be authored from permitted public documentation with proper source attribution and rights review. A module becoming ready for study is not evidence of study, assessment success, benchmark passage, or mastery.
