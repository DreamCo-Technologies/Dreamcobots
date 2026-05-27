from dreamco_platform.swarm.runtime import DreamCoRuntime


class _RedisClient:
    def __init__(self) -> None:
        self.stream_entries = []
        self.zset_entries = []

    def xadd(self, stream, values, maxlen=None, approximate=False):  # noqa: ANN001
        self.stream_entries.append((stream, values, maxlen, approximate))
        return "1-0"

    def zadd(self, key, mapping):  # noqa: ANN001
        self.zset_entries.append((key, mapping))
        return 1


def test_runtime_deposit_writes_trace_to_redis():
    redis_client = _RedisClient()
    runtime = DreamCoRuntime(redis_client=redis_client)
    trace = runtime.create_semantic_trace(
        trace_type="routing",
        strength=0.6,
        position=(2, 3),
        bot_id="bot_runtime",
        semantic_category="lead_generation",
        foraging_role="forager",
    )
    result = runtime.deposit_trace(trace, approval=True)
    assert result["allowed"] is True
    assert len(redis_client.stream_entries) == 1
    assert len(redis_client.zset_entries) == 1


def test_runtime_decay_keeps_nonzero_traces():
    runtime = DreamCoRuntime()
    trace = runtime.create_semantic_trace(
        trace_type="pricing",
        strength=0.8,
        position=(5, 5),
        bot_id="bot_runtime",
        semantic_category="economics",
        profitability_signal=4_000,
    )
    runtime.deposit_trace(trace, approval=True)
    decayed = runtime.apply_adaptive_decay()
    assert len(decayed) == 1
    assert decayed[0].strength > 0

