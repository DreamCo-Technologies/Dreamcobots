# Division and MasterBot specialist-course readiness

The current Bootcamp has a shared 18-module foundation assigned across 55 canonical divisions and 65 MasterBot lanes. That foundation is necessary, but it is not a substitute for specialist education.

This audit expects eight domain-specific modules for every division and MasterBot lane:

- Domain overview
- Core skills and workflows
- Tools, software, libraries and integrations
- Task-by-task playbooks
- Safety, rights, licensing and permission boundaries
- Sandbox labs
- Assessment and answer key
- Practical capstone and transfer task

A module counts as ready for study review only when its manifest entry points to an existing guide under `docs/bootcamp/specialist/` and includes learning objectives, exercises, an assessment, dated citations with rights evidence, an approved rights review and human review.

## Run

```bash
python -m pytest -q tests/test_division_specialist_course_readiness.py
python tools/audit_division_specialist_course_readiness.py
```

The artifact manifest starts empty until actual specialist lessons are authored and reviewed. The expected 960 module slots are a work inventory, not a claim that 960 guides exist. Owner-specific routing remains blocked until explicit owner approval is recorded.
