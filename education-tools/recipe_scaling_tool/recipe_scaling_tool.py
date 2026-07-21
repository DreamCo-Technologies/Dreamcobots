# GLOBAL AI SOURCES FLOW
"""Recipe Scaling Tool - scale recipes up or down with unit conversion."""
import sys
import os
import importlib.util
_TOOL_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_TOOL_DIR, '..', '..'))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)
from framework import GlobalAISourcesFlow  # noqa: F401
# Load local tiers.py by path to avoid sys.modules conflicts with other tiers modules
_tiers_spec = importlib.util.spec_from_file_location('_local_tiers', os.path.join(_TOOL_DIR, 'tiers.py'))
_tiers_mod = importlib.util.module_from_spec(_tiers_spec)
_tiers_spec.loader.exec_module(_tiers_mod)
TIERS = _tiers_mod.TIERS


UNIT_CONVERSIONS = {
    "tsp": {"tbsp": 1/3, "cup": 1/48, "ml": 4.929},
    "tbsp": {"tsp": 3, "cup": 1/16, "ml": 14.787},
    "cup": {"tsp": 48, "tbsp": 16, "ml": 236.588, "liter": 0.237},
    "oz": {"g": 28.3495, "lb": 0.0625},
    "lb": {"oz": 16, "g": 453.592, "kg": 0.453592},
    "g": {"oz": 0.035274, "kg": 0.001, "lb": 0.0022046},
    "kg": {"g": 1000, "lb": 2.20462, "oz": 35.274},
    "ml": {"tsp": 0.2029, "tbsp": 0.0676, "cup": 0.00423, "liter": 0.001},
    "liter": {"ml": 1000, "cup": 4.227},
}


class RecipeScalingTool:
    """Scale recipes and convert units for any number of servings."""

    def __init__(self, tier: str = "free"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["free"])
        self._recipe_count = 0
        self._monthly_limit = 10 if tier == "free" else None

    def _check_limit(self):
        if self._monthly_limit and self._recipe_count >= self._monthly_limit:
            raise PermissionError(f"Monthly recipe limit ({self._monthly_limit}) reached. Upgrade to Pro.")

    def scale_recipe(self, recipe: dict, original_servings: int, target_servings: int) -> dict:
        """Scale all ingredient quantities in a recipe."""
        self._check_limit()
        if original_servings <= 0:
            raise ValueError("original_servings must be greater than 0.")
        factor = target_servings / original_servings
        scaled_ingredients = []
        for ingredient in recipe.get("ingredients", []):
            scaled = dict(ingredient)
            scaled["quantity"] = round(ingredient.get("quantity", 0) * factor, 3)
            scaled_ingredients.append(scaled)
        self._recipe_count += 1
        return {
            "name": recipe.get("name", "Unnamed Recipe"),
            "original_servings": original_servings,
            "target_servings": target_servings,
            "scale_factor": round(factor, 4),
            "ingredients": scaled_ingredients,
            "instructions": recipe.get("instructions", []),
            "tier": self.tier,
        }

    def convert_unit(self, quantity: float, from_unit: str, to_unit: str) -> float:
        """Convert a quantity from one unit to another."""
        if from_unit == to_unit:
            return round(quantity, 4)
        conversions = UNIT_CONVERSIONS.get(from_unit, {})
        if to_unit not in conversions:
            raise ValueError(f"Cannot convert {from_unit} to {to_unit}.")
        return round(quantity * conversions[to_unit], 4)

    def generate_shopping_list(self, scaled_recipe: dict) -> list:
        """Generate a shopping list from a scaled recipe (Pro+ only)."""
        if self.tier == "free":
            raise PermissionError("Shopping list export requires Pro tier or higher.")
        return [
            f"{i['quantity']} {i.get('unit', '')} {i['name']}".strip()
            for i in scaled_recipe.get("ingredients", [])
        ]
