# Provisional FreeCodeCamp division queues

The full historical freeCodeCamp YouTube catalog is not currently verified. The repository has a partial metadata snapshot with 1,740 observed video records, but the snapshot does not retain a verified expected archive count.

This change preserves the strict default: complete verified inventory is still required for the canonical queue output. An explicit `--allow-partial` option creates a separate provisional queue file using only observed entries.

## Build provisional queues

```bash
python tools/build_freecodecamp_division_queues.py --allow-partial --limit 30
```

The default output is redirected to `config/generated/freecodecamp-provisional-division-learning-queues.json` so it cannot overwrite the verified canonical queue file.

## What provisional means

- All 55 domain queues can be generated from the observed metadata.
- Items remain `queued_not_studied`, with rights review required.
- No media download, transcript ingestion, model training, or mastery is authorized.
- The payload records `queue_mode: provisional_partial_inventory` and an explicit warning that the full archive is unverified.
- Missing, null, or duplicate observed rows still fail validation.

When an official, complete catalog is later verified, the normal strict command can regenerate the canonical queue.
