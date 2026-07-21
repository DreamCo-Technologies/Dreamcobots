import sys, os
REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, REPO_ROOT)

TOOL_DIR = os.path.join(REPO_ROOT, 'education-tools', 'recipe_scaling_tool')
sys.path.insert(0, TOOL_DIR)

import pytest
from recipe_scaling_tool import RecipeScalingTool

SAMPLE_RECIPE = {
    "name": "Pasta",
    "ingredients": [
        {"name": "pasta", "quantity": 200, "unit": "g"},
        {"name": "sauce", "quantity": 1, "unit": "cup"},
    ],
    "instructions": ["Boil pasta.", "Add sauce."],
}


class TestRecipeScalingToolInstantiation:
    def test_default_tier_is_free(self):
        tool = RecipeScalingTool()
        assert tool.tier == "free"

    def test_pro_tier(self):
        tool = RecipeScalingTool(tier="pro")
        assert tool.tier == "pro"


class TestScaleRecipe:
    def test_double_portions(self):
        tool = RecipeScalingTool(tier="pro")
        result = tool.scale_recipe(SAMPLE_RECIPE, 4, 8)
        pasta = next(i for i in result["ingredients"] if i["name"] == "pasta")
        assert pasta["quantity"] == 400.0

    def test_halve_portions(self):
        tool = RecipeScalingTool(tier="pro")
        result = tool.scale_recipe(SAMPLE_RECIPE, 4, 2)
        pasta = next(i for i in result["ingredients"] if i["name"] == "pasta")
        assert pasta["quantity"] == 100.0

    def test_same_portions_no_change(self):
        tool = RecipeScalingTool(tier="pro")
        result = tool.scale_recipe(SAMPLE_RECIPE, 4, 4)
        assert result["scale_factor"] == 1.0

    def test_invalid_original_servings(self):
        tool = RecipeScalingTool(tier="pro")
        with pytest.raises(ValueError):
            tool.scale_recipe(SAMPLE_RECIPE, 0, 4)

    def test_free_tier_monthly_limit(self):
        tool = RecipeScalingTool(tier="free")
        for _ in range(10):
            tool.scale_recipe(SAMPLE_RECIPE, 4, 8)
        with pytest.raises(PermissionError):
            tool.scale_recipe(SAMPLE_RECIPE, 4, 8)

    def test_returns_name(self):
        tool = RecipeScalingTool(tier="pro")
        result = tool.scale_recipe(SAMPLE_RECIPE, 4, 8)
        assert result["name"] == "Pasta"


class TestConvertUnit:
    def test_tsp_to_tbsp(self):
        tool = RecipeScalingTool()
        result = tool.convert_unit(3, "tsp", "tbsp")
        assert abs(result - 1.0) < 0.01

    def test_same_unit(self):
        tool = RecipeScalingTool()
        assert tool.convert_unit(5, "cup", "cup") == 5.0

    def test_invalid_conversion(self):
        tool = RecipeScalingTool()
        with pytest.raises(ValueError):
            tool.convert_unit(1, "tsp", "kg")

    def test_oz_to_grams(self):
        tool = RecipeScalingTool()
        result = tool.convert_unit(1, "oz", "g")
        assert abs(result - 28.35) < 0.1


class TestGenerateShoppingList:
    def test_pro_generates_list(self):
        tool = RecipeScalingTool(tier="pro")
        scaled = tool.scale_recipe(SAMPLE_RECIPE, 4, 8)
        shopping_list = tool.generate_shopping_list(scaled)
        assert len(shopping_list) == 2

    def test_free_raises_permission_error(self):
        tool = RecipeScalingTool(tier="free")
        with pytest.raises(PermissionError):
            tool.generate_shopping_list(SAMPLE_RECIPE)
