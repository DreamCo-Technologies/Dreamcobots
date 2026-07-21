# File Reading Skill

Read and parse common file formats in Node.js.

## Supported Formats

| Format | Library | Notes |
|--------|---------|-------|
| JSON | built-in | `JSON.parse()` |
| JSONL | built-in | split on `\n` |
| CSV | csv-parse | auto-cast types |
| TSV | csv-parse | `delimiter: '\t'` |
| YAML | yaml | multi-doc support |
| XML | xml2js | → JS object |
| TOML | @iarna/toml | Rust Cargo.toml, etc. |
| INI | ini | .env.ini, config files |
| Plain text | built-in | readline streaming |
| Binary | built-in | Buffer + fd ops |

## Quick Start

```js
const fs = require('fs');

// JSON
const data = JSON.parse(await fs.promises.readFile('data.json', 'utf8'));

// CSV (streaming for large files)
const { parse } = require('csv-parse');
for await (const row of fs.createReadStream('data.csv').pipe(parse({ columns: true }))) {
  console.log(row);
}

// YAML
const YAML = require('yaml');
const config = YAML.parse(fs.readFileSync('config.yml', 'utf8'));

// XML
const xml2js = require('xml2js');
const obj = await xml2js.parseStringPromise(fs.readFileSync('data.xml', 'utf8'), { explicitArray: false });
```

## Tips

- Always use streaming (`readline`, `csv-parse` pipe) for files > 50 MB
- Detect encoding with `chardet` before reading non-UTF-8 files
- Check file magic bytes to verify type before parsing
- Use `csv-parse/sync` for small files when async isn't needed
