# Buddy Song Voice Image Test

Test Buddy's song-with-my-voice-and-image workflow without uploading private media or using paid services.

## Song Packet

- Title: Built With My Own Hands
- Genre: motivational hip-hop soul
- BPM: 92
- Key: A minor

## Hook

I built it with my own hands, now Buddy light the way. We turn the work into a plan, then make a brighter day.

## Verse

- Started with a laptop and a dream in motion
- Bots in the dashboard, focus like an ocean
- Every safe step leaves a trail I can see
- DreamCo in the room, building what I believe

## Local Test Capabilities

- preview your selected image locally in the browser
- play your selected voice sample locally in the browser
- record a fresh voice sample locally with the browser microphone
- play back the recorded voice sample locally
- create a clone-readiness packet with consent metadata
- speak the hook with local browser speech synthesis
- store a consent checklist and production packet
- prepare the handoff path for a real approved voice model later

## Clone Capability

- recording: `browser_media_recorder_local_only`
- sample_storage: `user_controlled_browser_blob`
- clone_status: `ready_for_approved_local_model_or_provider`
- blocked_until:
  - owner confirms recorded voice belongs to owner
  - owner approves cloning for this song
  - local voice model or approved provider is configured
  - synthetic media label is preserved

## Approval Required For

- voice cloning
- face or likeness generation
- public release
- commercial use
- third-party model or API use
- uploading private media
