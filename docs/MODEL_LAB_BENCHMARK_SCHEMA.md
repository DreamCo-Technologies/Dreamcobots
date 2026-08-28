# Universal Model Benchmark Schema

This schema is intended to cover every current and future model in the DreamCo research registry.

## Identity

- lab/company
- model
- version/revision
- modality
- license
- source/evidence URL
- evaluation date

## Capability profile

- reasoning
- mathematics
- coding
- planning
- tool use
- agents
- retrieval
- memory
- vision/audio/multimodal capability where applicable
- multilingual capability
- safety/reliability

## Resource profile

- parameter count when known
- active parameters when applicable
- precision/quantization
- model storage
- VRAM
- RAM
- KV-cache/context footprint
- tokens/sec
- time-to-first-token
- compute/GPU-hours when known
- energy/cost when measurable

## Experiment profile

- benchmark suite/version
- task fixture
- baseline
- technique under test
- reasoning budget
- tool configuration
- random seed where applicable
- environment
- result
- uncertainty
- regression result
- reproducibility state

## Decision

`keep | modify | combine | distill | reject | blocked | stale | needs_review`

## No fabricated data

Unknown values remain unknown. Reported claims and independently reproduced results are stored separately.
