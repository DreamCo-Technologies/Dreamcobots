# pptxgenjs Library Reference

Homepage: https://gitbrent.github.io/PptxGenJS/

## Installation

```bash
npm install pptxgenjs
```

## PptxGenJS Class

```js
const PptxGenJS = require('pptxgenjs');
const pres = new PptxGenJS();
```

### Properties

| Property | Type | Default | Description |
|----------|------|---------|-------------|
| `layout` | string | `'LAYOUT_16x9'` | Slide layout preset |
| `author` | string | | Presentation author metadata |
| `company` | string | | Company metadata |
| `subject` | string | | Subject metadata |
| `title` | string | | Presentation title metadata |
| `rtlMode` | boolean | `false` | Right-to-left text mode |

### Layouts

```js
pres.layout = 'LAYOUT_16x9';   // 10.0 × 5.625 inches
pres.layout = 'LAYOUT_4x3';    // 10.0 × 7.5 inches
pres.layout = 'LAYOUT_WIDE';   // 13.33 × 7.5 inches
pres.layout = 'LAYOUT_USER';   // use custom via defineLayout()

pres.defineLayout({ name: 'A4_LANDSCAPE', width: 11.69, height: 8.27 });
pres.layout = 'A4_LANDSCAPE';
```

### Methods

| Method | Returns | Description |
|--------|---------|-------------|
| `addSlide(opts?)` | Slide | Add a new slide |
| `defineSlideMaster(opts)` | void | Define a reusable slide master |
| `defineLayout(opts)` | void | Define a custom slide layout |
| `write(opts)` | Promise<any> | Serialize to buffer/base64/etc. |
| `writeFile(opts)` | Promise<string> | Save to .pptx file |

---

## Slide Object

```js
const slide = pres.addSlide({ masterName: 'MY_MASTER' });
slide.background = { fill: '1F4E79' };
slide.addNotes('Speaker notes here');
```

### Slide.addText(text, opts)

**text** can be a `string` or `Array<{ text, options }>` for mixed formatting.

Key options:

| Option | Type | Description |
|--------|------|-------------|
| `x, y` | number\|string | Position in inches or `'%'` |
| `w, h` | number\|string | Size in inches or `'%'` |
| `fontSize` | number | Font size in points |
| `bold` | boolean | Bold |
| `italic` | boolean | Italic |
| `underline` | object | `{ style: 'sng'\|'dbl' }` |
| `color` | string | Hex color (no `#`) |
| `fontFace` | string | Font family name |
| `align` | string | `'left'`, `'center'`, `'right'`, `'justify'` |
| `valign` | string | `'top'`, `'middle'`, `'bottom'` |
| `fill` | object | `{ color: 'XXXXXX' }` background fill |
| `line` | object | `{ color, width, dashType }` border |
| `shadow` | object | `{ type, color, blur, offset, angle, opacity }` |
| `rotate` | number | Degrees clockwise |
| `wrap` | boolean | Text wrapping (default `true`) |
| `autoFit` | boolean | Auto-shrink text to fit box |
| `margin` | number | Margin in inches |
| `paraSpaceBefore` | number | Space before paragraph (pt) |
| `paraSpaceAfter` | number | Space after paragraph (pt) |
| `lineSpacingMultiple` | number | Line height multiplier |
| `bullet` | boolean\|object | Enable bullets |
| `indentLevel` | number | Indent level for bullets |
| `hyperlink` | object | `{ url, slide, tooltip }` |
| `charSpacing` | number | Character spacing (pt) |
| `subscript` | boolean | Subscript text |
| `superscript` | boolean | Superscript text |
| `strike` | boolean | Strikethrough |
| `softBreakBefore` | boolean | Soft line break before run |

### Slide.addShape(shapeType, opts)

**ShapeType enum** (access via `pres.ShapeType.xxx`):

```
rect            roundRect        ellipse
triangle        rtTriangle       parallelogram
trapezoid       diamond          pentagon
hexagon         heptagon         octagon
decagon         dodecagon        star4
star5           star6            star7
star8           star10           star12
star16          star24           star32
ribbon          ribbon2          ellipseRibbon
ellipseRibbon2  callout1         callout2
callout3        accentCallout1   accentCallout2
accentCallout3  borderCallout1   borderCallout2
borderCallout3  accentBorderCallout1
line            bentConnector2   bentConnector3
bentConnector4  bentConnector5   curvedConnector2
curvedConnector3 curvedConnector4 curvedConnector5
rightArrow      leftArrow        upArrow
downArrow       leftRightArrow   upDownArrow
quadArrow       leftRightUpArrow bentUpArrow
stripedRightArrow notchedRightArrow pentagonRight
chevron         rightArrowCallout leftArrowCallout
upArrowCallout  downArrowCallout  leftRightArrowCallout
```

Shape options:

| Option | Type | Description |
|--------|------|-------------|
| `x, y, w, h` | number | Position and size in inches |
| `fill` | object | `{ color }` or `{ type: 'gradient', ... }` |
| `line` | object | `{ color, width, dashType }` |
| `shadow` | object | Shadow config |
| `rotate` | number | Rotation degrees |
| `rectRadius` | number | Corner radius (for roundRect) |
| `hyperlink` | object | Clickable link |
| `flipH` | boolean | Flip horizontally |
| `flipV` | boolean | Flip vertically |

### Slide.addImage(opts)

| Option | Type | Description |
|--------|------|-------------|
| `path` | string | File path or URL |
| `data` | string | Base64 `data:image/...;base64,...` |
| `x, y, w, h` | number | Position/size in inches |
| `sizing` | object | `{ type: 'contain'\|'cover'\|'crop', w, h }` |
| `rounding` | boolean | Circular crop |
| `rotate` | number | Degrees |
| `shadow` | object | Shadow |
| `hyperlink` | object | `{ url, tooltip }` |
| `transparency` | number | 0–100 |

### Slide.addChart(type, data, opts)

**ChartType enum** (via `pres.ChartType.xxx`):
`bar`, `barHoriz`, `line`, `area`, `scatter`, `bubble`, `pie`, `doughnut`, `radar`, `waterfall`

Data format:
```js
[
  {
    name: 'Series Name',
    labels: ['Label1', 'Label2'],  // X axis labels
    values: [100, 200],            // Y axis values
  },
]
```

Key chart options:

| Option | Type | Description |
|--------|------|-------------|
| `x, y, w, h` | number | Position/size |
| `barDir` | string | `'col'` (vertical) or `'bar'` (horizontal) |
| `barGrouping` | string | `'clustered'`, `'stacked'`, `'percentStacked'` |
| `chartColors` | string[] | Array of hex colors |
| `showLegend` | boolean | Show chart legend |
| `legendPos` | string | `'b'`, `'t'`, `'l'`, `'r'`, `'tr'` |
| `showValue` | boolean | Show data labels |
| `dataLabelColor` | string | Data label hex color |
| `showTitle` | boolean | Show chart title |
| `title` | string | Chart title text |
| `titleFontSize` | number | Title font size |
| `catAxisTitle` | string | X axis title |
| `valAxisTitle` | string | Y axis title |
| `valAxisMinVal` | number | Y axis minimum |
| `valAxisMaxVal` | number | Y axis maximum |
| `lineSize` | number | Line width (line charts) |
| `lineSmooth` | boolean | Smooth lines |
| `showDot` | boolean | Show data points |
| `dotSize` | number | Data point size |
| `showPercent` | boolean | Show % (pie/doughnut) |
| `holeSize` | number | Doughnut hole 0–100% |
| `secondValAxis` | boolean | Enable secondary Y axis |
| `catAxisLabelRotate` | number | Label rotation degrees |
| `catAxisLabelColor` | string | X label color |
| `valAxisLabelColor` | string | Y label color |
| `gridLineDash` | string | Grid line dash type |

### Slide.addTable(rows, opts)

**rows**: `Array<Array<string | { text, options }>>` — each inner array is a row.

Cell options mirror text options plus `colspan`, `rowspan`.

Table options:

| Option | Type | Description |
|--------|------|-------------|
| `x, y, w` | number | Position/width |
| `rowH` | number\|number[] | Row height(s) |
| `colW` | number[] | Column widths |
| `fontSize` | number | Default font size |
| `border` | object | `{ type: 'solid'\|'dash', pt, color }` |
| `fill` | object | Default cell fill |
| `color` | string | Default text color |
| `align` | string | Default alignment |
| `valign` | string | Default vertical alignment |
| `autoPage` | boolean | Auto-paginate long tables |
| `autoPageRepeatHeader` | boolean | Repeat header on new pages |

---

## write() Output Types

```js
const buf = await pres.write({ outputType: 'nodebuffer' });   // Node.js Buffer
const b64 = await pres.write({ outputType: 'base64' });       // base64 string
const ab  = await pres.write({ outputType: 'arraybuffer' });  // ArrayBuffer
const blob = await pres.write({ outputType: 'blob' });        // Blob (browser)
```

## writeFile() Options

```js
await pres.writeFile({ fileName: 'output.pptx' });
await pres.writeFile({ fileName: path.join(__dirname, 'output.pptx') });
```

---

## Common Recipes

### Title + Content Slide

```js
function makeTitleContentSlide(pres, title, bullets) {
  const slide = pres.addSlide();
  // Title band
  slide.addShape(pres.ShapeType.rect, { x: 0, y: 0, w: '100%', h: 1, fill: { color: '1F4E79' } });
  slide.addText(title, { x: 0.5, y: 0.1, w: 9, h: 0.8, fontSize: 28, bold: true, color: 'FFFFFF' });
  // Content
  slide.addText(
    bullets.map((b) => ({ text: b, options: { bullet: true } })),
    { x: 0.5, y: 1.2, w: 9, h: 4, fontSize: 18 }
  );
  return slide;
}
```

### Section Divider Slide

```js
function makeDividerSlide(pres, sectionTitle) {
  const slide = pres.addSlide();
  slide.background = { fill: '1F4E79' };
  slide.addText(sectionTitle, {
    x: 1, y: 2, w: 8, h: 1.5,
    fontSize: 48, bold: true, color: 'FFFFFF', align: 'center',
  });
  return slide;
}
```

### Thank You Slide

```js
function makeThankYouSlide(pres, contactEmail) {
  const slide = pres.addSlide();
  slide.background = { fill: 'F8F8F8' };
  slide.addText('Thank You', { x: 1, y: 1.5, w: 8, h: 1.5, fontSize: 54, bold: true, color: '1F4E79', align: 'center' });
  slide.addText(contactEmail, {
    x: 2, y: 3.5, w: 6, h: 0.6,
    fontSize: 20, color: '555555', align: 'center',
    hyperlink: { url: `mailto:${contactEmail}` },
  });
}
```
