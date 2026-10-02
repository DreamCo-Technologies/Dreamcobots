# DreamCo beginner router

This is not a Hugging Face leaderboard model.

It matches plain phrases to 200 written replies in `buddy/easy_github/skills_00.json` through `skills_03.json`.

## Check

```bash
python3 buddy/learning/hf_router_eval.py
```

Twelve prompts. A perfect score means the word matcher found the written reply. It does not mean DreamCo is the top model in the world.

## Not included

- No trained weights
- No claim of first place
- No sign-in to Hugging Face
