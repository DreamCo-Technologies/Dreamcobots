# Editing PowerPoint Presentations

## Overview

pptxgenjs creates new presentations from scratch. To **edit** existing `.pptx` files you need a different approach:

## Approach 1: Read + Recreate with pptxgenjs

```js
// Extract data from existing pptx (using JSZip + xml parsing)
const JSZip = require('jszip');
const fs = require('fs');

async function readPptxText(filePath) {
  const zip = await JSZip.loadAsync(fs.readFileSync(filePath));
  const texts = [];

  for (const filename of Object.keys(zip.files)) {
    if (filename.startsWith('ppt/slides/slide') && filename.endsWith('.xml')) {
      const content = await zip.files[filename].async('string');
      // Extract text from <a:t> tags
      const matches = content.match(/<a:t[^>]*>(.*?)<\/a:t>/g) || [];
      matches.forEach((m) => {
        const text = m.replace(/<[^>]+>/g, '');
        if (text.trim()) texts.push(text);
      });
    }
  }
  return texts;
}
```

## Approach 2: Use python-pptx via Child Process

For editing existing slides (modifying text, replacing images), `python-pptx` is more capable:

```js
const { execSync } = require('child_process');
const fs = require('fs');

function editPptxWithPython(inputPath, outputPath, replacements) {
  const script = `
import sys
from pptx import Presentation
from pptx.util import Pt
from pptx.dml.color import RGBColor

prs = Presentation('${inputPath}')

replacements = ${JSON.stringify(replacements)}

for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    for old, new in replacements.items():
                        if old in run.text:
                            run.text = run.text.replace(old, new)

prs.save('${outputPath}')
print('Done')
`;

  fs.writeFileSync('_edit_pptx.py', script);
  try {
    execSync('python3 _edit_pptx.py', { stdio: 'inherit' });
  } finally {
    fs.unlinkSync('_edit_pptx.py');
  }
}

// Usage
editPptxWithPython('template.pptx', 'output.pptx', {
  '{{COMPANY_NAME}}': 'Acme Corp',
  '{{QUARTER}}': 'Q4 2024',
  '{{REVENUE}}': '$1.2M',
});
```

## Approach 3: Template-Based Editing with officegen

```bash
npm install officegen
```

```js
const officegen = require('officegen');
const pptx = officegen('pptx');

// officegen creates presentations slide by slide
const slide = pptx.makeTitleSlide('Presentation Title', 'Subtitle text');
```

## Common Editing Tasks

### Replace Placeholder Text

Use python-pptx approach above with a `replacements` object:

```js
const replacements = {
  '{{DATE}}':    new Date().toLocaleDateString(),
  '{{AUTHOR}}':  'John Smith',
  '{{VERSION}}': 'v2.1',
};
```

### Add a Slide to Existing Presentation

There is no native way in pptxgenjs to append to an existing file.
Use python-pptx:

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from copy import deepcopy

prs = Presentation('existing.pptx')
# Add new slide using first layout
slide_layout = prs.slide_layouts[1]
slide = prs.slides.add_slide(slide_layout)
tf = slide.shapes.title
tf.text = 'New Slide'
prs.save('updated.pptx')
```

### Delete a Slide

```python
from pptx import Presentation
from pptx.oxml.ns import qn

prs = Presentation('file.pptx')
# Delete slide at index 2
xml_slides = prs.slides._sldIdLst
xml_slides.remove(xml_slides[2])
prs.save('file.pptx')
```

### Change Theme Colors

```python
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.util import Pt

prs = Presentation('file.pptx')
for slide in prs.slides:
    for shape in slide.shapes:
        if shape.has_text_frame:
            for para in shape.text_frame.paragraphs:
                for run in para.runs:
                    # Change all dark blue text to brand color
                    if run.font.color.rgb == RGBColor(0x1F, 0x4E, 0x79):
                        run.font.color.rgb = RGBColor(0xE7, 0x4C, 0x3C)
prs.save('rebranded.pptx')
```

## Summary

| Task | Best Tool |
|------|-----------|
| Create new presentation | pptxgenjs |
| Replace placeholder text | python-pptx |
| Add slides to existing file | python-pptx |
| Extract text from existing | JSZip + XML parsing |
| Full slide editing | python-pptx |
