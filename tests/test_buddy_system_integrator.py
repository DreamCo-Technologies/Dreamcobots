from tools.buddy_system_integrator import classify

def test_known_system_paths_map():
    assert 'benchmarks' in classify('benchmarks/math/test.json')
    assert 'study_plans' in classify('training/study-plan.md')
    assert 'strategies' in classify('global_learning_system/learning_loop.py')
    assert 'divisions' in classify('divisions/finance/masterbot.py')
