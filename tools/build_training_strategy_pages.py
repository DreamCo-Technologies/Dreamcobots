#!/usr/bin/env python3
"""Publish canonical strategy policy without inventing experiments or metrics."""
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
import html,json
from buddy.learning.strategy_policy import registry

def generate():
    data=registry();out=ROOT/'website/data/training-strategy-registry.json';out.write_text(json.dumps(data,indent=2)+'\n')
    rows=''.join('<article><h2>'+html.escape(x['label'])+'</h2><p>Intervention tier '+str(x['tier'])+' · '+html.escape(x['execution_status'])+'</p><p>Requires: '+html.escape(', '.join(x['prerequisites']))+'</p><p>Stop: '+html.escape(', '.join(x['stop_criteria']))+'</p><p>Rollback: '+html.escape(x['rollback'])+'</p></article>' for x in data['strategies'])
    (ROOT/'website/training-strategies.html').write_text('<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Training Strategy Registry</title><style>body{font:16px system-ui;max-width:1100px;margin:2rem auto;padding:1rem}article{border:1px solid #aaa;padding:1rem;margin:1rem 0}</style><h1>Training Strategy Registry</h1><p>Selection considers measured pilot gains, rights, compatible adapters, intervention tier, and cost. No training is started by this page.</p><nav><a href="data/training-strategy-registry.json">Inspect registry</a> · <a href="general-intelligence.html">Review evidence</a> · <a href="resource-connection-center.html">Connect resources</a> · <a href="actions.html">Inspect workflows</a></nav><p>Experiment costs, benchmark deltas and accepted promotions: no new live evidence recorded.</p>'+rows+'</html>')
    return len(data['strategies'])
if __name__=='__main__':print(generate())
