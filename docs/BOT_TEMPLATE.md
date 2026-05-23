# Bot Template

Use this template as a starting point for creating new bots for the DreamCObots platform.

```python
from framework import GlobalAISourcesFlow

class ExampleBot:
    def __init__(self):
        self.flow = GlobalAISourcesFlow(
            bot_name="ExampleBot"
        )

        self.flow.validate()

    def execute(self, payload):
        return self.flow.run_pipeline(
            raw_data={
                "domain": "example",
                "input": payload
            },
            learning_method="supervised"
        )
```

## Guidelines for Bot Development

- Ensure your bot integrates `GlobalAISourcesFlow`.
- Implement all defined observability requirements (see `docs/OBSERVABILITY.md`).
- Follow the forbidden practices outlined in `CONTRIBUTING.md`.
- Validate the bot with CI tests before submitting it for review.

---