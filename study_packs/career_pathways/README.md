# Edu Career Pathways: majors to O*NET study plans

Maps 27 common bachelor's majors (2020 CIP codes) to O*NET-SOC occupations using the official O*NET CIP crosswalk, then writes one study plan per major: linked occupations with O*NET 31.0 Job Zones, the highest-importance O*NET knowledge areas and Essential Skills, 1 to 3 Job Zone-based entry-level targets, a 4-year outline, typical next steps, and 6 practice tasks with rubrics. The outline, next steps, and practice prompts are DreamCo-derived guidance, not O*NET data.

Fetch pinned sources: `python fetch_sources.py` (verifies sha256). Rebuild: `python build.py` (needs pandas, openpyxl; set `DREAMCO_GATE_TOOL` to `tools/license_provenance_gate.py` if it is not found automatically). Test: `pytest tests` (needs jsonschema for schema checks).

Outputs:
- `data/major_to_onet.csv`, `data/majors_selected.json` (incl. Job Zones and entry targets), `data/practice_tasks.json`.
- `study_plans/<cip>_<slug>.md` (human layer) and sidecar folder `study_plans/<cip>_<slug>/` with `plan.json` (machine layer), `provenance.json`, `asset.json`, `candidate.json`, and `license_gate.json` (output of the DreamCo license/provenance gate).
- Sources and hashes: `raw/SOURCES.md`. Test schemas snapshot: `tests/schemas/` (used when the live DreamCo schemas are not present).

Method notes:
- Entry targets: linked occupations in O*NET Job Zone 4 (typical bachelor's level), excluding titles containing Manager, Chief, Postsecondary, or All Other (and Supervisor, Director, or Treasurers and Controllers unless nothing else is linked). Base `.00` codes first, then ranked by correlation with the eligible occupations' average knowledge profile. Fallback order is Job Zone 3, then 5, then 1-2. Exceptions: Pharmacy uses Job Zone 5 (Pharmacists), and Criminal Justice uses Job Zone 3, because its only crosswalk links are supervisors, faculty, and an All Other code.
- Practice tasks reference an O*NET 31.0 Task ID and O*NET-SOC code only. The task text is not reproduced; its first verb picks the prompt type. Prompts and rubrics are labeled "DreamCo-original practice prompt".

## Status and open items

- O*NET 31.0 is pinned for this pack (DP-ONET): every O*NET file comes from `db_31_0_csv` and is sha256-pinned. The fleet O*NET ingest is still pinned to 30.3, and aligning the two is an open decision. O*NET 31.0 split Skills into Essential Skills and Transferable Skills; this pack uses Essential Skills.
- License gate (tools/license_provenance_gate.py, 0.1.0): all 27 plans pass every rights check (rights ceiling approved_for_sale) with no attribution warnings. The outcome is approved_for_private_use, capped by three sale-scope checks: no dataset scorecard score, no validation evidence ids in asset.json, and no owner approval.
- Owner approval is pending. build.py never sets it.
- The Data-Package Merchant still needs to re-score the triage dimensions. The figure in `evidence/scorer_cs.txt` is a builder self-assessment.
- Raw source files are not committed. `fetch_sources.py` downloads them and checks their hashes.
