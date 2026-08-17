# Buddy Capability Package Marketplace

Buddy should be distributable as capabilities rather than one giant opaque model/data bundle.

## Package structure

Every package has a stable ID, version, human-readable description, capability IDs, dependencies, required benchmarks, evidence/provenance, permissions, resource requirements, compatibility, limitations, and known failures.

## AI-readable data

The primary package manifest is structured JSON with schema versioning. JSONL task records, machine-readable benchmark results, and human-readable documentation can accompany it. Stable identifiers make packages easy for Buddy and other software to index, compare, validate, and compose.

## User choice

Users select what they want Buddy to be capable of—for example coding, video understanding, music creation, film production, game building, education, business, government-service assistance, data analysis, research, sales, or customer support.

## Bootcamp and sandbox

A package goes through:

`install → dependency check → sandbox boot → capability tests → benchmark → security check → resource check → integration check → user acceptance → promote`

Failures stay isolated. They produce evidence and recovery records rather than breaking Buddy or other packages.

## Data products

DreamCo can eventually publish lawful, well-documented datasets and capability packages with clear provenance, licensing, schemas, benchmark scores, limitations, and versions. The goal is useful, interoperable training/evaluation data—not an indiscriminate dump of copyrighted material.

## Commercial layer

Packages can support free/open and paid offerings. Pricing and licensing are explicit, and purchasing or billing remains user-authorized.
