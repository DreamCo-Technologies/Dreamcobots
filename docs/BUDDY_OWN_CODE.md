# Buddy runs on its own code

Wrappers are an extra option. They are not required to finish a task. The best approved model is still picked.

- `buddy/desk/test_models.py` tests every user-approved model on every task. A model with no answer and no trial is not a winner. Private models are excluded. Buddy does not call a remote model.
- `buddy/desk/pick_wrapper.py` names that winner. `used_wrapper` stays false unless you opt in. Own code still does the work.
- `buddy/learning/wrapper_steps.py` gives each bootcamp step the model that won the test for that step. A tie prefers the free model, then Buddy's own code.
- `buddy/desk/own_task.py` is the path that does the work: maps, games, notes, benchmarks, guardrails, content drafts, study procedures, ideas, dataset catalog, speech code, and a local plan for anything else.
- A task that names email, Stripe, OpenAI, Claude, Grok, a charge, or a wrapper is refused. Buddy does not hand that work to another company.
- Voice and image cloning stay in `capabilities/media_cloning` and still require an adult consent record. That code is Buddy's; it is not a wrapper.
