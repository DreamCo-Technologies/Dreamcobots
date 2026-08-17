# Buddy Benchmark Dataset Factory

The benchmark program needs a dataset engine, not a fixed spreadsheet of tests.

## Pipeline

`source → normalize → deduplicate → classify → difficulty → variants → edge cases → adversarial cases → evidence/ground truth → privacy/license checks → sandbox validation → splits → version → publish metadata`

## Evaluation splits

- **Train:** capability development.
- **Validation:** model selection and gap detection.
- **Test:** locked evaluation.
- **Transfer:** unfamiliar domains and formats.
- **Regression:** previous failures and mastered capabilities.

## Quality

Each dataset receives coverage, difficulty, diversity, label quality, provenance, leakage resistance, reproducibility, transfer value, and real-world relevance scores.

Unknown labels are allowed. Buddy must never manufacture ground truth merely to make a benchmark pass.

The factory can use O*NET, open datasets, public standards, government publications, authorized workflows, software documentation, repository evidence, sandbox traces, human feedback, and synthetic scenarios as inputs while respecting provenance, licensing, privacy, and reproducibility requirements.
