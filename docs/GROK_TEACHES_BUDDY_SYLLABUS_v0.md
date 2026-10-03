# Grok → Buddy Teacher Curriculum (v0)

**Owner lane:** Grok-Buddy-Teacher-Curriculum  
**Tied to:** Buddy Bootcamp levels + vs500 / F0–F4 floors  
**Sources (repo truth):** `config/buddy-bootcamp-program.json`, `buddy/bootcamp/buddy_bootcamp.yaml`, `config/buddy-bootcamp-curriculum-v1.json`, `reports/BUDDY_FRONTIER_MODEL_AND_PACKAGES.md` §2, `docs/BUDDY_BOOTCAMP_AND_TRUST_FRAMEWORK.md`, `config/pass-all-500-benchmarks.json`

## Non-negotiables

- Sources are teachers, not runtime authority.
- Graduation = repeat pass + holdout + no regression + fresh evidence (curriculum-v1 mastery).
- Log every teacher assist (cost/latency/external-assist) — F0+.
- Never claim frontier from catalog size; F2+ evidence required for claimed scope.
- vs500 = Buddy scored against owner 500-model registry peers on same fixtures; missing evidence ≠ pass.

## Axis A — Bootcamp levels (what Buddy is becoming)

| Level | Goal (from program.json) | Grok teacher role |
| --- | --- | --- |
| recruit | Identity, mission, boundaries, I/O contract | Teach canonical bot card, promise, deny-lists, “when to refuse” |
| fundamentals | Deterministic fixtures + failure modes | Socratic failure clinics; short original lessons from fixture fails |
| specialist | Domain hard cases, O*NET/workflows, packs | Domain walkthroughs → DreamCo-original practice tasks |
| operator | Multi-step tools, retries, permissions, recovery | Tool-selection + recovery playbooks; injection/rate-limit drills |
| competitor | Same-fixture vs open-weight / catalog peers | Gap analysis vs vs500 peers; remediations ranked by gain/min |
| elite | Mixed load, cost/latency, low user effort | Efficiency coaching; long-horizon mission critique |
| instructor | Teach others; generate fixtures; no duplicate systems | Meta-teaching: lesson/fixture/rubric authoring standards |
| graduated | DoD + guardrails + prod observation | Evidence packet review only; no “waive” teaching |

## Axis B — Frontier floors F0–F4 (how strong the claim may be)

| Floor | Pass condition | What Grok may teach | What Grok must stop doing |
| --- | --- | --- | --- |
| F0 Baseline | Pinned suite + cost/latency/assist logged under `evidence/frontier/` | How to run/read scorecards; classify failures into Bootcamp gaps | Claiming peer parity |
| F1 Peer parity | Beat designated peers on held-out tasks in ≥1 lane | Targeted remediation for that lane; teacher solutions as *study*, not answers | Multi-lane “frontier” language |
| F2 Multi-lane | Competitive on ≥4 lanes incl. coding + reasoning + tools + safety | Cross-lane transfer lessons; trust-suite coupled drills | Skipping holdout/regression |
| F3 Broad | Competitive across matrix vs strong baselines | Variance-aware coaching; methodology for CIs / published harness | Overfit to one fixture family |
| F4 Native distillation | Recurring teacher solutions reproduced with lower external dependency | Distill recurring Grok patterns into Buddy-native adapters/lessons; before/after evidence | Deleting teacher fallbacks / catalog |

## Axis C — vs500 benches (who Buddy is scored against)

Wave framing from `pass-all-500-benchmarks.json`: A-catalog → B-local-free → C-paid-hosted → D-blocked-honest.

| Bootcamp level | Primary vs500 use | Teacher (Grok) deliverable |
| --- | --- | --- |
| recruit–fundamentals | Smoke subset of A-catalog fixtures | Failure taxonomy + next lesson card |
| specialist–operator | Domain + tool lanes vs peers | Original practice + sandbox task + rubric |
| competitor–elite | Full same-fixture peer compare | Gap→Bootcamp gain plan with expected Δ score |
| instructor–graduated | Package export + regression | LP/RP/CP-ready lesson packs with provenance |

## Daily teacher loop (maps Bootcamp YAML stages)

1. diagnose (benchmark history / vs500 delta)  
2. select_resource (highest expected gain per minute)  
3. study (Grok original explanation; no copyrighted reproduction)  
4. sandbox (Buddy exercises alone)  
5. targeted_benchmark  
6. holdout  
7. regression  
8. promote (or remediate)

Study budget default: 30 minutes/cycle (`buddy_bootcamp.yaml`).

## Per-tier syllabus packets (v0 outline)

Each packet must include training_unit fields from curriculum-v1:  
`capability_id, objective, lesson, practice, sandbox_task, transfer_task, rubric, benchmark, provenance`

### T0 — F0 × recruit/fundamentals
- Teach: scorecard literacy, trust-suite smoke, identity/boundaries  
- Bench: F0 pinned suite + Bootcamp static/unit labs  
- Exit: logged baseline evidence packet

### T1 — F1 × specialist (one lane)
- Teach: one frontier lane (pick coding *or* reasoning *or* tools) to peer parity  
- Bench: held-out vs designated catalog peers  
- Exit: signed single-lane scorecard

### T2 — F1→F2 × operator + competitor
- Teach: tool use + recovery + coding + reasoning + safety coupled  
- Bench: ≥4-lane competitive vs500 subset  
- Exit: multi-lane scorecard; no production_ready claim yet

### T3 — F2→F3 × elite
- Teach: long-horizon, cost/latency pressure, multimodal if in matrix  
- Bench: evaluation_matrix.md lanes vs strong baselines  
- Exit: published methodology stub + variance notes

### T4 — F4 × instructor
- Teach: distill recurring Grok solutions → Buddy-native lessons/adapters  
- Bench: before/after + holdout + regression; lower external-assist rate  
- Exit: distillation evidence; teachers retained as fallback

## Gaps to close next (honest)

1. No dedicated `teacher-curriculum` config yet — this doc is the seed.  
2. vs500 owner bot (Grok-Buddy-Vs500-Bench) owns live runs; this lane owns *what to teach* after fails.  
3. Need lane→lesson ID mapping into Bootcamp engine (`tools/bootcamp_lesson_planner.py` / `buddy_bootcamp_engine.py`).  
4. Need explicit “assist logging” schema shared with Distill Lead / F0 Scorecard.

## Handoffs

| Teammate | Ask |
| --- | --- |
| Bootcamp Commandant | Lesson IDs / engine hooks for T0–T4 packets |
| Vs500 Bench | Fixture lists per floor for teacher remediations |
| F0 Scorecard | Evidence packet shape for teacher exits |
| Distill Lead | F4 native reproduction acceptance tests |
