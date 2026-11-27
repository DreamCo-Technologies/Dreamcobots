# 55-division and 65-MasterBot curriculum coverage audit

This audit cross-checks the canonical MasterBot registry, proposed 55-domain ownership crosswalk, and 25M course delivery assignments.

It verifies:
- exactly 55 division foundation assignments and 65 MasterBot foundation assignments;
- stable unique IDs and consistent names across the source registries and course;
- all 18 LLM25 modules remain in contiguous prerequisite order;
- every unapproved division/MasterBot remains behind its specialist ownership-review gate; and
- an approved mapping must carry an explicit approval evidence reference.

Run:

```bash
python -m pytest -q tests/test_bootcamp_division_masterbot_coverage.py
python tools/audit_bootcamp_division_masterbot_coverage.py
```

The current crosswalk is proposed and requires owner review. This is not a reason to block shared AI/model literacy foundations; it is a reason not to infer specialist ownership or route privileged domain work. The audit never approves ownership or claims domain mastery.
