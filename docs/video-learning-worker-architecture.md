# Buddy Video Learning Worker Architecture

Large video collections should be processed by independent workers rather than one monolithic pipeline.

## Workers

Scene detection, speech transcription, OCR, visual events, object tracking, action recognition, audio events, captioning, embeddings, deduplication, quality assessment, knowledge synthesis, and benchmark generation each have a separate contract.

## Why this matters

A failed OCR model must not prevent scene detection. A missing GPU must not destroy the inventory. A bad video file must be quarantined instead of stopping the collection. A low-confidence claim must remain uncertain until evidence improves.

## Evidence contract

Every worker emits source, timestamp, result, evidence, confidence, model version, and run ID. Temporal claims require timestamps. Conflicting worker results are preserved rather than silently overwritten.

## Learning loop

`video → workers → evidence graph → structured knowledge → benchmark cases → capability training → regression tests → improved worker`

This creates a reusable learning substrate for video understanding, filmmaking, education, music, games, simulation, and general computer-use benchmarks.
