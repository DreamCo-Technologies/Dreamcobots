# Buddy Build Runtime

The Universal Creation Engine uses a shared project graph so every project type follows the same evidence-driven lifecycle.

## Runtime lifecycle

1. Capture user intent from text, voice, image, or mixed input.
2. Infer project type and show multiple example approaches.
3. Create requirements and learning objectives when applicable.
4. Build a dependency graph connecting requirements, design, source, assets, tests, learning, versions, and deployment.
5. Generate a sandbox-safe prototype.
6. Execute automated tests and collect runtime evidence.
7. Repair failures through versioned changes and regression tests.
8. Route significant changes through review/PR/CI gates.
9. Present a live preview and teach the user how the project works.
10. Publish only after project-specific gates pass.
11. Measure outcomes and feed verified evidence into the learning/evaluation system.

## Non-negotiable guarantees

- A generated artifact is not automatically production-ready.
- Dependencies must be verified before downstream graph nodes advance.
- Security testing remains authorization-first.
- Voice/image assets require provenance and appropriate permission/consent controls.
- Failed experiments remain evidence; tests are not weakened to make a build green.
- Versions remain recoverable so unsuccessful changes can be rolled back.

## Universal scope

The runtime is shared by games, simulations, apps, websites, software, prototypes, courses, business plans, franchise models, commercials, music videos, films, AI projects, and custom creations.
