import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';

test('training manifest validator exists',()=>assert.ok(fs.existsSync('tools/validate_training_execution_manifest.py')));
test('training execution cannot imply mastery',()=>{const p=fs.readFileSync('tools/execute_benchmark_training_queue.py','utf8');assert.match(p,/never claim training or mastery/);});
