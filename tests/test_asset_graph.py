from buddy_os.assets.asset_graph import AssetGraph
from buddy_os.assets.digital_asset_registry import DigitalAsset, DigitalAssetRegistry


def test_dependency_closure_and_capability_index():
    registry = DigitalAssetRegistry()
    registry.register(DigitalAsset("api:x", "API", "api", capabilities=["payments"]))
    registry.register(DigitalAsset("tool:x", "Tool", "tool", dependencies=["api:x"], capabilities=["payments", "search"]))
    graph = AssetGraph(registry)
    assert graph.dependency_closure("tool:x") == {"api:x"}
    assert graph.capability_index()["payments"] == ["api:x", "tool:x"]
