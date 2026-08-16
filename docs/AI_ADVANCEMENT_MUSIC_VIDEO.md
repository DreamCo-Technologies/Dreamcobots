# DreamCo AI Advancement: Music & Video

DreamCo should use the open ecosystem as a research classroom, not as a template to copy.

## Reference → Capability → Benchmark → Original system

```text
Public research / open-source references
            ↓
     capability extraction
            ↓
 license + provenance check
            ↓
 DreamCo capability definition
            ↓
 DreamCo benchmark + holdout
            ↓
 independent implementation
            ↓
 sandbox experiments
            ↓
 failure analysis
            ↓
 measurable improvement
            ↓
 reusable capability
```

## Why benchmarks matter

Modern media benchmarks are becoming much more diagnostic. MovieGen Bench includes 1,003 video prompts and 527 audio/video examples, while VABench evaluates synchronized audio-video generation across 15 dimensions. citeturn0search0turn0search1

Newer evaluations also target the weaknesses that matter for professional production: FilmBench emphasizes professional cinematic language and multi-shot filmmaking; AVGen-Bench evaluates task-driven audio-video generation; and FlatSounds tests whether generated audio reflects physical processes rather than merely sounding plausible. citeturn0academia23turn0search4turn0search8

DreamCo should therefore create additional tests for gaps that existing benchmarks do not capture.

## DreamCo research goals

### Music

- controllable songwriting
- long-form structure
- arrangement consistency
- expressive performance
- editable stems
- mixing/mastering assistance
- emotional intent control
- production workflow automation
- lower cost and latency
- stronger human preference

### Video

- persistent characters
- multi-shot continuity
- director-style control
- cinematic language
- story continuity
- physical reasoning
- object-state consistency
- synchronized sound
- long-form editing
- automated production workflows

## Originality rule

The objective is not to reproduce another system's internal implementation. We compare **capabilities and outcomes** and then build DreamCo implementations that are independently designed or compliant with the applicable license.

When an external project has a permissive license, DreamCo may use it according to that license. When a project has restrictive terms, DreamCo should not copy its protected code or assets merely because they are technically useful.

## Advancement loop

A benchmark score is the beginning of a research question:

> What prevents us from reaching the next percentage point?

Buddy should categorize the failure, propose experiments, test candidates in a sandbox, evaluate on hidden holdouts, run regression tests, and preserve the evidence.

The goal is not to stop when DreamCo matches an existing system.

**Match → understand the gap → improve the capability → create a harder benchmark → advance the field.**

## Long-term target

Build an open, measurable media-production stack where researchers and developers can see exactly which capabilities work, which fail, and where new research can make AI music and video production meaningfully better.
