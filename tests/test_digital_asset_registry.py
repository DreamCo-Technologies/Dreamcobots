from buddy_os.assets.digital_asset_registry import DigitalAsset, DigitalAssetRegistry


def test_register_search_and_manifest():
    registry = DigitalAssetRegistry()
    asset = DigitalAsset(
        asset_id="model:demo:v1",
        name="Demo Model",
        asset_type="model",
        capabilities=["reasoning"],
        tags=["local", "benchmark"],
        utility_score=.9,
    )
    registry.register(asset)
    assert registry.search("reasoning")[0].asset_id == "model:demo:v1"
    assert registry.manifest()[0]["version"] == "0.1.0"


def test_secret_material_is_reference_only():
    registry = DigitalAssetRegistry()
    asset = DigitalAsset(
        asset_id="secret:github",
        name="GitHub credential",
        asset_type="secret_reference",
        secret_ref_only=True,
        source_uri="os_keychain:dreamco/github",
    )
    registry.register(asset)
    assert registry.get("secret:github").source_uri.startswith("os_keychain:")
