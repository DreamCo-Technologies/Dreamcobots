# O*NET task index

This directory stores a compact, versioned index of public O*NET task statements for Buddy's internal study queue.

- Source: official O*NET Database task-statements export.
- License: CC BY 4.0, with attribution to O*NET and the U.S. Department of Labor, Employment and Training Administration.
- Generator: `tools/build_onet_task_index.py`.
- Refresh workflow: `.github/workflows/buddy-onet-task-index-refresh.yml`.
- Runtime: `buddy.learning.course_track_registry` loads task-level assignments only when `onet-task-index.json` passes its release, row-count and identity checks.

A task-index row is not a completed study guide. Each task still requires an original detailed guide, practice, task-specific AI/human suitability review, acceptance tests, an unseen assessment and reviewer evidence. The index does not establish occupational competence, licensing, job placement or authority to perform regulated work.
