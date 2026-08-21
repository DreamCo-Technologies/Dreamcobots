# DreamCo Flagship: Build Your Own AI

## Product thesis

DreamCo's flagship product is a user-owned, personalized AI workspace. A customer creates an AI identity that can be shaped by authorized personal knowledge, conversations, files, images, audio, video, and skills while remaining model-agnostic.

The goal is not to retrain a frontier foundation model from scratch for every customer. The goal is to build a durable personal intelligence layer around replaceable foundation models.

## Core promise

**Your AI. Your memory. Your knowledge. Your skills. Your model choices.**

A user's personality, memories, knowledge, preferences, workflows, and skill evidence should remain portable when the underlying model changes.

## Product architecture

```text
User
  |
  v
Buddy Personal AI Manager
  |
  +--> Identity & Personality
  +--> Consent & Data Permissions
  +--> Personal Memory
  +--> Knowledge Vault
  +--> Skill Library
  +--> Conversation Learning
  +--> Model Router
  +--> Tool/Integration Router
  +--> Superbot Builder
  +--> Evaluation & Regression
  |
  v
Personal AI Runtime
  |
  +--> low-cost models
  +--> premium models
  +--> local/open models
  +--> future providers
  |
  v
Outcome + Evidence
  |
  v
Learning / Evaluation Loop
```

## Training modes

### 1. Knowledge ingestion

Users can add authorized content such as:

- documents and PDFs
- books they own or are licensed to process
- photos and images
- audio and voice recordings
- videos they have rights to process
- notes and structured data
- approved websites and knowledge sources
- business/company material

Content should be indexed with provenance, source identity, timestamps, permissions, and deletion/export controls.

### 2. Conversation learning

Buddy can learn from conversations only according to explicit user settings:

- Always learn
- Ask before learning
- Never learn
- Learn selected parts only

Important memories should be promoted only after validation; raw conversation history must not automatically become permanent truth.

### 3. Skill learning

A user can teach a skill by providing examples, instructions, demonstrations, tests, and success criteria. Skills become reusable packages with:

- capability contract
- examples
- tools
- permissions
- benchmark tasks
- evaluation results
- regression tests
- provenance
- version
- promotion state

### 4. Personalization

Buddy should model:

- communication preferences
- preferred formats
- recurring workflows
- domain expertise
- goals
- approved preferences
- successful strategies

Sensitive information must remain governed by explicit permissions and retention controls.

## Model independence

The personal intelligence layer must not be tied permanently to one provider. Buddy should route each task based on capability, quality evidence, cost, latency, privacy, availability, and user plan entitlements.

A premium model must never be silently charged. Paid model use requires the appropriate account entitlement and explicit authorization where required by policy.

## Self-improvement loop

```text
Task
 -> classify
 -> retrieve personal context
 -> select skill
 -> select model
 -> execute
 -> evaluate
 -> record evidence
 -> regression test
 -> promote successful strategy
 -> improve future routing
```

"Learning" means measurable improvement, not merely storing more text.

## User controls

Every personal AI must provide:

- data source inventory
- per-source permissions
- learning controls
- memory review/edit/delete
- export
- account deletion
- model usage visibility
- cost/usage visibility
- skill version history
- provenance for learned knowledge
- reset/revert controls

## Flagship customer journey

1. User creates a Personal AI.
2. Buddy asks what the AI should help accomplish.
3. User chooses personality and learning preferences.
4. User adds authorized knowledge and media.
5. Buddy indexes and validates the material.
6. User teaches initial skills.
7. Buddy runs benchmark tasks.
8. Successful capabilities are promoted.
9. Buddy begins personalized routing.
10. User reviews progress and controls what is learned.

## Monetization architecture

Buddy should be able to explain plans, compare capabilities, obtain explicit purchase confirmation, and initiate the supported checkout flow. Subscription entitlements then control available model tiers, storage, memory, media processing, automation, and Superbot capacity.

Recommended entitlement categories:

- personal AI count
- knowledge storage
- media processing capacity
- conversation-memory capacity
- skill count
- Superbot count
- automation capacity
- model tier access
- premium-model budget
- API/integration access
- team seats

## Product moat

The durable asset is the user's portable intelligence layer:

**identity + memory + knowledge + skills + evidence + workflows + preferences**

Foundation models remain replaceable infrastructure.

## Safety and rights

DreamCo must only ingest, retain, transform, or use content where the user has the necessary rights and permissions. Copyrighted books, movies, music, and other media do not become authorized merely because a user uploads them. The platform should preserve provenance and support deletion.

## Engineering direction

Do not create a new bot for every feature. Prefer a small number of Superbots and shared services:

- Personal AI Manager
- Model Router
- Knowledge/Memory Service
- Skill Builder
- Evaluation/Benchmark Engine
- Tool/Integration Router
- Billing/Entitlement Service
- Governance/Consent Service

This flagship should reuse and consolidate the existing Buddy model-routing, memory, benchmark, local-repository, success-policy, and learning infrastructure rather than duplicating it.

## Success metrics

Track:

- task success rate
- user acceptance rate
- correction rate
- repeat-task improvement
- retrieval accuracy
- skill benchmark score
- regression rate
- cost per successful task
- latency
- premium-model utilization
- user retention
- personal AI activation rate
- paid conversion

The north-star metric is **successful personalized outcomes per dollar of infrastructure/model cost**.
