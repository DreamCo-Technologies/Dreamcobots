# Buddy Geometric Reasoning Frontier

Buddy now has a dependency-light geometric kernel that can be used by the ontology, digital twin, planning, vision and navigation layers.

## Design goals

1. **Coordinate-system aware**: points and vectors are explicit objects.
2. **Invariant-first**: rigid transforms must preserve distances.
3. **Deterministic core**: foundational geometry does not require an LLM.
4. **Composable**: spatial relations can become ontology edges and graph nodes.
5. **Safe**: simulation and reasoning do not grant execution permissions.
6. **Extensible**: the kernel can later connect to Open3D, PyTorch3D, GTSAM and E(3)-equivariant neural models where those dependencies are appropriate.

## Current primitives

- 3D vectors and points
- dot/cross products and normalization
- distances and angles
- axis-aligned bounding boxes
- containment and intersection
- SE(2) rigid transforms and inverse/compose operations
- qualitative spatial relations
- weighted shortest-path planning
- rigid-motion distance invariance checks

## Frontier roadmap

### Geometry kernel
- SE(3) poses, quaternions and rotation matrices
- planes, rays, segments and polygons
- convex hulls and separating-axis collision tests
- signed distances and nearest-point queries
- coordinate-frame registry

### Spatial ontology
- `inside`, `contains`, `adjacent`, `overlaps`, `intersects`
- metric relations such as distance and bearing
- temporal + spatial event fusion
- provenance and uncertainty for every spatial relation

### Geometric learning
- equivariant representations
- point-cloud and mesh embeddings
- SE(3)/E(3) consistency tests
- learned geometry with deterministic geometric validators

### Digital twin
- scene graphs
- collision-aware simulation
- spatial constraints
- path planning
- uncertainty-aware state estimation

### Verification benchmark
Every geometric model should be tested against invariants: translation/rotation invariance where applicable, equivariance where required, numerical tolerance, degenerate inputs, and adversarial geometry.

## Open-source strategy

Use mature open-source components instead of reimplementing every low-level accelerator. Candidate integrations include Open3D for 3D data processing, PyTorch3D for differentiable 3D learning/rendering, GTSAM for geometric estimation, and e3nn for E(3)-equivariant neural networks. Their licenses and dependency compatibility must be reviewed before integration.
