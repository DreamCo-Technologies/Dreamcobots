# Blind holdout grading kit (v1)

This kit is for the owner (Irean), currently the only available human grader. Its purpose is an independent human check of 12 authored practice items: does each rubric work, and do the graded answers hold up? **No grades have been entered. No holdout evidence exists until this sheet is filled in and scored.**

## What to open, and what not to open

- Open only `README.md` (this file), `items.md` (or `items.json`) and `grading_sheet.csv`.
- **Do not open `_key.json` or `make_holdout_kit.py`.** They contain the answer key.
- While grading, do not look at `study_plans/`, `data/practice_tasks.json` or `authored/`. They contain the reference answers and would unblind you.

## How to grade (about 45 to 60 minutes)

1. Read each item in `items.md`: a scenario prompt, a candidate answer in outline form, and a 3-criterion rubric.
2. Judge the candidate answer only against that item's rubric. Answers are short outlines, so judge whether the content is there and correct, not polish or length. Some answers are deliberately weaker than others, and you are not told which.
3. In `grading_sheet.csv`, give each criterion a score:
   - 0: missing or wrong.
   - 1: partly there, or vague.
   - 2: clearly and correctly covered.
4. Fill in `factually_correct` with `yes`, `no` or `unsure`. This is your judgment of whether anything in the answer is wrong for the field (for example, a wrong drug-safety statement or wrong accounting treatment).
5. Use `comments` for anything you would fix in the prompt, the rubric or the answer.
6. Put your name in `grader` and the date and time in `graded_at` (ISO 8601 with offset, e.g. `2026-10-05T14:30:00-05:00`) on every row.
7. Save the CSV. Do not change `item_id` or the criterion columns.

## Scoring after grading (builder side)

```
python score_holdout.py --sheet evidence/holdout_kit/grading_sheet.csv            # dry run: prints results
python score_holdout.py --sheet evidence/holdout_kit/grading_sheet.csv --write    # writes holdout evidence records
python build.py                                                                    # links passing records into asset.json
```

`score_holdout.py` refuses an incomplete sheet. It also refuses if any kit item was edited after the kit was drawn, and it compares your scores with the sealed key. It writes one record per study plan that has items in the kit, `holdout:<asset_id>:<YYYYMMDD>-<NN>` under `data/dreamco_knowledge/evidence/holdout/<asset_id>/`. Each record has source_type `human_evaluation` and transformation `original_evaluation`, and its integrity_hash is the sha256 of the results file. The records follow `config/evidence_provenance_schema.json`.

Limits: one grader, 12 items, and the grader is also the owner, so this is not independent of DreamCo. The records say so.
