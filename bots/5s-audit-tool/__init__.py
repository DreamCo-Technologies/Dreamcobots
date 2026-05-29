from .tiers import BOT_FEATURES, get_bot_tier_info
import importlib.util, os as _os
_spec = importlib.util.spec_from_file_location(
    "_5s_audit_bot",
    _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "bot.py"))
_mod = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_mod)
FiveSAuditBot = _mod.FiveSAuditBot
__all__ = ["FiveSAuditBot", "BOT_FEATURES", "get_bot_tier_info"]
