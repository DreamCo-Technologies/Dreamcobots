# Start here — Buddy is the easy way to GitHub

You do **not** need to already know GitHub.

Buddy's job: turn plain requests into the right GitHub action, keep the project tidy, and explain results in common words.

## The only loop you need

1. **Say what you want** in normal words.
2. Buddy **picks the path** (save, send, review, fix, check).
3. You **look at the simple summary**.
4. You **say yes** before anything big (publish, spend, delete).

## First 10 minutes

1. Open this folder: `buddy/easy_github/`
2. Read `WORDS.md` (one page of translations)
3. Open `MAP.md` (where things live)
4. Try a sentence from `SAY_THIS.md`
5. If you use the command line later:

```bash
python3 buddy/easy_github/buddy_easy_github.py help
python3 buddy/easy_github/buddy_easy_github.py say "what's broken"
python3 buddy/easy_github/buddy_easy_github.py say "save my work"
```

## Feel like an experienced coder

Experienced people do five things well. Buddy wraps each one:

| Experienced habit | Easy words | Buddy tool |
|-------------------|------------|------------|
| Know the map | "Where is everything?" | `MAP.md` |
| Save often | "Save my work" | commit helper text |
| Review before merge | "Review this change" | change-request checklist |
| Trust tests | "Did the check pass?" | robot-check explainer |
| Keep noise down | "Clean fake tickets" | issue cleaner |

## Truth in plain words

- A **list of bots** is not the same as every bot being live.
- A **green check** means that one test passed, not that the whole company is finished.
- **Never paste secret keys** into chat.
