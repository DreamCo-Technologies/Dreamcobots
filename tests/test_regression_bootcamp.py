from tools.build_regression_bootcamp import build

def test_candidates_are_traceable_practice_only():
    rows=build()
    assert len(rows)>=60
    assert len({r['id'] for r in rows})==len(rows)
    assert all(r['training_allowed'] is False and r['mode']=='practice_only' and r['provenance']['source_sha256'] for r in rows)
    assert all(set(r['levels'])=={'beginner','intermediate','expert'} for r in rows)
