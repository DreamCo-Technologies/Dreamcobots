# Buddy Live Learning Bridge

`live_learning_bridge.py` is the boundary between Bootcamp's task-to-resource route and Buddy's existing execution/evidence systems.

- `prepare_learning_execution` emits a `dreamco.learning_execution_request.v1` packet.
- The normal Buddy runtime must enforce user approval, tool permissions, sandboxing, budgets, and audit logging before executing it.
- `evaluate_learning_completion` consumes a completion event and delegates evidence decisions to the existing continuous-learning controller, adding an explicit holdout requirement before promotion.
- The bridge does not itself fetch third-party content, execute tools, invoke paid models, or train weights.

`buddy/fleet_runtime/executor.py` now detects `input.learning_request` on a normal FleetExecutor task and calls this bridge after the existing task permission and input guardrail checks. A ready route is attached to the task and returned as `result.learning_execution`; workflow-engine tasks also receive the ordered Bootcamp learning steps in their workflow plan. Paid and account-gated sources stop at the existing `approval_required` result. A route with no eligible resource returns `learning_blocked`.

This is a live runtime integration point, but it is not yet proof of a complete external course or tool execution. The current FleetExecutor engines are deterministic planning/analysis/classification/drafting engines; the bridge does not fetch external course bodies or run arbitrary labs. Do not mark end-to-end learning completion until a real sandbox run, completion event, and evidence persistence test pass.
