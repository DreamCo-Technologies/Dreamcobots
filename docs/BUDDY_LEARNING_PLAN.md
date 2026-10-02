# Plan: learn the tasks Buddy cannot do

Buddy already picks the best user-approved model for each task and each bootcamp step. This plan is how it learns the tasks it cannot do yet. It does not call a remote model and it does not train weights.

## Pick the best model

1. Take only models a user approved or marked shared. Private models stay out.
2. Test every approved model on every task. A missing answer is not a score.
3. Buddy's own code is always in the test.
4. The highest score wins. A tie prefers the free model, then Buddy's own code.
5. Each bootcamp step uses the winner of that step. Own code still does the work unless you opt in.

The scorer is `buddy/desk/test_models.py`. The task picker is `buddy/desk/pick_wrapper.py`. The step picker is `buddy/learning/wrapper_steps.py`.

## Learn a task it does not know

`buddy/learning/gap_plan.py` splits every asked task into known, refused, or needs practice.

Known tasks stay on Buddy's own code: maps, datasets, ideas, captions, notes, games, benchmarks, guardrails, study, speech, and workers.

Refused tasks are not practiced through another company: email, Stripe, OpenAI, Claude, Grok, a charge, or a wrapper.

A task that is only planned is not learned. For each of those:

1. Write one new example in Buddy's own file.
2. Run that example and record pass or fail.
3. Test every user-approved model on the same task and keep the highest score.
4. Prefer a free model on a tie, then Buddy's own code.
5. Repeat the example on a new case before calling the task learned.

A recorded trial is the test. A model that was not run does not get a score, and this plan does not invent one.
