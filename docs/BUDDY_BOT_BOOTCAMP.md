# Buddy Bot Bootcamp

DreamCo's training ground converts a customer's desired outcome into a measurable bot curriculum.

## Curriculum

1. Intake the customer's goal and constraints.
2. Decompose the goal into capabilities and subskills.
3. Compare the bot's evidence against the capability graph.
4. Select the best authorized sources for each gap.
5. Distill concepts into original DreamCo lessons.
6. Generate practice, failure-recovery, and transfer exercises.
7. Run isolated sandbox tasks.
8. Select external and DreamCo benchmarks that measure the capability.
9. Remediate only failed subskills.
10. Require novel transfer and regression evidence before mastery.
11. Continuously watch for regressions caused by model, tool, dependency, or source changes.

## Compute-saving strategy

Routine checks and cached knowledge come first. Independent jobs run in parallel. Small/cheap models handle classification and routine generation when adequate. Larger reasoning models are reserved for difficult synthesis, debugging, or tasks where measured learning gain justifies their cost.

## Source integrity

Sources are teachers, not authorities for runtime actions. Only authorized access is permitted. DreamCo creates original explanations, examples, exercises, and tests rather than reproducing protected source material. Locked benchmark answers are never used as training data.

## Customer controls

Customers can select capabilities, benchmarks, approved sources, privacy boundaries, compute/time budgets, permitted models, and mastery thresholds. The Buddy Bootcamp page adds a categorized resource picker across the repository's discovered resource catalog and governed resource registry. Users choose resources per plan; the choice is saved in that browser and can be exported. It does not connect accounts, fetch private data, or grant training rights.

DreamCo's own read-only source inspection system is `dreamco_platform.opensource.BuddyOpenSourceLab`; its command-line entry point is `tools/dreamco_code_workbench.py`. It inventories local repository structure and emits file-and-line evidence for entry points, route hints, tests, and documentation. It does not run target code, use the network, or copy source into reports. Use it only for repositories you own or have permission to analyze. Potential secret files block a clean-room report.

For source repos, open weights, frontier model APIs, websites, mobile apps, games, media, and general APIs, `tools/dreamco_investigation_plan.py` prepares a scoped test plan from the canonical profiles in `config/dreamco-investigation-profiles.json`. The [DreamCo reverse engineering playbook](DREAMCO_REVERSE_ENGINEERING_PLAYBOOK.md) documents evidence, test families, and safe local workflows. These plans do not connect to the target or claim test results: each target type needs a separately configured adapter before execution.

The catalog also includes a reference to [REA](https://github.com/morluto/rea) as an optional external project to evaluate. REA is not installed or connected by DreamCo. Review its current code, license, dependencies, security, and setup before choosing to use it. DreamCo's workbench operates independently of REA.

Any reconstruction plan must include target-owner authorization, clean-room implementation, at least two distinct user-selected customizations, and an original differentiator of at least 30 characters. The plan requires users to adapt the interface, workflow, audience, accessibility, security, integrations, performance, or add original features. It does not copy proprietary source/assets, bypass access controls or DRM, or claim a target was cloned. The browser flow exports a plan only; DreamCo's local analyzer creates static evidence, and neither flow executes REA or clones a target.

Customer-private curricula remain isolated from shared DreamCo training assets unless explicitly promoted through governance.
