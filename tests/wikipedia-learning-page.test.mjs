import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';

const page = fs.readFileSync('website/benchmarks.html', 'utf8');
const script = fs.readFileSync('website/benchmarks.js', 'utf8');
const map = JSON.parse(fs.readFileSync('website/data/wikipedia-learning-target-map.json', 'utf8'));

test('benchmark page exposes all goal and benchmark Wikipedia discovery links', () => {
  assert.match(page, /Wikipedia discovery linked to goals and benchmarks/);
  assert.match(page, /View the full machine-readable learning map/);
  assert.match(script, /data\/wikipedia-learning-target-map\.json/);
  assert.match(script, /noopener noreferrer/);
  assert.equal(map.goals.length, map.goal_count);
  assert.equal(map.benchmarks.length, map.benchmark_count);
  assert.ok(map.goals.every((row) => row.wikipedia_search_url.startsWith('https://en.wikipedia.org/w/index.php?search=')));
  assert.ok(map.benchmarks.every((row) => row.wikipedia_search_url.startsWith('https://en.wikipedia.org/w/index.php?search=')));
  assert.equal(map.training_policy, 'retrieval_only_until_explicit_consent_and_page_specific_rights_review');
});
