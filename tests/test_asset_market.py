from buddy_os.assets.asset_market import AssetMatcher
from buddy_os.assets.digital_asset_registry import DigitalAsset


def test_matcher_prefers_high_trust_utility_assets():
    assets = [
        DigitalAsset("a", "A", "tool", capabilities=["search"], trust_score=.9, utility_score=.9),
        DigitalAsset("b", "B", "tool", capabilities=["search"], trust_score=.2, utility_score=.3),
    ]
    result = AssetMatcher().match(assets, "search")
    assert result[0].asset_id == "a"
