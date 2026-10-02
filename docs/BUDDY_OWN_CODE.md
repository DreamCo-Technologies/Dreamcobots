# Buddy runs on its own code

Wrappers are an extra option. They are not required to finish a task.

- `buddy/desk/own_task.py` is the path that does the work: maps, games, notes, benchmarks, guardrails, content drafts, study procedures, ideas, dataset catalog, speech code, and a local plan for anything else.
- `buddy/desk/pick_wrapper.py` can name a user-added model. It does not call that model, and `offer()` returns nothing unless `use_wrapper=True`.
- `buddy/learning/wrapper_steps.py` assigns Buddy's own code to every bootcamp step unless that step sets `use_wrapper: true`.
- A task that names email, Stripe, OpenAI, Claude, Grok, a charge, or a wrapper is refused. Buddy does not hand that work to another company.
- Voice and image cloning stay in `capabilities/media_cloning` and still require an adult consent record. That code is Buddy's; it is not a wrapper.
