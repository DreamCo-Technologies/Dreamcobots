from learning_orchestrator import EvaluationFailure, LearningAction, can_promote, propose_learning_jobs


def test_clusters_same_root_cause():
    failures = [
        EvaluationFailure("eval-1", "coding", "dependency", 0.2, 0.1, evidence_refs=("reg-1",)),
        EvaluationFailure("eval-2", "coding", "dependency", 0.3, 0.2, evidence_refs=("reg-2",)),
    ]
    jobs = propose_learning_jobs(failures)
    assert len(jobs) == 1
    assert jobs[0].action == LearningAction.TRAIN
    assert jobs[0].source_failures == ["eval-1", "eval-2"]


def test_promotion_requires_all_gates():
    assert can_promote(held_out_passed=True, regression_passed=True, safety_passed=True)
    assert not can_promote(held_out_passed=True, regression_passed=False, safety_passed=True)
    assert not can_promote(held_out_passed=True, regression_passed=True, safety_passed=False)
