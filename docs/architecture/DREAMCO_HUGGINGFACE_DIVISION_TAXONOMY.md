# DreamCo Hugging Face Division Taxonomy and Discovery Map

**Status:** discovery-only reference; not an approval to train or redistribute data.

## Why this exists

DreamCo has two distinct registries:
- 65 canonical MasterBots, each of which receives its own discovery lane and model-development identity.
- 55 domain division profiles, connected through the existing conservative crosswalk. Exact-name matches remain proposed until owner approval; unresolved MasterBots remain unresolved.

This map connects the 65 MasterBot lanes to Hugging Face task families and existing DreamCo capability packs without inventing domain ownership.

## Taxonomy dimensions

The reference taxonomy records NLP, computer-vision, audio, tabular, multimodal, and reinforcement-learning task families. It keeps model `pipeline_tag` values separate from dataset `task_categories` and `task_ids`. The Hub's metadata also exposes dimensions such as language, multilinguality, size category, benchmark, gated status, license, freshness, downloads, likes, and tags.

Official references:
- https://huggingface.co/docs/hub/main/models-tasks
- https://huggingface.co/docs/huggingface_hub/main/package_reference/hf_api
- https://huggingface.co/docs/transformers.js/en/pipelines

The static task list is a refreshable reference snapshot, not a claim that it contains every current Hub tag. New or unknown tags must be preserved for review rather than discarded.

## Generated route contract

`config/generated/division-huggingface-taxonomy-map.json` contains one row per canonical MasterBot:
- a stable discovery lane ID;
- subject terms and search queries;
- the existing MasterBot-to-domain crosswalk state;
- candidate capability packs and candidate model pipeline tags;
- an explicit unverified-rights state.

All lanes receive shared instruction, reasoning, and safety research packs. Additional packs are discovery hints based on the MasterBot name—not a learned capability or a validated training plan.

## Rights and training boundaries

- Public visibility, a Hub tag, or a dataset listing does not establish training permission.
- Unknown licenses, missing dataset cards, incomplete file-level rights, and privacy issues block training.
- Benchmark holdouts remain evaluation-only.
- Customer-private data is not shared across tenants.
- Candidate search results never auto-approve a dataset, model, training run, marketplace listing, or release.

## Regeneration and tests

```bash
python3 tools/build_division_huggingface_taxonomy_map.py
python3 -m unittest tests.test_division_huggingface_taxonomy_map
python3 tools/build_division_huggingface_taxonomy_map.py --check
```
