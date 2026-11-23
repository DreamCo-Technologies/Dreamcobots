# Verified MasterBot-to-Domain Crosswalk

## Purpose

DreamCo has two distinct canonical inventories: 65 MasterBots in
`config/masterbot-65-registry.json` and 45 domain profiles in
`shared/division-production-contract.ts`. They are not interchangeable.

## Generator

Run:

```bash
python tools/build_masterbot_division_crosswalk.py
python tools/build_masterbot_division_crosswalk.py --check
python -m unittest tests.test_masterbot_division_crosswalk
```

The generator uses exact normalized name equality only. An exact match is
recorded as `proposed_exact_name_match`, not verified ownership. Fuzzy or
keyword-based candidates remain unresolved. Every proposed match requires
owner review; collaboration links are never inferred.

## Safety and execution

Do not route privileged work, allocate private datasets, start division-specific
training, or claim mastery from an unapproved mapping. The crosswalk is a
traceability aid until an accountable owner approves the primary assignment and
any collaborators. The generated artifact records both source registries,
unresolved entries, review flags, and counts.

## Next steps

1. Review each proposed exact-name match with the division owner.
2. Resolve unmatched MasterBots and domains from authoritative lineage records.
3. Add reviewed primary-owner and collaborator decisions with source evidence.
4. Connect approved mappings to capability-specific task runners, tests,
   runtime routes, private benchmark suites, and evidence-gated promotion.
5. Keep unresolved work visible; never fabricate coverage.
