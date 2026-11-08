# Buddy Live Learning Bridge

`live_learning_bridge.py` is the boundary between Bootcamp's task-to-resource route and Buddy's existing execution/evidence systems.

- `prepare_learning_execution` emits a `dreamco.learning_execution_request.v1` packet.
- The normal Buddy runtime must enforce user approval, tool permissions, sandboxing, budgets, and audit logging before executing it.
- `evaluate_learning_completion` consumes a completion event and delegates evidence decisions to the existing continuous-learning controller, adding an explicit holdout requirement before promotion.
- The bridge does not itself fetch third-party content, execute tools, invoke paid models, or train weights.

The production task dispatcher still needs to call this bridge and pass the packet to its existing authorization and sandbox path. Do not mark the live integration complete until that call site is wired and an end-to-end test proves request, approval, sandbox execution, result event, and evidence persistence.
