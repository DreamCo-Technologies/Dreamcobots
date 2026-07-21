# Recipe Scaling Tool

Scale recipes up or down for any number of servings, with smart unit conversion and shopping list export.

## Tiers
- **Free** ($0/mo): 10 recipes/month, basic scaling, unit conversion
- **Pro** ($14/mo): Unlimited recipes, nutritional info, shopping list export
- **Enterprise** ($49/mo): Batch cooking planner, allergen tracking, API access

## Usage
```python
import sys
sys.path.insert(0, "education-tools/recipe_scaling_tool")
from recipe_scaling_tool import RecipeScalingTool

tool = RecipeScalingTool(tier="pro")
result = tool.scale_recipe(recipe, original_servings=4, target_servings=12)
```
