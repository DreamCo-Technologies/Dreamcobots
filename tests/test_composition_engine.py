from buddy_os.assets.composition_engine import AssetCompositionEngine
from buddy_os.assets.digital_asset_registry import DigitalAsset, DigitalAssetRegistry


def test_composition_collects_dependencies_and_stays_simulation_only():
    registry = DigitalAssetRegistry()
    registry.register(DigitalAsset("api:search", "Search API", "api", utility_score=.8, risk_score=.1))
    registry.register(DigitalAsset("skill:research", "Research", "skill", dependencies=["api:search"], utility_score=1, risk_score=.2, lifecycle="verified"))
    result = AssetCompositionEngine(registry).compose("research", ["skill:research"])
    assert result.dependencies == ["api:search"]
    assert result.simulation_only is True
    assert result.estimated_utility == 1
