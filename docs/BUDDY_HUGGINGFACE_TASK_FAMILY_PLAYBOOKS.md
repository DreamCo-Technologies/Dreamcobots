# Hugging Face 37 task-family playbooks

This original playbook pack expands each task in the repository's current Hugging Face task taxonomy. It covers text, vision, audio, tabular, multimodal, and reinforcement-learning task families.

Each task family has learning objectives, an ordered workflow, a sandbox lab, task-specific evaluation metrics, risk checks, acceptance criteria, and evidence requirements. Pipeline tags remain discovery hints and are not treated as proof of model suitability.

## Dynamic inventory boundary

The taxonomy is a discovery snapshot, not a complete or permanent list of Hugging Face Hub tasks. Refresh official Hub metadata and preserve newly discovered or unknown task families. The taxonomy contains entries without a documented pipeline tag; those must not receive invented tags.

## Validate

```bash
python -m pytest -q tests/test_buddy_huggingface_task_family_playbooks.py
python tools/validate_buddy_huggingface_task_family_playbooks.py
```

All playbooks remain `original_task_guide_draft_not_executed` and `mastery_status: not_assessed`. Model/data licenses, privacy, consent, holdout integrity, and human review remain mandatory.
