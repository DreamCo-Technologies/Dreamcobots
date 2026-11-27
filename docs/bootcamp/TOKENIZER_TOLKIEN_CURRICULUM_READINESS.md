# Tokenizer and Tolkien curriculum readiness audit

The audit checks the two specialist study tracks without conflating study with execution.

Tokenizer checks:
- all 12 ordered lessons contain outcomes, labs and assessments;
- course references are HTTPS and rights-qualified;
- rights, holdout, artifact, model-compatibility, compute and release gates exist; and
- reading, tokenizer training and model-weight training remain distinct.

Tolkien checks:
- core curriculum and 12 extended units have learning outcomes, labs, assessments and rights gates;
- copyrighted Tolkien text ingestion, training and verbatim reproduction remain disabled;
- unknown rights remain blocked; and
- a course reference stays pending until supplied or approved.

Run:

```bash
python -m pytest -q tests/test_tokenizer_tolkien_curricula.py
python tools/audit_tokenizer_tolkien_curricula.py
```

This is a structural readiness check. It does not run tokenizer training, model training, or literary study, and it does not grant rights to copyrighted texts.
