from buddy_os.intelligence.reasoning_ensemble import ReasoningOpinion
from buddy_os.intelligence.reasoning_pipeline import ReasoningPipeline


def test_pipeline_gates_disagreement_for_verification():
    pipeline = ReasoningPipeline()
    solvers = {
        "causal": lambda _: ReasoningOpinion("causal", "A", 0.9, ("cause-x",)),
        "probabilistic": lambda _: ReasoningOpinion("probabilistic", "B", 0.8, ("evidence-y",)),
        "metacognitive": lambda _: ReasoningOpinion("metacognitive", "A", 0.7, ("uncertainty",)),
    }
    result = pipeline.run("diagnosis", ["causal", "uncertainty"], solvers, "why did it fail?")
    assert result.status == "verification_required"
    assert result.conflict is not None


def test_pipeline_returns_candidate_when_methods_agree():
    pipeline = ReasoningPipeline()
    solvers = {
        "deductive": lambda _: ReasoningOpinion("deductive", "A", 0.95),
        "constraint": lambda _: ReasoningOpinion("constraint", "A", 0.9),
        "metacognitive": lambda _: ReasoningOpinion("metacognitive", "A", 0.9),
    }
    result = pipeline.run("logic", ["verification"], solvers, "prove A")
    assert result.status == "candidate_ready"
    assert result.ensemble.answer == "A"
