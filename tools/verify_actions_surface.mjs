#!/usr/bin/env node
import fs from 'node:fs';

const files = ['website/actions.html','website/data/buddy-continuous-value-engine.json','website/data/buddy-work-to-value-engine.json','docs/BUDDY_CONTINUOUS_VALUE_ENGINE.md','docs/BUDDY_WORK_TO_VALUE_ENGINE.md'];
const required = ['Continuous Opportunity Scan','Problem → Business','Invention Lab','Productivity → Income','Failure Recovery','Scale What Works','Buddy PR Review Center','Buddy Money Opportunity Engine'];
const report = { files: {}, required_controls: {}, ok: true };
for (const file of files) {
  const exists = fs.existsSync(file);
  report.files[file] = exists;
  if (!exists) report.ok = false;
}
const html = fs.existsSync('website/actions.html') ? fs.readFileSync('website/actions.html','utf8') : '';
for (const label of required) {
  report.required_controls[label] = html.includes(label);
  if (!html.includes(label)) report.ok = false;
}
console.log(JSON.stringify(report,null,2));
process.exit(report.ok ? 0 : 1);
