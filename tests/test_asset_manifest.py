from buddy_os.assets.asset_manifest import AssetManifest


def test_manifest_compatibility_and_export():
    manifest = AssetManifest(
        asset_id="skill:search:v1",
        name="Search Skill",
        version="1.0.0",
        asset_type="skill",
        inputs=["query"],
        outputs=["evidence"],
        permissions=["network.read"],
    )
    assert manifest.compatible_with(["query"], ["evidence"])
    assert not manifest.compatible_with(["query", "secret"], ["evidence"])
    assert manifest.export()["asset_id"] == "skill:search:v1"
