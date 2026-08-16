# DreamCodeLab: Coding Capability Benchmark Lab

DreamCodeLab is treated as a long-running learning and evaluation program, not as proof of mastery by elapsed time.

The repository already contains coding-mastery programs and a DreamCodeLab bot. This document defines how that work should become measurable.

## What gets measured

Every coding capability receives separate percentages for:

- language fundamentals
- idiomatic style
- standard library use
- ecosystem/library use
- framework use
- API integration
- testing
- debugging
- code review
- refactoring
- architecture
- security
- performance
- documentation
- package/build tooling
- deployment
- interoperability
- version migration
- unfamiliar-code comprehension
- error recovery

## Benchmark ladder

```text
Syntax task
   ↓
Small coding task
   ↓
Library task
   ↓
Multi-library task
   ↓
Real repository task
   ↓
Debugging task
   ↓
Refactoring task
   ↓
Architecture task
   ↓
Unseen holdout
   ↓
Transfer task
   ↓
Regression suite
```

## Library mastery

For a library, DreamCodeLab should distinguish:

1. Can identify what the library is for.
2. Can install/import it correctly.
3. Can use its core API.
4. Can solve representative tasks.
5. Can debug common failures.
6. Can integrate it with other libraries.
7. Can read unfamiliar documentation/source when necessary.
8. Can work across relevant versions.
9. Can transfer the concept to an unseen task.
10. Can avoid regressions after improvements.

Each stage gets evidence and a percentage instead of a binary mastered/not-mastered flag.

## Two-year learning history

If a capability has been studied for approximately two years, preserve that history as provenance. Do not convert elapsed time directly into a mastery percentage.

The benchmark system answers the more useful question:

> What can DreamCodeLab demonstrably do today, and how much better is it than its previous verified baseline?

## Continuous improvement

Every significant failure becomes a categorized data point:

- reasoning error
- syntax error
- API misuse
- dependency/version error
- tool error
- environment error
- test failure
- security issue
- performance issue
- misunderstanding of requirements
- incomplete solution

Buddy can then prioritize the largest or highest-value failure classes for the next sandbox cycle.

## Output

The desired dashboard is:

```text
DreamCodeLab
Overall coding capability: XX%

Python: XX%
TypeScript: XX%
Java: XX%
C/C++: XX%
Rust: XX%
Go: XX%
SQL: XX%
...

Libraries: XX / N verified
Frameworks: XX / N verified
Debugging: XX%
Architecture: XX%
Security: XX%
Testing: XX%
Generalization: XX%

Benchmark trend: +X.X points
Largest current gap: ______
Next improvement target: ______
```

The exact numbers must come from recorded evaluations, not estimates.
