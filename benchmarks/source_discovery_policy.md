# Buddy Autonomous Source Discovery

Buddy must be able to discover new learning sources instead of depending on a fixed list or waiting for a human to name one.

## Discovery triggers

- a capability gap is detected
- a benchmark failure identifies missing knowledge
- a user asks Buddy to learn a subject
- a user asks Buddy to perform a task Buddy cannot yet perform reliably
- an existing source becomes stale
- a new technology or standard is detected
- a repository scan finds an unfamiliar dependency/pattern
- another benchmark identifies a stronger authoritative source

## Discovery process

`goal -> capability gap -> source query -> candidate collection -> authority ranking -> redundancy check -> access/terms check -> source approval policy -> adapter creation -> ingestion -> benchmark generation -> sandbox -> mastery`

## Candidate ranking

Score candidates using:

- authority
- primary/official status
- relevance to the gap
- uniqueness
- evidence quality
- freshness
- accessibility
- reproducibility
- licensing clarity
- benchmark potential
- practical examples
- cross-domain transfer value

## Asking ChatGPT for help

When Buddy cannot find enough authoritative sources using its own authorized discovery tools, it may create a **source research request** for an external research assistant such as ChatGPT. The request must contain:

- learning goal
- detected capability gap
- current sources searched
- rejected candidates and reasons
- desired source type
- required authority level
- access/terms constraints
- output format required for ingestion

ChatGPT's suggestions are treated as **candidate sources**, never automatically trusted facts. Buddy verifies every candidate through its source adapter before using it for mastery.

## Self-improvement loop

After every benchmark cycle Buddy asks:

1. What capability was missing?
2. Which source would close that gap fastest?
3. Is there a more authoritative source?
4. Is there a less redundant source?
5. Can an existing capability be transferred?
6. What new benchmark should prove the improvement?

The answer becomes a new discovery task, not an unverified permanent belief.

## Guardrails

Buddy must not bypass authentication, paywalls, robots/access controls, licensing restrictions or repository permissions. External repository changes require authorization. Consequential decisions remain subject to human approval.
