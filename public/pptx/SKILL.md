# PowerPoint Presentation Manipulation — SKILL.md

## Setup

```bash
npm install pptxgenjs
```

## Minimal Example

```js
const PptxGenJS = require('pptxgenjs');
const pres = new PptxGenJS();

const slide = pres.addSlide();
slide.addText('Title', { x: 1, y: 1, w: 8, h: 1.5, fontSize: 44, bold: true, color: '1F4E79' });

await pres.writeFile({ fileName: 'deck.pptx' });
```

## Coordinates

- All positions (`x`, `y`) and sizes (`w`, `h`) are in **inches**
- 16:9 slide = 10 × 5.625 inches
- Origin (0,0) = top-left corner
- Can also use percentages: `{ x: '10%', w: '80%' }`

## Text Options Reference

```js
slide.addText('Text', {
  x: 0.5, y: 0.5, w: 9, h: 1,
  fontSize:     24,
  bold:         true,
  italic:       false,
  underline:    { style: 'sng' },  // 'sng' | 'dbl' | 'thick'
  color:        '000000',          // hex, no #
  fontFace:     'Calibri',
  align:        'center',          // 'left' | 'center' | 'right' | 'justify'
  valign:       'middle',          // 'top' | 'middle' | 'bottom'
  margin:       0.1,               // inches
  fill:         { color: 'F0F0F0' },
  line:         { color: 'CCCCCC', width: 1 },
  shadow:       { type: 'outer', color: '000000', blur: 5, offset: 3, angle: 45, opacity: 0.3 },
  rotate:       0,                 // degrees
  paraSpaceBefore: 6,              // pt
  paraSpaceAfter:  6,
  wrap:         true,
  autoFit:      true,
});
```

## Chart Quick Reference

```js
// Supported chart types
pres.ChartType.bar     // vertical bars
pres.ChartType.barHoriz  // horizontal bars
pres.ChartType.line
pres.ChartType.area
pres.ChartType.pie
pres.ChartType.doughnut
pres.ChartType.scatter
pres.ChartType.bubble
pres.ChartType.radar

// Data format
const chartData = [
  {
    name: 'Series 1',
    labels: ['Jan', 'Feb', 'Mar'],
    values: [100, 200, 150],
  },
];

slide.addChart(pres.ChartType.bar, chartData, {
  x: 0.5, y: 1, w: 9, h: 4,
  showLegend: true,
  legendPos: 'b',
  showValue: true,
  chartColors: ['1F4E79', '2E75B6'],
});
```

## Table Quick Reference

```js
const tableData = [
  [
    { text: 'Header 1', options: { bold: true, fill: '1F4E79', color: 'FFFFFF' } },
    { text: 'Header 2', options: { bold: true, fill: '1F4E79', color: 'FFFFFF' } },
  ],
  ['Row 1 Col 1', 'Row 1 Col 2'],
  ['Row 2 Col 1', 'Row 2 Col 2'],
];

slide.addTable(tableData, {
  x: 0.5, y: 1, w: 9,
  rowH: 0.5,
  fontSize: 12,
  border: { type: 'solid', pt: 1, color: 'CCCCCC' },
});
```

## Shapes Quick Reference

```js
// All shapes from pres.ShapeType
slide.addShape(pres.ShapeType.rect, {
  x: 1, y: 1, w: 3, h: 2,
  fill: { color: '1F4E79' },
  line: { color: 'FFFFFF', width: 2 },
});
```

Key shape types: `rect`, `roundRect`, `ellipse`, `triangle`, `line`, `rightArrow`, `leftArrow`, `pentagon`, `hexagon`, `star5`, `ribbon`, `callout1`.

## Slide Master

```js
pres.defineSlideMaster({
  title: 'CORP',
  background: { fill: 'FFFFFF' },
  objects: [
    { image: { x: 8.5, y: 0.1, w: 1.2, h: 0.6, path: 'logo.png' } },
    { text: { text: 'Confidential', options: { x: 0.5, y: 5.3, fontSize: 8, color: '999999' } } },
  ],
  slideNumber: { x: 9.2, y: 5.3, fontSize: 8 },
});

const slide = pres.addSlide({ masterName: 'CORP' });
```

## Export Options

```js
await pres.writeFile({ fileName: 'deck.pptx' });

const buf = await pres.write({ outputType: 'nodebuffer' });
fs.writeFileSync('deck.pptx', buf);

const b64 = await pres.write({ outputType: 'base64' });
```

## Tips

- Build a slide template function to avoid repetition across many slides.
- Use `pres.defineSlideMaster` for consistent branding.
- Chart colors are arrays of hex strings (no `#`).
- `autoFit: true` on text boxes prevents overflow.
- Always `await` the `writeFile` / `write` calls.
