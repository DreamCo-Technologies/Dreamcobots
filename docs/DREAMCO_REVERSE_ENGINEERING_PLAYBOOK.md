# DreamCo reverse engineering and test playbook

DreamCo uses REA's useful operating pattern—connect an agent to focused inspection tools, ask a narrow question, retain evidence, follow references, and test an independent implementation—as a design reference. This playbook and the `BuddyOpenSourceLab` implementation are DreamCo-authored. They do not install REA or copy its implementation.

## Investigation loop

1. **Define authority and scope.** Record who owns the target, approved artifacts/endpoints, permitted accounts, test window, data classes, and stop conditions.
2. **Pin the target.** Record a commit, model revision, file hash, app/build version, browser URL/route list, game build, or media file hash. Avoid a floating branch or changing target.
3. **Inventory and triage.** Identify formats, manifests, licenses, dependencies, secrets, sensitive data, required tools, and what can be analyzed statically.
4. **Form a falsifiable question.** Prefer one behavior or subsystem per investigation. Keep user-observed behavior separate from source-derived facts and hypotheses.
5. **Collect minimal evidence.** Use static inspection first. For dynamic tests, use fixtures, a test account, an emulator or isolated browser profile, a disposable state, and explicit resource/network limits.
6. **Trace causes.** Connect a visible behavior to the nearest available evidence: routes, modules, API contracts, state transitions, symbols, package metadata, test cases, or profiles. Record file/line, timestamps, hashes, and limitations rather than copying source.
7. **Build an independent behavior spec.** Capture inputs, outputs, state changes, failure cases, accessibility needs, and unknowns. Choose at least two DreamCo-specific changes and describe an original differentiator.
8. **Implement and compare.** Create original code and tests. Compare against the same owner-provided fixtures. Run security, privacy, licensing, accessibility, holdout, regression, performance, and cost checks before a human approves release.

## Target-specific evidence and tests

The machine-readable profile set lives in [`config/dreamco-investigation-profiles.json`](../config/dreamco-investigation-profiles.json). It specifies evidence and test families for source repositories, open weights, hosted frontier models, websites, mobile apps, games, media, and APIs. Each profile still needs its own adapter; a profile is a plan and is not evidence of a live connection.

### Source repositories

Inventory the immutable revision, language and build manifests, dependencies, entry points, routes, tests, documentation, generated artifacts, licenses, and secret risks. Use static review before execution. For a run, build in an isolated disposable non-root environment with a read-only source mount, a separate scratch output directory, no host credentials, no network by default, and bounded CPU, memory, disk, process count, and time. Lock dependencies and hashes. Retain stdout/stderr after secret scrubbing, exit code, test report, resource use, and artifact hashes. Never run a pull request or third-party install script in a privileged/self-hosted runner.

### Open-weight models

Pin repository revision and hashes; verify publisher, model card, use license, tokenizer, architecture, and required inference runtime. Prefer a safe tensor format. Inspect model and custom code before use; do not enable remote code or unpickle arbitrary weights by default. Load only in a sandbox without host secrets, then run the same task fixtures and hidden holdout used for comparison. Measure quality, safety, latency, memory, throughput, and cost. Hugging Face notes that pickle can execute arbitrary code; scanner results do not replace reviewing publisher, revision, and files.

### Hosted frontier model APIs

Use a provider's documented API and exact model identifier. Put credentials in the user's operating-system secret store or provider vault, with the smallest available scope, budget, quota, and expiration. Do not put keys in prompts, source trees, exported plans, or logs. Send only approved synthetic or consented fixtures. Record provider/version, request settings, timestamps, token usage, cost, latency, errors, and grader outputs. Compare with local models only on identical fixtures and account for provider data-retention terms. This tests observable API behavior; it does not reveal provider weights or internal reasoning.

### Websites and web applications

Start from the authorized route list and documented journeys. Capture DOM/accessibility state, screenshots, browser console, relevant network metadata, timing, and visible state changes in an ephemeral browser context. Use dedicated test accounts, synthetic records, route allowlists, request limits, and resettable state. Keep functional, accessibility, visual, performance, and security tests separate. Do not probe routes, accounts, or infrastructure outside scope.

### Mobile apps

Start with owner-provided source or a pinned package. Inventory manifests, permissions, signing data, SDKs, dependencies, strings, and resources. For runtime behavior, install only into a disposable emulator snapshot or an owner-approved test device/account; collect screenshots, logs, network metadata, and storage behavior. Test permissions, accessibility, privacy, offline/error states, and performance. OWASP MASTG distinguishes static and dynamic testing and stresses scope, evidence, and human interpretation; automated scanner results can have false positives and false negatives.

### Games and interactive apps

Observe user-authorized builds and source. Define control inputs, state transitions, scoring/rules, save/load, level progression, and expected outputs as repeatable scenarios. Use a clean profile and offline/local test mode where available. Measure frame time, memory, loading, crashes, and accessibility across declared hardware. For Unity, compare Profiler captures from development and target devices. Do not bypass DRM, anti-cheat, account checks, or live-service controls.

### Film, audio, and media

Analyze only user-provided or licensed media. Record file hash, codec, duration, tracks, segment boundaries, transcript/caption/audio-description quality, playback errors, and the user's own scene/pacing observations. Keep analysis notes and measurements; do not reproduce protected scenes, dialogue, music, or assets as a substitute for the original work. Any generated output needs its own rights review.

### APIs and services

Use an owner-approved schema, base URL, role-scoped test credentials, and provider sandbox/staging environment. Start with mocks and contract tests; then test validation, authn/authz, idempotency, retries, rate limits, webhooks, consistency, privacy, performance, and cost within explicit quotas. Use non-destructive endpoints. Production testing needs its own endpoint allowlist and approval.

## Safety and capability boundaries

- Static inspection can be local and read-only. Dynamic execution is a different permission and requires an isolated runtime adapter.
- A Docker container alone is not a guarantee against malicious code. Prefer a disposable VM/microVM or a hardened rootless runtime with no shared host socket and no secrets.
- The current DreamCo CLI performs static repository evidence analysis. `investigation_plan()` emits modality-specific plans. Neither currently launches a general sandbox or connects to a model provider.
- Model comparisons and sandbox plans in the Open Model Lab remain plans until a concrete adapter records run evidence. Never report a plan as a passed test.
- “Any target” is not one universal parser or safe runner. New formats/providers need a reviewed adapter, tests, license and scope rules, and a supported-host declaration.

## Sources

- [REA repository: workflow, evidence model, supported target classes, and local analysis](https://github.com/morluto/rea)
- [Hugging Face: pickle scanning and model artifact risks](https://huggingface.co/docs/hub/security-pickle)
- [Hugging Face Transformers: pin custom model code to a revision](https://huggingface.co/docs/transformers/main/models)
- [GitHub Actions: secure use and untrusted code risks](https://docs.github.com/en/actions/reference/security/secure-use)
- [Playwright: isolated browser contexts](https://playwright.dev/docs/browser-contexts)
- [OWASP MASTG: Android testing techniques](https://mas.owasp.org/MASTG/)
- [Unity Profiler: device and editor performance evidence](https://docs.unity.com/en-us/engine/6000.6/manual/analysis/profiler)
