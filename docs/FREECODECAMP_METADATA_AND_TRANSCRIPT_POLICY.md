# FreeCodeCamp metadata, lessons, and transcript policy

## Current integration

- Source: the verified freeCodeCamp.org YouTube channel, channel ID `UC8butISFwT-Wl7EV0hUK0BQ`.
- Metadata discovery uses the channel's public YouTube RSS feed. It is a recent-upload feed, not a complete historical archive.
- The cataloger records video ID, title, URL, publish date, description, thumbnail, and deterministic topical categories.
- The route builder exposes metadata to all 65 canonical MasterBot lanes and prepares five daily lesson slots for each of the 55 domain profiles (275 planned slots/day).
- A lesson slot is `queued_not_studied` until Buddy completes an authorized study task and records evidence.

## Transcript and media boundaries

The cataloger does **not** download video/audio, scrape captions, or ingest transcript text. Each video starts with `transcript_status=not_ingested_rights_gate`; media download, transcript ingestion, and model training remain false.

A transcript may enter a later study/evaluation path only when its source and use rights are specifically established (for example, an owner-authorized transcript or a user-supplied transcript with documented permission). A public video page or the existence of captions is not, by itself, permission to download, retain, redistribute, or train on a transcript.

The weekly transcript evaluation queue must include only transcripts with a verified rights decision, an immutable transcript hash, and a permitted evaluation purpose. Unavailable or unauthorized transcripts stay visible as blocked; they are not silently skipped or represented as tested.

## Daily lesson schedule

The schedule target is five lesson slots per domain profile per day: 55 profiles × 5 = 275 slots. The current catalog may not contain five suitable videos for every profile. The planner reports planned and blocked slots separately and never duplicates a video within one profile's daily plan. The schedule is a plan, not proof of study, model training, or mastery.

## Full archive

The public RSS feed only covers recent channel uploads. Do not scrape the full channel archive. A future full-archive connector may use the official YouTube Data API with an operator-provided API key, documented quota limits, and explicit authorization. Until then, catalog coverage remains `latest_public_channel_rss_entries_per_poll_not_full_archive`.
