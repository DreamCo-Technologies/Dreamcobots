from .tiers import BOT_FEATURES, get_bot_tier_info
import importlib.util, os as _os
_spec = importlib.util.spec_from_file_location(
    "_3d_asset_mgr_bot",
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "bot.py"))
_mod = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)
ThreeDAssetManagerBot = _mod.ThreeDAssetManagerBot
__all__ = ["ThreeDAssetManagerBot", "BOT_FEATURES", "get_bot_tier_info"]
