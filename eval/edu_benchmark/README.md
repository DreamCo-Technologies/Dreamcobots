# Course-level eval packets — thin skeleton (SET7, draft)

Status: draft v0.1.1, proposed for review. **Nothing here is a mastery, certification, or production-readiness claim.** Every packet is in a pre-test state (`registered`/`unknown`) and has 0 evidence runs.
The packet format implements `SET7_COURSE_MASTERY_FLOORS_AND_HOLDOUT_POLICY.md` §2–§6, which lives in this directory.
Source files were read at `DreamCo-Technologies/Dreamcobots@2ccd678` (the Gap Planner workflow/script at `@5ba09f2`) and are byte-identical on main @5ba09f2. Each packet's `provenance` records the sha256 values.

```
python3 eval/edu_benchmark/validate.py --self-test                     # bridge checks SKIPPED (separate repo)
EDU_SCORECARDS_REPO=/path/to/edu-mastery-scorecards \
  python3 eval/edu_benchmark/validate.py --self-test                   # also runs the 12 bridge checks
python3 eval/edu_benchmark/gen_packets.py                              # regenerate packets from repo files (deterministic)
```

## Files
| File | What it is |
|---|---|
| `course_packet.schema.json` | JSON Schema (2020-12 subset) for a course packet: id/semver, track (`bootcamp`/`school_college`/`frontier_f_tier`), objectives, modules (prereqs, concepts), practice bank, **sealed holdout bank (reference only; no stems allowed)**, grader contract, fail-closed floors (+ `approved_lowering` log), `evidence_state` enum `unknown…mastered`, evidence run schema (run_id, fixture_hash, grader/subject version, timestamps, cost, latency, rep_index, safety/regression/assistance, simulated), provenance/rights, non-binding `repo_references`, `open_gaps`. |
| `bootcamp/BC-universal-1000-smoke.packet.json` | From `benchmarks/tasks/universal_1000_smoke.json`: 7 required capabilities → 7 units; the single public task is **practice only**; holdout bank empty placeholder. State `registered`. |
| `school_college/SC-example.packet.json` | **EXAMPLE** Intro Statistics (4 units). Every item is an `EXAMPLE-` placeholder; there are no real holdout items. State `unknown`; it can never be certified. |
| `frontier/F0.packet.json` | F0 skeleton. **F0–F4 are not defined in the repo**, so every numeric floor is `null` with TODO owners Grok-Buddy-F0-Scorecard / Frontier Loop Captain. Modules = 5 Q4 lanes of `config/frontier-evidence-suite.json` (training tasks = practice; holdout task IDs listed as IDs only). |
| `validate.py` | Stdlib validator (uses `jsonschema` if installed). Checks structure plus policy. `python3 validate.py --self-test` also runs 13 negative and 2 positive packet controls. With `EDU_SCORECARDS_REPO` / `--scorecards-repo` it adds 12 bridge/scorecards consistency checks; without it they are reported as SKIPPED. |
| `gen_packets.py` | Regenerates the 3 packets. It reads source files from the repo root (fallback: `$EDU_BENCH_SRC` or a `../repo_src` snapshot) and checks each one against a pinned sha256; any drift is recorded and warned, never silent. v0.1.1 also ingests the Benchmark Gap Planner artifact as pinned literal values, since the artifact is not in the repo; set `$EDU_GAP_QUEUE` to re-verify it. It copies only literal counts into non-binding `repo_references` plus one `open_gaps` entry and never touches `evidence_state`. It adds read-only edu-mastery-scorecards refs to F0. |
| `scorecard_mapping.json` | Field, floor, and state mapping to the edu-mastery-scorecards evidence card. Every value is cited to file:line. Floors use strictest-wins. Conflicts are listed, not resolved. |
| `scorecard_bridge.py` | Packet + evidence bundle → scorecards evidence card. Imports their `gate/cert_gate.py` read-only (separate repo; `EDU_SCORECARDS_REPO` or `--gate`) and reports our validator result, our policy cap, and their gate result. Never issues a certificate and never edits packets. Refuses frontier packets. |
| `bridge_examples/` | EXAMPLE bundle for the BC packet, the resulting card, and the bridge output (FAIL, as expected: 0 runs, no license/consent). |
| `ALIGNMENT_NOTES.md` | Gap Planner findings, scorecards comparison, conflicts, and owner decisions. |

## How floors and holdouts apply
- **All tracks:** `fail_closed: true`. Defaults: unit practice ≥0.90, exit mean ≥0.90, **no unit <0.80**, sealed holdout ≥0.90, ≥1 transfer task, **≥3 comparable reps** (same fixture_hash, grader_version, and subject_version), 0 critical regressions, retention retest at +7d before `mastered`. A floor can go higher. Going lower needs an `approved_lowering` record with a named human approver and a rationale, otherwise the validator fails the packet.
- **Holdouts:** `sealed: true`, stored only at a private path (a placeholder for now), with dual control. Forbidden uses: train, fine-tune, RAG, lessons, prompts, and practice. Items rotate weekly. Burned items are retired and replaced before any claim, and the isomorphism screen fails closed. Only aggregate scores are disclosed publicly. The validator rejects inlined holdout items, a practice bank that points at the holdout bank or store, and holdout or burned IDs reused as practice.
- **Bootcamp:** gets the 0.90 seed directly from the smoke suite. The public smoke task can never act as its own holdout.
- **School/college:** same floors. The human-learner evidence (PII) variant is still TODO.
- **Frontier F-tier:** null floors are allowed only on this track. They need `floors.todo.owners` and keep the packet in `unknown/registered/baselined/testing`, so it cannot pass or be mastered until the floors are defined.
- **States:** `mastered_candidate` needs ≥3 comparable non-simulated holdout reps that each pass the floors, plus a passing transfer run and an active holdout store. `mastered` also needs a retention run at least `retention_retest_days` after the gate.

## Open gaps and owners
1. **F0–F4 are undefined in the repo.** Decide whether they map to `buddy/frontier/frontier_competition_policy.json` `progression.stage_1..stage_5` or to the readiness gates G1–G7, then set numbers. Owners: Grok-Buddy-F0-Scorecard / Frontier Loop Captain.
2. **Threshold conflict.** `config/frontier-evidence-suite.json` has `score_threshold: 0.8`, which is below the SET7 0.90 floor. A human has to either raise it or record an approved lowering. Owners: Frontier Loop Captain + human owner.
3. **No sealed holdout content or store exists.** The private eval store path is not standardized (placeholder `eval/holdouts/`). The smoke suite has one public task and no holdout, and the per-lane graders plus grader versions and timeouts are not pinned. Owners: Bootcamp Commandant, Frontier Loop Captain, Grok-Edu-Benchmark-Planner.
4. **Benchmark Gap Planner has no data.** `benchmark-scores.json` is absent on main (404 @5ba09f2). Every scheduled "green" run (e.g. 37065929919, 37032509096 on 2026-10-02) reports 65/65 divisions as `RUN_BENCHMARKS` / "no measured evidence". Green means the job ran; no gaps were closed. The queue is keyed by MasterBot division, not course, and is uploaded as an artifact only (90-day expiry), never committed. Owners: Dreamcobots benchmark owners (unassigned).
5. **Scorecards F0–F4 naming collision and lower floors.** edu-mastery-scorecards F0–F4 are course evidence-card floors (0.00/0.70/0.80/0.80/0.80; F4 needs ≥30 days plus an independent evaluator). They are not frontier tiers and not adopted. Their gate also accepts lowered per-card floors, F0 certs, and duplicate bench IDs. See `ALIGNMENT_NOTES.md`. Owners: Grok-Edu-Mastery-Scorecards + Grok-Buddy-F0-Scorecard + human owner.
6. **Bridge prerequisites missing.** Packets have `provenance.license: null` and no consent record. Runs need `artifact_uri`, `artifact_sha256`, `evaluator`, and `leakage_check` (optional schema fields added in v0.1.1) before any card can pass their gate.
7. Smaller gaps: per-unit scores aren't emitted by `buddy_benchmark_runner.py`; there is no efficiency envelope per deployment tier; there is no human-learner evidence schema; no pilot school course or educator owner has been named.
