# Buddy Mathematical Intelligence

This layer implements small, composable mathematical primitives that can feed the unified decision engine.

## Current primitives

- Bayesian normalization and posterior updates
- entropy and information gain
- Hidden Markov Model forward inference
- deterministic Monte Carlo estimation
- scalar Kalman measurement updates
- Pareto-front selection for multi-objective choices

## Design rule

Mathematics produces evidence and rankings. It does not grant authorization. Policy, permissions, approval and execution remain separate layers.

## Roadmap

Add MCTS, dynamic programming, constrained optimization, linear/integer programming, convex optimization, evolutionary search, particle swarm optimization, simulated annealing, network flow, game-theoretic analysis and control loops behind stable interfaces. Each implementation should have deterministic tests where possible and explicit simulation-only boundaries for external actions.
