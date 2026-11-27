# Hugging Face Bootcamp coverage audit

Validates the existing Hugging Face catalog against the internal Buddy course-track registry:
- 12 official Hugging Face courses;
- 18 ordered ecosystem engineering modules;
- 37 documented task families;
- shared-foundation delivery to 55 canonical divisions and 65 MasterBot lanes; and
- the two internal course-track parser routes.

Run:

```bash
python -m pytest -q tests/test_huggingface_bootcamp_coverage.py
python tools/audit_huggingface_bootcamp_coverage.py
```

The report distinguishes catalog coverage from course study, original guide authoring, transcript rights, assessment evidence, model training and mastery. Third-party course content is not assumed to be training data, and transcript permission remains ungranted unless separately documented.
