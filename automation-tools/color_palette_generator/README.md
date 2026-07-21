# Color Palette Generator

AI-powered color palette generator for branding, UI/UX design, and marketing materials.

## Tiers
- **Free** ($0/mo): 5 palettes/month, basic color schemes
- **Pro** ($19/mo): Unlimited palettes, brand color analysis, export PNG/SVG
- **Enterprise** ($79/mo): AI color matching, team workspaces, API access

## Usage
```python
import sys
sys.path.insert(0, "automation-tools/color_palette_generator")
from color_palette_generator import ColorPaletteGenerator

gen = ColorPaletteGenerator(tier="pro")
palette = gen.generate_palette("#1a73e8", scheme="triadic")
```
