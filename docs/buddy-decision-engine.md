# Buddy Decision Engine

Buddy's learning systems should produce evidence, not authority.

The unified decision engine combines:

- capability fit
- historical success
- Markov transition probability
- MDP expected value
- reliability
- evidence quality
- cost efficiency
- latency efficiency
- risk penalty

Unauthorized candidates are filtered before scoring. A low-confidence result returns `selected=null` so the planner can gather more evidence or escalate for review.

## Architecture

`ontology -> memory -> candidate generation -> Markov/MDP signals -> decision engine -> policy/authorization -> simulation -> approval -> execution -> outcome -> learning`

The decision engine is intentionally deterministic and dependency-free. Learned models can supply signals, but they cannot grant permissions, execute actions, expose secrets, or override safety controls.

## Why this matters

This turns Buddy from a collection of independent routing heuristics into a common decision contract. Different divisions can add specialized evidence without inventing their own incompatible scoring rules.

Future upgrades can add calibrated confidence, Pareto-front selection, counterfactual evaluation, agent reputation, causal evidence, and offline policy evaluation behind the same contract.
