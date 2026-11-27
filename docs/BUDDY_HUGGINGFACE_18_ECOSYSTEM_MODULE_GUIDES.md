# Hugging Face ecosystem module study guides

This guide pack expands all 18 modules in the canonical Hugging Face learning map into original three-part lesson sequences, learning objectives, practical labs, assessment tasks, failure cases, and evidence requirements. It preserves all 12 official course links as link-only references.

## Module coverage

The modules cover Hub/repository operations, governance, datasets, Spaces, Transformers, tokenizers, Accelerate, PEFT, TRL, Diffusers, vision, embeddings/retrieval, optimization, evaluation, inference providers, experiment operations, agents, and robotics/3D.

## Rights and completion

The guide pack does not reproduce official course content. Official course pages remain references; transcripts and media are not downloaded. Training-data permissions are separate from study permissions. All module guides remain `guide_draft_not_studied_or_benchmarked` pending human review, hands-on labs, holdout evaluation, and regression evidence.

## Validate

```bash
python -m pytest -q tests/test_buddy_huggingface_module_guides.py
python tools/validate_buddy_huggingface_module_guides.py
```
