# Blind holdout grading kit (v2: rubric discrimination)

The kit is for the owner (Irean), currently the only available human grader. It checks whether the rubric, applied blind by a human, separates full-strength answers from subtly weakened ones. It has 16 new scenario prompts across 13 authored majors: 4 for Computer Science (11.0701), and 1 each for Computer Engineering, Registered Nursing, Psychology, Biology, Mechanical Engineering, Civil Engineering, Accounting, Marketing, Elementary Education, Chemistry, Statistics and Social Work.

The prompts and candidate answers were written for this kit only. They do not appear in the published study plans, `data/practice_tasks.json` or `authored/`, and a test checks that no 5-word run is shared. The candidate answers are not learner responses. Some are full-strength and some are subtly weakened on one rubric criterion. Every answer has the same shape: five labelled points of similar length. Length and layout tell you nothing.

**No grades have been entered. No holdout evidence exists until this sheet is filled in, declared final and scored.**

## Replacement note

The v1 kit (12 items drawn from the authored practice tasks, with `_key.json` in this folder) was deleted on 2026-10-02. It was not blind: its prompts and answers matched published content, and its key was committed and could be regenerated. The kit is not evidence, so replacing it does not affect the append-only evidence in `data/dreamco_knowledge/evidence/`.

## What is here

- `items.md`: the 16 items to grade. `items.json` has the same content.
- `grading_sheet.csv`: the blank sheet, one row per item.
- `KEY_COMMITMENT.txt`: the sha256 of the answer key. The key itself is kept by the builder outside the repository and is not in this folder or anywhere in the repo. The key contains a random 256-bit nonce, so the hash cannot be matched by guessing. Scoring refuses any key that does not match this hash, so the key cannot be changed after you grade.

## How to grade (about 60 to 75 minutes)

1. Read each item in `items.md`: the major, a scenario prompt, a candidate answer, and a 3-criterion rubric.
2. Score each criterion in `grading_sheet.csv`, judging only against that item's rubric:
   - 0: missing or wrong.
   - 1: partly there, vague, or with a real flaw.
   - 2: clearly and correctly covered.
3. Grade each item on its own merits. Do not try to balance scores across items or assume any particular number of weak answers.
4. Fill in `factually_correct` with `yes`, `no` or `unsure`. This is your judgment of whether the answer contains anything wrong for the field.
5. Use `comments` for anything you would change in the prompt, rubric or answer.
6. Put your name in `grader`, and the date and time in `graded_at` (ISO 8601 with offset, e.g. `2026-10-05T14:30:00-05:00`), on every row. Do not edit `item_id`, `major` or the criterion columns.
7. Optional: `python score_holdout.py` checks only that the sheet is complete and well formed. It prints no scores.
8. When you are done, create `GRADING_FINAL.txt` in this folder with one line:
   `FINAL: grader=<your name>; declared_at=<ISO date-time with offset>`
   After that, do not change the sheet.

Do not run `score_holdout.py --finalize` yourself, and do not look at its output before you have declared grading final.

## Scoring (builder, after GRADING_FINAL.txt exists)

```
python score_holdout.py --finalize --run-id <YYYYMMDD>-<NN>
python build.py      # links passing records into asset.json validation_evidence_ids.holdout
```

`--finalize` takes these steps:
1. It reads the private key.
2. It checks the key's sha256 against `KEY_COMMITMENT.txt`, and checks that `items.json` is unchanged.
3. It writes one record per asset with kit items: `holdout:<asset_id>:<run>` under `data/dreamco_knowledge/evidence/holdout/<asset_id>/`. Each record has source_type human_evaluation, transformation original_evaluation, and integrity_hash = sha256 of its results file.

## Pass rule

A record can pass only if the grader discriminated across the whole kit. Both of these must hold:

- **Detection rate ≥ 0.8.** A weakened item counts as detected when its weakened criterion is scored ≤ 1 and lower than the mean of that item's other two criteria.
- **Mean gap ≥ 1.0 on the 0-2 scale.** This is the mean of all criterion scores on full-strength items minus the mean of the weakened-criterion scores on weakened items.

Giving everything the same score (for example all 2s) detects nothing and fails every record.

Given kit-level discrimination, each asset's record also needs:
- Agreement ≥ 0.8. This is the fraction of its criterion scores inside the key's accepted band: 1-2 for full-strength criteria, 0-1 for the weakened criterion.
- No full-strength item judged factually incorrect.

The results file also reports, for majors that happen to have both answer types, how many weakened items scored below every full-strength item of that major. This is for information only.

## Limitations

There is one grader, and that grader is also the owner, so the result is not independent of DreamCo. There are few items per asset. The candidate answers were written by the builder, not by learners. The result shows whether the rubrics discriminate when a human applies them; it says nothing about learning outcomes.
