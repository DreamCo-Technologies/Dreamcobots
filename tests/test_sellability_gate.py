from buddy.media.sellability_gate import decide, combine

H = "a" * 64
def base(**kw):
    r = dict(asset_id="x", source_type="web", source="https://ex", collection_date="2026-09-28T00:00:00Z",
             owner="DreamCo", license="proprietary", ownership_class="dreamco_owned",
             commercial_redistribution_allowed=True, attribution_required=False, share_alike_required=False,
             transformation_history=["none"], provenance_hash=H, review_status="approved")
    r.update(kw); return r

def test_owned_approved_sellable(): assert decide(base())["decision"] == "sellable"
def test_missing_field_blocked(): r = base(); del r["license"]; assert decide(r)["decision"] == "blocked"
def test_unknown_blocked(): assert decide(base(ownership_class="unknown_do_not_publish"))["decision"] == "blocked"
def test_movie_reference_only(): assert decide(base(source_type="movie", ownership_class="third_party_reference_only"))["decision"] == "reference_only"
def test_license_nc_train_only(): assert decide(base(ownership_class="licensed_for_use", commercial_redistribution_allowed=False))["decision"] == "train_only"
def test_unreviewed_not_sellable(): assert decide(base(review_status="unreviewed"))["decision"] == "train_only"
def test_upload_no_consent_blocked(): assert decide(base(source_type="user_upload", ownership_class="user_contributed_with_permission"))["decision"] == "blocked"
def test_upload_train_scope(): 
    c = dict(consent_id="c1", reference_sha256=H, scope=["train"], attestation="I own this file and allow training use.", revoked=False)
    assert decide(base(source_type="user_upload", ownership_class="user_contributed_with_permission", consent=c))["decision"] == "train_only"
def test_upload_sell_scope():
    c = dict(consent_id="c1", reference_sha256=H, scope=["train","sell"], attestation="I own this file and allow training and resale.", revoked=False)
    assert decide(base(source_type="user_upload", ownership_class="user_contributed_with_permission", consent=c))["decision"] == "sellable"
def test_upload_revoked_blocked():
    c = dict(consent_id="c1", reference_sha256=H, scope=["train","sell"], attestation="I own this file and allow training and resale.", revoked=True)
    assert decide(base(source_type="user_upload", ownership_class="user_contributed_with_permission", consent=c))["decision"] == "blocked"
def test_package_most_restrictive():
    out = combine([base(asset_id="a"), base(asset_id="b", source_type="book", ownership_class="third_party_reference_only")])
    assert out["decision"] == "reference_only" and out["limiting_asset"] == "b"
def test_empty_package_blocked(): assert combine([])["decision"] == "blocked"
