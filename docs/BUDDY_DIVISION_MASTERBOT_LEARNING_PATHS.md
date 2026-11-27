# Ordered learning paths for all canonical divisions and MasterBot lanes

This manifest derives 55 division profiles from `shared/division-production-contract.ts` and 65 MasterBot identities from `config/masterbot-65-registry.json`. Both receive the same seven-stage ordered learning path, with division-specific mission, outcome, boundary, and focus areas retained from the canonical profile.

## Seven-stage sequence

1. Mission, users, and boundaries.
2. Domain fundamentals, terminology, standards, and source-backed concepts.
3. Tools, software, libraries, APIs, data sources, and permissions.
4. Professional workflows, realistic practice, quality, and recovery.
5. Advanced specialist and cross-functional cases.
6. Benchmarks, independent holdout transfer, regression, and delayed recall.
7. Instructor capability and reviewed curriculum improvement.

## Ownership is not inferred

The 55-to-65 crosswalk remains proposed. Exact-name matches are not approved ownership. Unresolved records remain unresolved; no fuzzy mapping is generated. Owner review is required before privileged routing or domain-specific authority is granted.

## Completion truth

This creates ordered learning-path templates, not 120 completed domain courses. Each division and MasterBot still needs authored lessons, worked examples, labs, assessments, human review, and evidence-backed mastery.

## Validate

```bash
python -m pytest -q tests/test_buddy_division_masterbot_learning_paths.py
python tools/validate_buddy_division_masterbot_learning_paths.py
```
