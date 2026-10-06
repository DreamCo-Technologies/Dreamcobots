"""Placeholder GRPO reward; must pass reward_fn_review_grpo gate."""
def format_reward(completions, **kwargs):
    out = []
    for c in completions:
        text = c[0]["content"] if isinstance(c, list) else c
        out.append(1.0 if text.strip() else 0.0)
    return out
