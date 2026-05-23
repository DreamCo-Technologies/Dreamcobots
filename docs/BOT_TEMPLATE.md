# Bot Template

Use this template as a starting point for creating new bots for the DreamCObots platform. The updates ensure compatibility with enterprise-grade requirements, emphasizing observability, validation, and governance.

```python
from typing import Any, Dict

from framework import GlobalAISourcesFlow
from dreamco_platform.observability.metrics import MetricsCollector
from dreamco_platform.observability.audit_log import AuditLog
from dreamco_platform.observability.tracer import Tracer


class ExampleBot:
    """
    Base template for DreamCObots-compatible bots.

    Requirements:
    - Must integrate GlobalAISourcesFlow
    - Must pass framework validation
    - Must emit observability telemetry
    - Must comply with governance/security requirements
    """

    def __init__(self) -> None:
        self.bot_name = "ExampleBot"

        # Core AI pipeline
        self.flow = GlobalAISourcesFlow(
            bot_name=self.bot_name
        )

        # Observability systems
        self.metrics = MetricsCollector()
        self.audit_log = AuditLog()
        self.tracer = Tracer()

        # Validate framework compliance
        self.flow.validate()

    def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution entry point.
        """

        with self.tracer.span("example_bot.execute"):

            self.audit_log.record(
                actor=self.bot_name,
                action="execute",
                resource="pipeline",
                outcome="pending"
            )

            try:
                result = self.flow.run_pipeline(
                    raw_data={
                        "domain": "example",
                        "input": payload
                    },
                    learning_method="supervised"
                )

                self.metrics.counter(
                    "bot_execution_success"
                ).increment()

                self.audit_log.record(
                    actor=self.bot_name,
                    action="execute",
                    resource="pipeline",
                    outcome="success"
                )

                return result

            except Exception as error:

                self.metrics.counter(
                    "bot_execution_failure"
                ).increment()

                self.audit_log.record(
                    actor=self.bot_name,
                    action="execute",
                    resource="pipeline",
                    outcome="error"
                )

                raise RuntimeError(
                    f"{self.bot_name} execution failed"
                ) from error
```

---

## Required Bot Structure

Organize all bot contributions as follows:

```
bots/
└── example_bot/
    ├── __init__.py
    ├── example_bot.py
    ├── README.md
    ├── config.json
    └── tests/
        └── test_example_bot.py
```

---

## README Requirements

Every bot README must include:

- Purpose
- Supported capabilities
- Learning method used
- Required dependencies
- Example payloads
- Execution instructions
- Observability integrations
- Governance considerations
- Security notes

---

## Testing Template

Use the following testing template to validate your bot:

```python
def test_bot_pipeline_execution():
    bot = ExampleBot()

    result = bot.execute({
        "message": "test"
    })

    assert result["pipeline_complete"] is True
```

---

## Bot Lifecycle Requirements

Every bot should explicitly support:

- Initialization
- Validation
- Execution
- Telemetry emission
- Audit logging
- Graceful failure handling
- Future retraining compatibility