"""Permissioned feature reconstruction specification for Buddy wrappers.

This creates an original implementation brief, never a copied product.
"""
from urllib.parse import urlparse

BLOCKED = ("bypass_paywall", "evade_license", "steal_credentials", "copy_proprietary_code",
           "defeat_drm", "impersonate_brand", "scrape_private_data")

def create_spec(request):
    if not isinstance(request, dict):
        raise ValueError("request must be a dictionary")
    target = request.get("target", "")
    if not isinstance(target, str) or not target.strip():
        raise ValueError("target required")
    if request.get("authorized") is not True:
        raise PermissionError("target inspection requires permission")
    if request.get("source_type") not in ("owned_app", "open_source", "documented_api", "public_ui"):
        raise ValueError("unsupported or unverified source type")
    if request.get("source_type") == "public_ui" and request.get("terms_reviewed") is not True:
        raise PermissionError("public UI terms must be reviewed")
    if request.get("license_reviewed") is not True:
        raise PermissionError("license review required")
    if any(request.get(action) for action in BLOCKED):
        raise PermissionError("prohibited replication technique")
    features = request.get("features")
    custom = request.get("customizations")
    if not isinstance(features, list) or not features or not all(isinstance(f, str) and f.strip() for f in features):
        raise ValueError("nonempty feature list required")
    if not isinstance(custom, list) or not custom or not all(isinstance(f, str) and f.strip() for f in custom):
        raise ValueError("user customizations are mandatory")
    if len(set(custom)) != len(custom):
        raise ValueError("customizations must be unique")
    return {
        "target": target.strip(), "source_type": request["source_type"],
        "mode": "original_implementation_spec", "features": features,
        "user_customizations": custom, "user_customizations_required": True,
        "attribution": request.get("attribution", "Source acknowledged where required"),
        "original_branding_required": True, "copy_source_code": False,
        "copy_assets": False, "copy_trademarks": False,
        "reuse_licensed_material_only": True, "status": "design_review_required",
        "evaluation": {"correctness": "pending", "latency": "pending",
                       "accessibility": "pending", "safety": "pending",
                       "cost": "pending", "regressions": "pending"},
        "production_ready": False
    }
