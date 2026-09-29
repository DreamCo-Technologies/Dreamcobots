# Edu Career Pathways: majors to O*NET study plans

Maps 27 common bachelor's majors (2020 CIP codes) to O*NET-SOC occupations using the official O*NET CIP crosswalk, then writes one study plan per major with the highest-importance O*NET knowledge areas and foundational skills plus a 4-year outline (the outline is DreamCo-derived guidance).

Fetch pinned sources: `python fetch_sources.py` (verifies sha256). Rebuild: `python build.py` (needs pandas, openpyxl). Test: `pytest tests`.
Outputs: `data/major_to_onet.csv`, `data/majors_selected.json`, `study_plans/*.md`. Sources and hashes: `raw/SOURCES.md`.

## Status and open items

- Built on O*NET 31.0 (current release). The fleet O*NET ingest is pinned to 30.3, and alignment is an open decision.
- Raw source files are not committed. `fetch_sources.py` downloads them and checks their hashes.
