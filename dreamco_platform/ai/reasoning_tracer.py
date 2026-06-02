"""Bot reasoning trace recorder."""
    from __future__ import annotations

    from dataclasses import dataclass, field
    from typing import Dict, List
    import uuid


    @dataclass
    class ReasoningTrace:
        step_id: str
        thought: str
        action: str
        observation: str
        confidence: float


    @dataclass
    class TraceContext:
        bot_id: str
        task: str
        trace_id: str = field(default_factory=lambda: str(uuid.uuid4()))
        steps: List[ReasoningTrace] = field(default_factory=list)

        def add_step(self, thought: str, action: str, observation: str, confidence: float) -> ReasoningTrace:
            step = ReasoningTrace(f"step-{len(self.steps) + 1}", thought, action, observation, round(confidence, 3))
            self.steps.append(step)
            return step

        def replay(self) -> List[str]:
            return [f"{step.step_id}: {step.thought} -> {step.action} => {step.observation}" for step in self.steps]

        def as_directed_graph(self) -> Dict[str, List[str]]:
            graph: Dict[str, List[str]] = {}
            for index, step in enumerate(self.steps):
                next_step = self.steps[index + 1].step_id if index + 1 < len(self.steps) else "END"
                graph[step.step_id] = [next_step]
            return graph


    class ReasoningTracer:
        def __init__(self) -> None:
            self.active: Dict[str, TraceContext] = {}

        def start_trace(self, bot_id: str, task: str) -> TraceContext:
            context = TraceContext(bot_id=bot_id, task=task)
            self.active[context.trace_id] = context
            return context

        def visualize(self, trace: TraceContext) -> str:
            lines = ["digraph reasoning {"]
            for source, targets in trace.as_directed_graph().items():
                for target in targets:
                    lines.append(f'  "{source}" -> "{target}";')
            lines.append("}")
            return "
".join(lines)

        def replay(self, trace_id: str) -> List[str]:
            trace = self.active[trace_id]
            return trace.replay()
