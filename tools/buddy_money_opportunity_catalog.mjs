#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const catalogPath = path.resolve('website/data/buddy-money-opportunity-catalog.json');
const catalog = JSON.parse(fs.readFileSync(catalogPath, 'utf8'));
const query = process.argv.slice(2).join(' ').trim().toLowerCase();

if (!query) {
  console.log(JSON.stringify({categories: catalog.catalog_categories.map(({id,name}) => ({id,name})), dimensions: catalog.dimensions}, null, 2));
  process.exit(0);
}

const terms = query.split(/\s+/).filter(Boolean);
const ranked = catalog.catalog_categories.map(category => {
  const text = JSON.stringify(category).toLowerCase();
  const score = terms.reduce((n, term) => n + (text.includes(term) ? 1 : 0), 0);
  return { category, score };
}).filter(x => x.score > 0).sort((a,b) => b.score - a.score || a.category.name.localeCompare(b.category.name));

console.log(JSON.stringify({query, results: ranked.map(x => x.category), count: ranked.length, policy: catalog.truth_policy}, null, 2));
