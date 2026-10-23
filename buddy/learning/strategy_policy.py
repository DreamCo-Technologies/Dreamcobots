"""Evidence-first intervention selection over the canonical learning catalog.

This module selects proposals; execution remains with authorized existing adapters.
Costs and predicted gains must come from caller-supplied measured pilot evidence.
"""
from __future__ import annotations
import hashlib
import json
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HASH64 = re.compile(r'^[0-9a-f]{64}$')


def valid_hash(value):
    """Shape check only: a digest is not independently verified evidence."""
    return isinstance(value, str) and HASH64.fullmatch(value) is not None


NON_WEIGHT = ('prompt_optimization', 'router_optimization', 'retrieval_optimization',
              'memory_optimization', 'tool_policy_optimization', 'benchmark_only')


def finite(value, name, minimum=0):
    if type(value) not in (int, float) or not math.isfinite(value) or value < minimum:
        raise ValueError(f'{name} must be finite numeric >= {minimum}')
    return value


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()


def registry():
    source = json.loads((ROOT/'config/buddy-learning-strategies.json').read_text())
    rows = []
    for item in source['techniques']:
        stage = item['stage']
        tier = 1 if stage == 'adapter' else 3 if stage in ('pretraining', 'architecture') else 2
        rows.append({**item, 'tier': tier, 'changes_weights': True,
                     'prerequisites': ['licensed_trainable_weights', 'rights_cleared_data', 'heldout_set', 'reviewed_budget', 'compatible_adapter'],
                     'metrics': ['quality', 'safety', 'factuality', 'retention', 'latency_ms', 'cost_usd'],
                     'stop_criteria': ['budget_exceeded', 'heldout_regression', 'safety_regression', 'no_reproducible_gain'],
                     'rollback': 'restore_versioned_champion',
                     'do_not_use': ['missing_rights', 'contaminated_data', 'unsupported_model', 'unmeasured_baseline'],
                     'execution_status': 'adapter_and_authorization_required'})
    for name in NON_WEIGHT:
        rows.append({'id': name, 'label': name.replace('_', ' ').title(), 'tier': 0, 'changes_weights': False,
                     'prerequisites': ['versioned_baseline', 'heldout_set', 'reviewed_budget', 'compatible_adapter'],
                     'metrics': ['quality', 'safety', 'factuality', 'retention', 'latency_ms', 'cost_usd'],
                     'stop_criteria': ['budget_exceeded', 'regression', 'no_reproducible_gain'],
                     'rollback': 'restore_versioned_configuration', 'do_not_use': ['missing_baseline', 'unsupported_adapter'],
                     'execution_status': 'adapter_and_authorization_required'})
    return {'schema': 'dreamco.training_strategy_registry.v1', 'source_hash': digest(source), 'strategies': rows,
            'production_ready': False, 'frontier': False, 'mastery': False}


def validate_data(records, heldout_hashes):
    if (not isinstance(records, (list, tuple)) or not records
            or not isinstance(heldout_hashes, (list, tuple, set, frozenset)) or not heldout_hashes):
        raise ValueError('training and heldout records required')
    seen = set()
    for row in records:
        if not isinstance(row, dict):
            raise ValueError('training records must be objects')
        if row.get('training_allowed') is not True or row.get('rights_verified') is not True:
            raise ValueError('data rights not authorized')
        if (not isinstance(row.get('license'), str) or not row['license'].strip()
                or not isinstance(row.get('provenance'), str) or not row['provenance'].strip()):
            raise ValueError('license and provenance required')
        if not isinstance(row.get('text'), str) or not row['text'].strip():
            raise ValueError('nonempty training text required')
        h = hashlib.sha256(row['text'].strip().encode()).hexdigest()
        if h in seen or h in heldout_hashes:
            raise ValueError('duplicate or heldout contamination')
        seen.add(h)
    return sorted(seen)


def select(candidates, gap, budget_usd, model, data, heldout_hashes):
    finite(gap, 'gap'); finite(budget_usd, 'budget')
    if not isinstance(candidates, (list, tuple)):
        raise ValueError('strategy candidates must be a sequence')
    by_id = {x['id']: x for x in registry()['strategies']}
    eligible, rejected = [], []
    ids = set()
    for c in candidates:
        if not isinstance(c, dict):
            rejected.append({'strategy_id': None, 'reason': 'strategy candidate must be an object'})
            continue
        sid = c.get('strategy_id')
        try:
            if sid in ids: raise ValueError('duplicate strategy candidate')
            ids.add(sid)
            strategy = by_id[sid]
            cost = finite(c.get('estimated_cost_usd'), 'estimated cost')
            gain = finite(c.get('pilot_gain_lower_bound'), 'pilot gain')
            if (not valid_hash(c.get('pilot_receipt_hash'))
                    or not isinstance(c.get('baseline_revision'), str)
                    or not c['baseline_revision'].strip()):
                raise ValueError('well-formed pilot receipt hash and versioned baseline required')
            if c.get('adapter_verified') is not True or c.get('compatible') is not True:
                raise ValueError('compatible verified adapter required')
            if cost > budget_usd or gain < gap: raise ValueError('budget or expected gain insufficient')
            if strategy['changes_weights']:
                if not isinstance(model, dict):
                    raise ValueError('model metadata required for weight training')
                if model.get('training_allowed') is not True or model.get('rights_verified') is not True or model.get('weights_available') is not True:
                    raise ValueError('weight training rights unavailable')
                if model.get('ownership') not in ('dreamco', 'licensed_open') or not model.get('license'):
                    raise ValueError('proprietary or unlicensed weights prohibited')
                validate_data(data, heldout_hashes)
            eligible.append((strategy['tier'], cost, sid, c))
        except (ValueError, KeyError, TypeError) as e:
            rejected.append({'strategy_id': sid, 'reason': str(e)})
    eligible.sort(key=lambda x: x[:3])
    chosen = eligible[0][3] if eligible else None
    return {'selected': chosen, 'rejected': rejected, 'reason': 'lowest intervention tier, then lowest measured estimated cost' if chosen else 'no eligible strategy',
            'execution_authorized': False, 'production_ready': False}


def promotion(candidate, baseline, max_regression=0.0):
    """Validate repeat evidence; never independently authorize deployment."""
    finite(max_regression, 'max regression')
    reasons = []
    try:
        if not isinstance(candidate, dict) or not isinstance(baseline, dict):
            raise ValueError('candidate and baseline must be objects')
        if not isinstance(baseline.get('revision'), str) or not baseline['revision'].strip():
            raise ValueError('versioned baseline required')
        if candidate.get('baseline_revision') != baseline['revision']: raise ValueError('baseline mismatch')
        runs = candidate['runs']
        if not isinstance(runs, (list, tuple)) or len(runs) < 3 or any(not isinstance(r, dict) for r in runs):
            raise ValueError('three independent trial records required')
        if any(not isinstance(r.get('id'), str) or not r['id'].strip() or type(r.get('seed')) is not int for r in runs):
            raise ValueError('trial IDs and integer seeds required')
        if len({r['id'] for r in runs}) != len(runs): raise ValueError('three independent trial IDs required')
        if len({r['seed'] for r in runs}) != len(runs): raise ValueError('independent seeds required')
        for r in runs:
            for flag in ('heldout', 'uncontaminated', 'rights_verified', 'regression_passed'):
                if r.get(flag) is not True: raise ValueError(f'{flag} required')
            for key in ('quality','safety','factuality','retention'):
                score=finite(r[key], key); old=finite(baseline[key], key)
                if score > 1 or old > 1 or score + (0 if key == 'safety' else max_regression) < old: raise ValueError(key+' regression or range error')
            if r['quality'] <= baseline['quality']: raise ValueError('reproducible quality gain absent')
            for key in ('cost_usd','latency_ms'): finite(r[key], key)
            if (not valid_hash(r.get('receipt_hash')) or not valid_hash(r.get('config_hash'))
                    or not isinstance(r.get('hardware'), str) or not r['hardware'].strip()):
                raise ValueError('reproducibility metadata missing or malformed')
        if candidate.get('rollback_revision') != baseline['revision']: raise ValueError('rollback must restore the baseline revision')
    except (KeyError, ValueError, TypeError) as e: reasons.append(str(e))
    return {'eligible_for_review': not reasons, 'reasons': reasons, 'production_ready': False, 'frontier': False, 'mastery': False}


def rollback_decision(current_metrics, champion_metrics, champion_revision):
    if not champion_revision: raise ValueError('immutable champion revision required')
    regressions=[]
    for metric in ('quality','safety','factuality','retention'):
        try:
            if finite(current_metrics[metric],metric) < finite(champion_metrics[metric],metric):regressions.append(metric)
        except (KeyError,ValueError,TypeError):regressions.append(metric)
    return {'rollback_required': bool(regressions), 'restore_revision': champion_revision if regressions else None, 'regressions': regressions}
