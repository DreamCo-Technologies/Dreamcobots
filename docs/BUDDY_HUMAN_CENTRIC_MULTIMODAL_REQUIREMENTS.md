# Buddy human-centric multimodal requirements

## Existing repository capabilities and limits

The repository already has a multimodal learning-fabric architecture, speech
and image capability cards, a hash-bound consent gate, voice-cloning code,
image-generation code, and small study/evaluation packs.

Important implementation truth:
- The current `capabilities/media_cloning/voice_clone.py` routes through
  Buddy's local speech implementation and watermarks output. It is not proof
  of a high-fidelity commercial voice-cloning model, production inference, or
  verified voice similarity.
- The current `capabilities/media_cloning/image_clone.py` calls Buddy's
  drawing code and explicitly does not reproduce a person's face. It is not
  a working photorealistic face/likeness cloning pipeline.
- Existing consent checks bind a reference-file hash and require an adult
  confirmation, but the record is not identity verification. The intake,
  signer authentication, revocation propagation, watermark fail-closed
  enforcement, and real likeness/voice quality benchmarks remain gaps.

## Target capability families

1. **Original image generation** — create new realistic or stylized images
   from prompts, with no real person's identity unless the request is
   authorized and explicitly consented.
2. **Consented likeness generation** — optional user-authorized likeness
   workflow bound to reference hashes, purpose, permitted channels, expiry,
   revocation, and verified identity/authority. No minor likeness cloning.
3. **Consented voice replication** — optional voice model with the same
   consent and revocation controls; watermark/provenance must fail closed.
4. **Speech understanding** — speech-to-text, diarization where lawful,
   language/accent feature descriptions, and speech-quality analysis.
5. **Observable communication cues** — describe observable non-sensitive
   signals such as speaking rate, volume, pauses, pitch variation, visible
   facial movements, and explicit words. Treat emotion or intention as
   uncertain hypotheses, never facts.
6. **User-directed communication adaptation** — let users state preferred
   language, pronunciation, pacing, accessibility, and communication style.
   Store these as user-controlled preferences, not demographic inferences.

## Non-negotiable safeguards

- Do not infer or label race, ethnicity, nationality, religion, or cultural
  identity from face, voice, accent, or appearance.
- Do not treat accent as proof of origin, identity, education, or intent.
- Do not claim to know a person's inner emotion, honesty, mental state, or
  intention from facial expression or tone. Ask or phrase interpretations
  as uncertain observations.
- Do not identify a person from an image or voice sample. Consent to generate
  a likeness is not permission to identify the person.
- Require explicit, informed, revocable consent from the person represented;
  bind consent to exact media hashes and specific scopes (train, generate,
  publish, commercial use). A checkbox or an unverified JSON field alone is
  not identity verification.
- Reject requests to impersonate a third party, deceive an audience, bypass
  platform disclosure, or create non-consensual intimate or harmful depictions.
- Mark generated audio and images with provenance metadata/watermarks where
  supported. If a required watermark cannot be applied and verified, fail
  closed rather than silently output an unmarked clone.
- Keep raw biometric references private, encrypted, access-controlled, and
  deletable; never place voice/face samples in public Git or ordinary training
  fixtures. Revocation must block future generation and trigger governed
  deletion/retention review.
- Distinguish capability specification, installed model, successful inference,
  and benchmark-verified mastery as separate states.

## Required evidence before release

- End-to-end consent intake and signer/authority verification.
- Scope, expiry, revocation, and exact-file-hash negative tests.
- Privacy, retention, deletion, access-control, and incident-response tests.
- Watermark generation and independent detection tests.
- Real held-out voice similarity/naturalness and image identity/quality metrics,
  with human review and bias/robustness assessment.
- Safety tests for impersonation, deception, minors, non-consensual use, and
  sensitive identity inference.
- Latency, memory, hardware, cost, and reproducibility measurements.
- Separate approvals for personal, business, and commercial deployment.

## Status

This document records target requirements and known gaps. It does not claim
that Buddy already has production-grade photorealistic likeness cloning,
high-fidelity voice cloning, emotion recognition, cultural understanding, or
commercial readiness.
