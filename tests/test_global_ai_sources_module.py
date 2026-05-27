from global_ai_sources import ResourceOptimizer, SourcesManager, choose_source_for_task


def test_sources_manager_ranks_sources_for_domain():
    manager = SourcesManager()
    ranked = manager.rank_sources(domain="engineering", modality="code")
    assert ranked
    assert ranked[0].source_id in {source.source_id for source in manager.list_sources()}


def test_resource_optimizer_returns_fallback_chain():
    optimizer = ResourceOptimizer()
    chain = optimizer.fallback_chain(domain="marketing", modality="image", limit=2)
    assert len(chain) >= 1


def test_choose_source_for_task_returns_integration_decision():
    decision = choose_source_for_task(task="build ad assets", domain="creative", modality="image")
    assert decision.domain == "creative"
    assert isinstance(decision.fallback_chain, tuple)

