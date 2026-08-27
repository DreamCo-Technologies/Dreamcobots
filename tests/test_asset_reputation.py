from buddy_os.assets.asset_reputation import ReputationBook


def test_reputation_learns_from_verified_outcomes():
    book = ReputationBook()
    for _ in range(8):
        book.record("tool:search", success=True, verified=True)
    book.record("tool:search", success=False, verified=False, incident=True)
    reputation = book.get("tool:search")
    assert reputation.attempts == 9
    assert reputation.success_rate > .8
    assert reputation.verification_rate > .8
    assert 0 <= reputation.score <= 1
