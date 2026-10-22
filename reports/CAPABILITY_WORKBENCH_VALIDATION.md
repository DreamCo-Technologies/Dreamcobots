# Capability workbench validation

The workbench lives at `website/capability-workbench.html` and is linked from
both shared navigation and shared repository controls. It indexes tracked paths,
opens served pages, verifies page HTTP responses on request, and reuses the
existing BuddyRun prospectus/issue router for eligible fleet bot buttons.

## Scan evidence

- Full static link scan: 3,636 references checked, zero broken paths before the
  final generated-file refresh. Rerun `python3 tools/check_website_links.py --all`.
- Refreshed page audit: 224 pages, 216 wired, one partial, seven server-dependent
  stubs, zero broken pages. “Wired” does not prove runtime correctness.
- Shared controls reach every HTML page according to
  `python3 tools/connect_repository_pages.py --check`.
- Missing server capabilities remain on app-shop, buddy, connections, hf-unlock,
  models, search and sign-in. Command-center also requires server endpoints.
  GitHub Pages cannot itself run Express/Python or supply OAuth/provider secrets.

## Implemented repairs and checks

- Wired the dead rotation simulation, FX-reference navigation and step-model
  form controls. Removed canned monitor assertions; snapshot checks now fetch
  actual evidence and explicitly state that no new runtime test was executed.
- Declared the career-pathway builder's pandas, snowballstemmer and cryptography
  dependencies in the existing optional tools environment manifest.
- Regenerated the page feature audit, repository test registry, Actions
  prospectus and per-file prospectus using their canonical generators.
- Supervised runtime/permission/distillation/local-bridge/dependency suite:
  36 tests passed. Page/prospectus/runtime regression selection: 45 tests passed.
- Workbench Node tests passed. DOM integration also exercised file filtering,
  page verification, existing bot issue links, income arithmetic and specification
  export against the actual page scripts and repository data.

## Remaining boundaries

The income exercise is a calculator over user assumptions. The build exercise
exports a specification. Neither claims actual earnings, generated code, trained
weights or unrestricted app control. Physical device adapters, authenticated
backend deployment, provider accounts and independent end-to-end task benchmarks
remain necessary. The supervised Python runtime is independently testable through
the linked Capability workbench proof workflow; the static UI does not execute it.

The local canonical quick gate passed types, dependencies and governed tests;
its build subprocess was blocked by the local tsx CLI IPC socket restriction.
The equivalent build can be exercised with `node --import tsx script/build.ts`.
Browser binary installation was unavailable in this environment; DOM integration
is not a substitute for a real browser deployment check.
