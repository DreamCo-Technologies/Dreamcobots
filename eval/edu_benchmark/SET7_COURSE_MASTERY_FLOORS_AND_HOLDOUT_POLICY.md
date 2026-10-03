# SET 7 — Course-Level Mastery Floors & Holdout Policy

**Owner:** Grok-Edu-Benchmark-Planner  
**Status:** Draft v0.1 (evidence-aligned; awaiting track lock)  
**Repos of truth overlay:** DreamCo-Technologies/Dreamcobots  
**Hard rule:** No vanity certs. Listing, routing, single passes, or weakened tests ≠ mastery.

---

## 1. Purpose

Define how a **course** (school/college pack, Bootcamp lesson track, or Buddy capability course) earns `mastered` / certifiable status — and how **anti-cheat holdouts** keep that claim honest.

Aligns to existing Dreamcobots contracts:
- `benchmarks/README.md` — promote only after configured mastery threshold repeatedly passed
- `docs/BENCHMARK_EVIDENCE_LIFECYCLE.md` — evidence states; no false mastery list
- `docs/BUDDY_1000_SOURCE_BOOTCAMP.md` — independent holdouts; weekly holdout rotation
- `benchmarks/tasks/universal_1000_smoke.json` — `mastery_threshold: 0.9` (smoke suite seed)
- Frontier harness / evidence plan — 3+ comparable reps; separate holdout; no catalog-as-proof

---

## 2. Course packet (unit of certification)

Every certifiable course MUST ship as a versioned packet:

| Field | Required |
|-------|----------|
| `course_id` + semver | yes |
| Learning objectives (observable) | yes |
| Module map (prereqs → modules → exit gate) | yes |
| Practice item bank (train/practice only) | yes |
| **Holdout item bank** (gate-only; sealed) | yes |
| Rubric / grader contract | yes |
| Mastery floors (below) | yes |
| Evidence schema (run id, fixture hash, grader version, cost/latency) | yes |
| Provenance / rights note | yes |

Normalization (from AI course system):  
`course → module → concept → prerequisite → example → exercise → assessment → mastery`

---

## 3. Mastery floors (course-level)

Floors are **gates**, not aspirational targets. Fail-closed.

### 3.1 Numeric floors (seed from repo; course may raise, never silently lower)

| Gate | Floor | Basis |
|------|-------|--------|
| **Unit practice bar** | ≥ configured unit threshold on practice bank | Default seed **0.90** (from `universal_1000_smoke.json`) unless course packet declares a higher bar with rationale |
| **Course exit (practice composite)** | ≥ 0.90 mean across required units; **no unit below 0.80** | Prevents averaging away a weak unit |
| **Holdout / transfer gate** | ≥ 0.90 on sealed holdout set **and** ≥ 1 novel transfer task at pass | Bootcamp mastery gate + education engine |
| **Repeatability** | Holdout+exit pass on **≥ 3 comparable runs** (same fixture/grader/timeout/assistance policy) | Frontier evidence plan |
| **Regression** | Zero **critical** regressions on dependent mastered courses/capabilities | Bootcamp + frontier harness |
| **Efficiency (deployment tier)** | Cost/latency within course packet's declared tier envelope | Bootcamp mastery gate |
| **Trust/safety (when applicable)** | Trust suite clean for the course's risk class | Bootcamp + Trust Framework |

### 3.2 Qualitative floors (education engine)

Mastery also requires evidence of:
1. **Repeated success** (not one lucky pass)
2. **Novel variants** (paraphrase / isomorphic items)
3. **Transfer** (new context, not memorized stem)
4. **Retention** (spaced retest window — default 7d for course exit claim)
5. **Regression evidence** (related modules still green)

### 3.3 Forbidden as mastery evidence

From `BENCHMARK_EVIDENCE_LIFECYCLE.md` / Bootcamp (non-exhaustive):
- source registered or downloaded
- model route exists / frontier model did the work for Buddy
- single lucky pass
- “looks good” without required artifacts
- faster/cheaper but less correct or unsafe
- pass obtained by **weakening** the test
- catalog size, mocked rows, harness-only green

**Vanity cert ban:** No `certified` / `mastered` / `production-proven` label without sealed-holdout + repeatability evidence attached.

---

## 4. Anti-cheat holdout policy

### 4.1 Separation of banks

| Bank | Use | Visibility |
|------|-----|------------|
| Practice | lessons, drills, adaptive samples | may be in train/retrieval |
| **Holdout** | course exit, promotion, cert | **sealed** — never in train, fine-tune, retrieval, or lesson text |
| Golden / historical | regression & longitudinal | versioned; prior versions kept when items change |

### 4.2 Sealing rules

1. Holdout prompts and expected checks live in a **private evaluation store** (per Frontier Evidence Plan).
2. Holdout answers MUST NOT appear in prompts, RAG, Bootcamp lessons, or training sets.
3. Graders are deterministic where possible; judge models require de-correlated panel + disclosed policy.
4. Creating/editing a holdout item requires dual control (owner agent + human or second cert agent) before unseal for a gate run.
5. After a gate run, **do not** publish raw holdout stems publicly; publish aggregate scores + evidence refs only.

### 4.3 Rotation & contamination

- **Weekly:** rotate a subset of active holdouts (Bootcamp cadence).
- **Contamination event:** if a holdout stem is found in train/practice/logs → mark item `burned`, retire from gate use, replace before any cert claim.
- **Isomorphism check:** new practice items must be screened for near-duplicate overlap with holdouts (fail-closed on high similarity).

### 4.4 Gate run protocol

```
freeze course packet version
 → draw sealed holdout set (versioned)
 → run ≥3 comparable reps
 → score vs floors
 → attach traces, fixture hashes, grader versions, cost/latency
 → if pass: mastered_candidate
 → retention retest (default +7d) → mastered
 → else: diagnose → remediate on PRACTICE only → never train on holdout
```

### 4.5 Learner / Buddy / adapter scope

Same floors apply whether the subject is a **human learner**, **Buddy adapter**, or **fleet bot** — only the evidence schema fields differ (PII handling for humans; model/tool config for bots).

---

## 5. Alignment to F0 / edu scorecards

| Layer | Role | Relationship to this policy |
|-------|------|------------------------------|
| **Course mastery floors (this doc)** | School/college + Bootcamp course packets | Certifies *learning packages* |
| **Buddy F0–F4 frontier floors** (F0 Scorecard / Frontier Loop) | Frontier capability claims vs peers | Must consume the same holdout discipline; F0 cannot claim frontier on practice-only greens |
| **Platform / readiness scorecards** | Product certification | May require course packs green as inputs; never substitute for holdout |
| **Universal Education Engine** | Pedagogy loop | Supplies qualitative mastery criteria (transfer, retention) |
| **500-model / trust suite** | Safety before promotion | Hard gate when course risk class requires it |

**Alignment rule:** Any F0/edu scorecard cell that says `mastered` / `certified` MUST link to a course packet evidence bundle satisfying §3–§4. Scorecard color without bundle = invalid.

---

## 6. Evidence states (course)

`unknown → registered → baselined → testing → passed/failed/blocked → repair → retest → mastered_candidate → mastered`

Regression demotes to investigation. Dashboard may show aggregates; secrets and raw holdouts stay out of public Pages.

---

## 7. Immediate gaps (honest)

| Gap | Notes |
|-----|-------|
| No dedicated `docs/COURSE_MASTERY_FLOORS.md` in repo yet | This draft is the candidate |
| Smoke suite has `mastery_threshold: 0.9` but not a full course packet schema | Need YAML/JSON schema next |
| F0 numeric floors not fully enumerated in fetched frontier harness (vector scores, not single %) | Coordinate with Grok-Buddy-F0-Scorecard |
| Private holdout store path not standardized in Dreamcobots | Propose `eval/holdouts/` (private) + public evidence refs |

---

## 8. Next actions

1. Lock first track (Bootcamp lesson / school-college / F0 floors / thin skeleton).
2. Land this file under `docs/` in Dreamcobots (or Empire HQ plan path) after owner approval.
3. Add `course_packet.schema.json` + one exemplar course (Bootcamp smoke → full packet).
4. Sync F0 scorecard cells to require holdout evidence refs.
5. Message Bootcamp Commandant + F0 Scorecard for dual-sign on holdout rotation owners.

---

## 9. Change control

Numeric floors may **increase** with evidence. Lowering a floor or shrinking a holdout requires explicit human approval and a recorded rationale. Silent weakening = policy violation.
