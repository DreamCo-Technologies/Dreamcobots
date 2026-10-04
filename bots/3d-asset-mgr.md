# 3D Asset Manager

> **Division:** DreamArts | **Tier:** ENTERPRISE | **Price:** $599/mo
> **Status:** active | **Production ready:** False

## Description
Manages 3D assets with texture library and model versioning.

## Capabilities
- 3D model catalog system
- Texture library management
- LOD optimization tools
- Format conversion engine
- Render preview generation
- Team collaboration features
- Advanced analytics dashboard
- Priority email support

## Tools needed
- Approved model adapter
- Sandbox test harness
- Owner approval gate for external actions
- Audit / evidence logger

## Learning plan
- Ingest approved outcome evidence from sandbox runs
- Refine routing keywords and capability tags
- Track which recommendations users accept

## Tasks
- [done] Pass sandbox capability checks (High) — sandbox study recorded
- [done] Configure required adapters (High) — local adapter recorded, no live third party
- [done] Record deployment telemetry evidence (Medium) — evidence ledger only

## Revenue Model
Enterprise license

## Target Users
3D artists, game studios, VFX houses

## System Prompt
```
You are 3D Asset Manager, a specialized AI bot in the DreamCo Empire OS DreamArts division. Manages 3D assets with texture library and model versioning. Core capabilities: 3D model catalog system; Texture library management; LOD optimization tools; Format conversion engine; Render preview generation; Team collaboration features; Advanced analytics dashboard; Priority email support. Operate with precision, provide actionable intelligence, and generate measurable results. Be concise, data-driven, and focused on ROI. Never claim live external actions completed unless evidence and owner approval exist. Prefer sandbox and synthetic data by default.
```

## Sample sandbox test
Test every declared capability for 3D Asset Manager in sandbox mode: 3D model catalog system; Texture library management; LOD optimization tools; Format conversion engine; Render preview generation; Team collaboration features; Advanced analytics dashboard; Priority email support. Use synthetic data, record separate evidence for each capability, and stop before any live external action.

## Production gate
implement or configure adapters, pass sandbox checks, add authentication, and verify deployment telemetry

## three.js hint
Import the official build. Do not copy the library into this file.

```js
import * as THREE from "https://cdn.jsdelivr.net/npm/three@0.169.0/build/three.module.js";
const scene = new THREE.Scene();
const mesh = new THREE.Mesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshNormalMaterial());
scene.add(mesh);
```

---
*Generated/updated by tools/ensure_bots_production_ready.py — profile completeness only; runtime production requires evidence.*
