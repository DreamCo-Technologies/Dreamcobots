# Media, Digital Actor & Game Capability Roadmap

DreamCo should treat creative AI as another capability family, not a separate collection of disconnected bots.

## Phase 1 — Core media primitives

- audio transcription
- speech synthesis
- consented voice cloning
- audio restoration
- image generation/editing
- video generation/editing
- image/video analysis
- captioning and localization

## Phase 2 — Production pipelines

- storyboard → assets → scenes → timeline
- script → dialogue → voice → animation
- image → character sheet → consistent scenes
- audio → cleanup → mix → master
- video → edit → effects → captions → export

## Phase 3 — Digital actors

Build controllable synthetic characters with explicit provenance and authorization controls:

- appearance
- voice
- facial expression
- body movement
- dialogue
- scene interaction
- performance direction
- localization

The system should distinguish a fictional DreamCo-created character from an authorized digital representation of a real person.

## Phase 4 — Games

Build an end-to-end game laboratory:

```text
Idea
 ↓
Game design
 ↓
Prototype
 ↓
Code generation
 ↓
Asset generation
 ↓
NPC/agent behavior
 ↓
Automated playtesting
 ↓
Balance/performance evaluation
 ↓
Regression testing
 ↓
Build/package
```

## Phase 5 — Benchmarking

Every creative capability receives percentages for relevant dimensions:

- quality
- task success
- consistency
- controllability
- generalization
- latency
- cost
- safety
- provenance
- regression stability

## Phase 6 — Buddy composition

A user should eventually be able to request:

> “Build me a game trailer with an original cast, voices, environments, music, sound effects, captions and a playable prototype.”

Buddy should decompose that request into capabilities, select appropriate tools/models, run them in a sandbox, benchmark the outputs, identify failures, and iterate.

## Guardrails

Real-person voice/likeness workflows must require authorization/consent and provenance. Synthetic media should be clearly represented as synthetic where disclosure is appropriate. DreamCo should not build identity-cloning workflows whose purpose is fraud, impersonation, or evasion.

## Long-term vision

The same capability graph should power:

**chat + coding + research + audio + image + video + digital actors + games + robotics + business automation + education + scientific workflows.**

The implementation should remain modular so improvements in one capability can benefit many products.
