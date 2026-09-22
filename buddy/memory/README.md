# Buddy memory places

You choose where learning and teaching notes live.

## Places

| Easy name | What it is |
|-----------|------------|
| This computer | `buddy/memory/vault/` |
| Chats folder | `chats/buddy_memory/` |
| Project notes | `docs/memory/` |
| This browser only | Website localStorage |
| A folder I choose | Any path you pass |
| GitHub export file | File you review, then send up |

## Commands

```bash
python3 buddy/memory/memory_places.py places
python3 buddy/memory/memory_places.py choose this_computer
python3 buddy/memory/memory_places.py choose chats_folder
python3 buddy/memory/memory_places.py choose custom_folder --path ~/Documents/buddy-memory
python3 buddy/memory/memory_places.py teach "Give short answers" --bot buddy
python3 buddy/memory/memory_places.py learn "Our deals need downside first" --bot deal
python3 buddy/memory/memory_places.py show
python3 buddy/memory/memory_places.py where
cd buddy/memory && python3 memory_places_test.py
```

Web picker: `buddy/memory/memory.html`

Rules: no secret keys. Teaching is not auto-promotion to live.
