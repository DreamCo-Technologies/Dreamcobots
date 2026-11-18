# Observable capability learning and supervised execution

`buddy/capabilities/runtime.py` supplies a shared Python runtime for trusted
adapters. It is not connected to the public website or an authenticated backend
yet. Its tests use a synthetic Bluetooth speaker; no physical device is accessed.

## Host integration

1. Authenticate the user and pair their chosen adapter through the operating
   system or official service. Bind one Session to that user and device. Never
   expose `approve` to a model or accept client-supplied Grant objects.
2. Implement Adapter.discover from actual negotiated services/API permissions,
   not device names, catalog descriptions, or model guesses. Its Action risk
   classification is trusted code. Bluetooth/WiFi are transports: they do not
   guarantee media playback, video, or app control.
3. Render the discovered actions and exact arguments in the existing approval
   UI. Call Session.approve only after the authenticated user approves that
   specific action. Approval expires, binds adapter revision and arguments,
   and is consumed before execution. Preserve the existing additional gates
   for destructive operations, repository writes and production deployment.
4. Use step(mode="watch") to stream running/result events while executing.
   Use step(mode="guided") to return adapter instructions without execution.
   Missing capabilities produce a manual handoff. Pause between steps with
   session.paused; stop invalidates grants. Adapters need their own cancellation
   for operations already in flight. Never automatically retry uncertain writes.
5. Adapter.execute must verify an outcome before returning True. A callback
   that merely dispatched an action must return False. Keep sensitive receipts
   in private user storage; progress events omit arguments and exception text.

## Reverse engineering and learning

Study authorized source, public documentation, user demonstrations and observable
inputs/outputs. Record source revision, expected behavior, custom user features
and independent acceptance tests. Reimplement and benchmark in a sandbox.
Customization is a product requirement, not a replacement for source/data rights.
This cannot recover proprietary weights or hidden model reasoning.

`distill_observations` exports consented, verified, redacted training examples
in memory. The calling host must actually redact private data and validate
rights; the flags are attestations, not automatic content inspection. It excludes
holdouts and unrelated fields. It does not perform inference or weight training.

Use existing `shared/model-provider-sources.ts` and
`server/open-model-lab-policy.ts` for external/local model onboarding and
`buddy/store/own_model.py` for the existing personal-model product path. A model
adapter must be configured and tested separately for each provider/protocol.
Personal fine-tuning requires a compatible licensed base, authorized private
training data, chosen hardware and budget. Keep datasets and weights outside the
public repository. Use `config/buddy-distill-contract.json` and
`tools/check_buddy_distill_gate.py` for baseline/holdout/promotion gates.

## Verification

Run `python3 -m unittest tests.test_observed_capability_runtime
tests.test_fleet_runtime_permissions tests.test_check_buddy_distill_gate
tests.test_buddy_local_bridge` from repository root.

Passing synthetic tests establishes runtime control behavior only. Universal
app/device compatibility, physical pairing, provider inference, trained weights
and improved model benchmarks remain unverified until separately demonstrated.
