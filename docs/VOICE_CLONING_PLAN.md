# Voice cloning plan

Default backend is Chatterbox in `buddy/media/voice.py`. It is MIT-licensed and runs on Apple GPU. XTTS stays commented out in `requirements-media.txt` because that license is non-commercial.

## Gate order

1. Consent. A signed record must match the sha256 of the exact reference clip. No record, wrong hash, wrong scope, or expired record refuses the job.
2. Reference check. 3 seconds minimum, 10–15 seconds ideal, silence trimmed, capped at 15 seconds. Reject a minor's voice.
3. Local budget. One model at a time on an 8 GB Mac. Peak memory target is under 6 GB. Longer batches go to a remote worker, not a second local model.
4. Watermark and manifest. Every output gets a provenance mark and a sidecar before it leaves the sandbox.
5. Evidence. Three independent sandbox passes, a holdout that is not in the public repo, and a regression run. Until those exist, mastery stays false.

## Backend order

- Chatterbox for cloning.
- Kokoro-82M only as a non-cloning fallback voice.
- F5-TTS or OpenVoice only after a license check.
- Do not install XTTS for a paid product.

## Missing before this is real

- An intake flow that calls `write_consent_record` after a human consent step.
- A remote client wired to the DreamCo router for jobs over 8 GB.
- A watermark check that fails the job if AudioSeal is not installed. The current fallback can ship unmarked audio.
- Speaker-similarity and naturalness scores from a real clip. The consent tests do not download a model.
- A commercial-license decision if the product is sold.

Holdout clips stay out of the public repo. Publishing them would invalidate the test.
