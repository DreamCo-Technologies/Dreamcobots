# ALIGNMENT_NOTES — Gap Planner + edu-mastery-scorecards (draft, 2026-10-02 CT)

edu-mastery-scorecards is a **separate teammate repo** (Grok-Edu-Mastery-Scorecards, @466e831). It is not vendored here, and nothing from it is committed apart from cited values and pinned sha256s. It was read and its tests were run **read-only**, either from a `/tmp` copy or with bytecode writes disabled. Its `git status` was unchanged before and after. Times below are CT unless marked Z.

## 1. Benchmark Gap Planner: what it really produces
- **Workflow** `.github/workflows/benchmark-gap-planner.yml@5ba09f2` (sha256 pinned in `gen_packets.py`). It runs on cron `7 * * * *`, on push, and on dispatch, with `permissions: contents: read` (L8-9). It has one step, `python3 tools/benchmark_gap_planner.py --scores benchmark-scores.json --out benchmark-gap-queue.json` (L17), then uploads that file as artifact `benchmark-gap-queue` (L18-21). **Nothing is committed to the repo.** Artifacts expire 2026-12-31.
- **Script** `tools/benchmark_gap_planner.py@5ba09f2`, last changed 2026-08-23. If the scores file is missing it uses `{"results":[]}` (L14). Every division 1..65 with no results becomes `RUN_BENCHMARKS / "no measured evidence"` (L21-23). `target` is read from the input. **The script defines no threshold of its own** (L25-29), it does not use `evidence_count`, and nothing in it is per-course or per-unit.
- **Input**: `benchmark-scores.json` returns **404 on main** at both 5ba09f2 and fc4493b, and no commit has ever touched that path.
- **Output (runs 37065929919 at 16:17 CT and 37032509096 at 11:13 CT)**: the two inner JSON files are byte-identical (sha256 `6d75a7ab…4676`). They contain `divisions: 65`, 65 queue items that are all `priority 0 / RUN_BENCHMARKS / "no measured evidence"`, and **0 items with a benchmark or score**. The policies read `"unknown is not failure"` and `"repeatable evidence required"`. The job log stdout is `{"divisions":65,"queue_items":65,"unmeasured_divisions":65}`.
- **"Green" means the job ran.** No gaps were closed and there are no scores. All 30 most recent scheduled runs (since 2026-09-26) are `success`. The cron is hourly, but the runs actually fire irregularly, every 2–7 h.
- **What I folded in** (`gen_packets.py` → BC + F0 packets): the artifact, workflow, and script are added to `provenance.sources` with hashes. The literal counts (`by_action`, `by_reason`, `items_with_benchmark_or_score: 0`) go in a non-binding `repo_references` entry. One `open_gaps` entry was added. **No `evidence_state` changed** (BC stays `registered`, F0 `unknown`, SC `unknown`). New validator rule (validate.py:25,142): a run whose `trace_ref`/`artifact_uri` cites the gap queue is rejected, because a work list is not a scored run.

## 2. edu-mastery-scorecards cert gate: rules (cited)
| Item | Their rule | Source |
|---|---|---|
| Unit | One card per (course, learner) | docs/EVIDENCE_CARD_SPEC.md:3 |
| F0 | Baseline diagnostic, min 0.00, no holdout | spec:15; examples/make_examples.py:14 |
| F1 | Practice, 0.70 | spec:16; make_examples.py:15 |
| F2 | Held-out, 0.80, held-out + leakage check | spec:17; make_examples.py:16 |
| F3 | Novel transfer + retest after remediation, 0.80, held-out | spec:18; make_examples.py:17 |
| F4 | F3 + regression retest ≥30 days later, evaluator independent of issuer, 0.80 | spec:19; make_examples.py:18; gate cert_gate.py:71-79 |
| Defaults | "per-course cards may raise them". The gate hard-codes no min_score and reads them from the card | spec:12; cert_gate.py:54,37 |
| Holdout | `bench.holdout == true` and `leakage_check.passed` (self-declared) | cert_gate.py:39-43 |
| Evidence | run_id, artifact_uri, 64-hex artifact_sha256, valid timestamp, score/max ≥ min | cert_gate.py:28-38; spec:6-8 |
| Claims | floor_attained must equal the highest supported floor; the cert floor cannot exceed it; cert bench IDs must resolve | cert_gate.py:92-113 |
| Provenance | Every source needs a license and consent | cert_gate.py:114-116 |
| Tracks | k12, stem, college, career, bootcamp | schema/course_evidence_card.schema.json:12 |

Their tests: `python3 -B -m unittest -v tests.test_cert_gate` → 9 run, 8 ok, 1 skipped (jsonschema not installed). This matches their tests/RESULTS.txt.

## 3. Conflicts (recorded, NOT resolved)
1. **Name collision.** Their F0–F4 are course-card floors, not the Buddy frontier tiers `frontier/F0.packet.json` is waiting on. F0 numeric floors **stay null**. Their values are recorded as non-binding refs.
2. **Floors are lower.** F1 0.70 and F2–F4 0.80 sit below SET7 0.90 (policy:52-54). They are not adopted into any packet.
3. **Their gate accepts weakening** (I probed a /tmp copy). A card that lowers F2 min_score to 0.1 passes with score 0.15. A certificate at F0 with a 0-score diagnostic passes, which is a vanity cert under SET7:80. Duplicate `bench_id`s collapse and the last one wins (cert_gate.py:49), which hides a failing rep.
4. **Reps.** Their gate has 1 result per bench. Ours needs ≥3 comparable reps (same fixture/grader/subject) (policy:55).
5. **Retention.** Their F4 needs ≥30 days plus an independent evaluator. Ours is +7d (policy:66,117), so our `mastered` does not imply their F4. SET7 also defines **no retention score floor**.
6. **Holdout discipline.** Their gate only checks a self-declared leakage flag. We require a sealed private store, dual control, weekly rotation, and burn-on-contamination (policy:91,99,104-106).
7. **no_unit_below 0.80, simulated, safety/regression.** Their gate cannot express these.
8. **Tracks/provenance.** Our `school_college` has no single match in their track list, and `frontier_f_tier` has none at all. All our packets have `license: null` and no consent, so every bridged card fails their gate today.

## 4. What our side now does (alignment)
- `scorecard_mapping.json` holds the field, floor, and state maps. Their defaults are cited per line, and the self-test checks them against their spec table. The card floor rule is **strictest-wins**: `max(their default, our packet floor)`. That gives F1–F4 = 0.90, and F4 days = max(30, 7) = 30. F0 keeps their 0.00 because a baseline is not a claim.
- `scorecard_bridge.py` (read-only import of their gate) maps only the largest comparable holdout group into `min_comparable_runs` slots. Unfilled slots stay `MISSING-*`, so their gate fails closed. A missing leakage_check counts as failed, and fixture_hash is never used as artifact_sha256. It computes **our policy cap**: store active, unit floor, safety/independence, transfer, and retention days. It flags `their_floor > our_cap` as a conflict (exit 1). The **certificate is always null** and status is never `certified`. It refuses frontier packets, duplicate run IDs, a missing learner, and school_college without an explicit card_track.
- Schema v0.1.1 (additive): run `bank` gains `baseline` and `remediation_retest`. Runs get optional `artifact_uri`, `artifact_sha256`, `evaluator`, and `leakage_check`.
- Validator: rejects a claim-state holdout rep with `leakage_check.passed=false` (validate.py:159) and rejects planner-queue runs. Self-test adds 2 negatives and 12 bridge checks (validate.py:225). I mutation-tested 3 of them by weakening the bridge, and they went red as expected.

## 5. Owner-only decisions
1. F0–F4 naming: do the scorecards course floors and the frontier tiers stay separate (rename one), or are they meant to be one ladder?
2. Accept strictest-wins (0.90) for bridged cards, or record an `approved_lowering` to their 0.70/0.80? (A human must approve.)
3. Should a retention/regression-retest **score** floor exist? The bridge applies holdout_min fail-closed as a placeholder.
4. Is the F4 30-day window to be adopted into SET7 (raising 7d), or is it scorecards-only?
5. Should their gate enforce default minimums, ban F0 certificates, and reject duplicate bench IDs? That is the teammate's repo, so this is a suggestion only.
6. Map `school_college` to which card track(s). Holdout semantics for transfer/retention benches (bridge marks them `holdout: true`).
7. Gap Planner: who creates `benchmark-scores.json`, and how do MasterBot divisions map to course packets? Should the queue be committed or kept artifact-only?
8. frontier-evidence-suite `score_threshold 0.8` vs 0.90 (unchanged, still pending).
