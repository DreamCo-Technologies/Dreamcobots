# Data dictionary: DreamCo Occupation Synthesis Pack (built with O*NET® 31.0 data), version 0.0.2

Internal SKU id: `DP-ONET-OCC-SYN` (internal identifier only; a buyer-facing id will be decided before any listing).

File: `sample/occupations.jsonl` (one JSON object per line, UTF-8). Schema: `schemas/dp_onet_occ_syn.row.schema.json`.
Origin: **O*NET®-derived** = O*NET® 31.0 Database value (CC BY 4.0, USDOL/ETA), possibly ranked or rounded; **DreamCo** = DreamCo-derived.

| Field | Type | Origin | Description / allowed values |
| --- | --- | --- | --- |
| `record_id` | string | DreamCo | `dp-onet-occ-syn/<package_version>/<onet_soc_code>` |
| `sku_id` | string | DreamCo | `DP-ONET-OCC-SYN` |
| `package_version` | string | DreamCo | Package version, e.g. `0.0.2` |
| `source_version` | string | DreamCo | `O*NET 31.0` (must equal the pin) |
| `onet_soc_code` | string | O*NET®-derived (`occupation_data.csv` O*NET-SOC Code) | `NN-NNNN.NN` |
| `onet_title` | string | O*NET®-derived (`occupation_data.csv` Title) | Occupation title as published |
| `soc_major_group` | string | DreamCo (code prefix) | First two digits of the code (2018 SOC major group) |
| `job_zone` | integer | O*NET®-derived (`job_zones.csv`) | 2-5 in 31.0 (2 = "Job Zone 1-2") |
| `preparation_band` | enum | DreamCo | `little_to_some` (zones 1-2), `medium` (3), `considerable` (4), `extensive` (5) |
| `top_knowledge[]` | array of {element_id, element_name, importance} | O*NET®-derived (`knowledge.csv`, scale IM) | Top 5 by importance 1-5, suppressed ratings excluded |
| `top_essential_skills[]` | same | O*NET®-derived (`essential_skills.csv`, 2.A.*, IM) | Top 5 (31.0 Essential Skills; Transferable Skills not used) |
| `top_work_activities[]` | same | O*NET®-derived (`work_activities.csv`, 4.A.*, IM) | Top 5 |
| `task_counts` | {core, supplemental, unclassified} | O*NET®-derived (`task_statements.csv` Task Type) | Counts only; no task text |
| `capability_lenses` | {4 lenses: number 0-1} | DreamCo over O*NET® IM | Mean IM of the DreamCo-grouped 4.A.* activities, (mean-1)/4 |
| `lens_lift` | {4 lenses: number -1..1} | DreamCo | Lens score minus the all-occupation mean for that lens |
| `dominant_lens` | enum | DreamCo | Lens with the largest lift: `information_and_analysis`, `people_and_communication`, `physical_and_equipment`, `digital_and_records` |
| `knowledge_lens` | enum | DreamCo | Lens with the largest summed lift of the top knowledge elements over their all-occupation means |
| `data_confidence` | object | DreamCo over O*NET® metadata | `band` high/medium/low (medium if any ranked rating is before 2021-01 or >3 suppressed; low if before 2017-01 or >10), `min_n`, `suppressed_ratings_excluded`, `rating_sources` (O*NET® Domain Source values), `oldest_rating`/`newest_rating` (YYYY-MM) |
| `dreamco_synthesis.practice_task_seed` | string | DreamCo (template; embeds O*NET® names) | Scenario drill prompt |
| `dreamco_synthesis.rubric_dimensions[]` | strings (3-8) | DreamCo | Grading dimensions for the drill |
| `dreamco_synthesis.analysis` | {agree, caveats, improve, still_need_test} | DreamCo | Data-driven notes (lens agreement, stale ratings, suppressed ratings, small N, preparation framing) |
| `dreamco_synthesis.evidence_perspectives[]` | strings | DreamCo over O*NET® metadata | Distinct O*NET® rating sources behind the ranked values |
| `source_refs[]` | objects | DreamCo | Per-field provenance: `source_id`, `version`, `file`, `file_sha256` (O*NET® member pin), `keys` (code / element / scale), `fields` covered; the `dreamco_synthesis` entry names the generator |
| `license` | object | DreamCo | Field-level split (`onet_derived_fields`, `dreamco_fields`), licenses and the attribution pointer |

Lens groupings (DreamCo's judgment, documented in `tools/build_dp_onet_occ_syn_sample.py`): information and analysis = 4.A.1.*, 4.A.2.*;
people and communication = 4.A.4.a.*, 4.A.4.b.*; physical and equipment = 4.A.3.a.*, 4.A.3.b.2/4/5; digital and records = 4.A.3.b.1,
4.A.3.b.6, 4.A.4.c.*. Knowledge (2.C.*) uses a parallel DreamCo grouping in the same file.

`sample/occupation_cards.md` renders the same rows for people and ends with the full attribution text.
