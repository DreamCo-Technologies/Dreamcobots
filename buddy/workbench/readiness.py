"""Readiness estimates and gates; never substitutes estimates for live evidence."""
import math
import re
import shutil
import subprocess
from html.parser import HTMLParser
from urllib.parse import urlparse


def positive_int(value):
    if type(value) is not int or value <= 0:
        raise ValueError('positive integer required')
    return value


def gpu_inventory():
    executable = shutil.which('nvidia-smi')
    if not executable:
        return {'status': 'unavailable', 'devices': [], 'reason': 'NVIDIA probe unavailable; other accelerators require an adapter'}
    try:
        result = subprocess.run([executable, '--query-gpu=name,memory.free', '--format=csv,noheader,nounits'], capture_output=True, text=True, timeout=5, check=True)
        devices = []
        for line in result.stdout.splitlines():
            name, memory = line.rsplit(',', 1)
            devices.append({'name': name.strip(), 'free_bytes': positive_int(int(memory.strip())) * 1024**2})
        return {'status': 'measured' if devices else 'unavailable', 'devices': devices}
    except (OSError, ValueError, subprocess.SubprocessError):
        return {'status': 'unavailable', 'devices': [], 'reason': 'probe failed'}


def qualify_model(parameters, vocabulary=150000, hidden_size=1024, training=False, available_bytes=None):
    for value in (parameters, vocabulary, hidden_size):
        positive_int(value)
    if type(training) is not bool:
        raise ValueError('training must be boolean')
    if available_bytes is not None:
        positive_int(available_bytes)
    # Parameter count must include embeddings. Untied output heads need more parameters.
    embedding_parameters = vocabulary * hidden_size
    if parameters < embedding_parameters:
        raise ValueError('parameter count cannot be smaller than the embedding table')
    lower_bound = parameters * (16 if training else 2)
    return {'vocabulary_tokens': vocabulary, 'vocabulary_words': None,
            'embedding_parameters': embedding_parameters, 'memory_lower_bound_bytes': lower_bound,
            'fits_lower_bound': None if available_bytes is None else available_bytes >= lower_bound,
            'qualified': False, 'production_ready': False,
            'required': ['model-specific activation and context memory measurement', 'supported trainer and accelerator', 'rights-cleared data and weights', 'held-out evaluation', 'successful bounded trial'],
            'explanation': 'FP16 inference or mixed-precision Adam training lower bound excludes activations, KV cache, runtime and temporary buffers; tokens are not words.'}


def payment_readiness(account, tenant_id):
    if not isinstance(account, dict) or not tenant_id or account.get('tenant_id') != tenant_id:
        raise ValueError('authenticated account ownership required')
    required = ('provider_verified', 'charges_enabled', 'payouts_enabled', 'details_submitted')
    missing = [key for key in required if account.get(key) is not True]
    if account.get('requirements_due') != []:
        missing.append('requirements_due')
    capabilities = account.get('capabilities', {})
    if not isinstance(capabilities, dict) or capabilities.get('card_payments') != 'active':
        missing.append('card_payments')
    return {'payment_collection_ready': not missing, 'blockers': missing,
            'card_connected': account.get('card_connected') is True,
            'bank_account_created': False, 'money_moved': False,
            'instant_payout_eligible': not missing and account.get('instant_payout_eligible') is True,
            'source': 'server-side provider snapshot required; never trust browser-supplied flags'}


class SEOParser(HTMLParser):
    def __init__(self):
        super().__init__(); self.title = ''; self.in_title = False; self.h1 = 0; self.lang = ''; self.description = ''; self.canonical = ''; self.missing_alt = 0
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'title': self.in_title = True
        if tag == 'html': self.lang = a.get('lang', '')
        if tag == 'h1': self.h1 += 1
        if tag == 'meta' and a.get('name', '').lower() == 'description': self.description = a.get('content', '')
        if tag == 'link' and 'canonical' in a.get('rel', '').split(): self.canonical = a.get('href', '')
        if tag == 'img' and 'alt' not in a: self.missing_alt += 1
    def handle_endtag(self, tag):
        if tag == 'title': self.in_title = False
    def handle_data(self, data):
        if self.in_title: self.title += data


def audit_seo(document):
    if not isinstance(document, str): raise ValueError('HTML required')
    p = SEOParser(); p.feed(document)
    checks = {'title': bool(p.title.strip()), 'description': bool(p.description.strip()),
              'language': bool(p.lang), 'primary_heading': p.h1 == 1,
              'canonical_https': urlparse(p.canonical).scheme == 'https' and bool(urlparse(p.canonical).netloc),
              'image_alt_attributes': p.missing_alt == 0}
    return {'checks': checks, 'failed': [k for k,v in checks.items() if not v],
            'scope': 'static on-page checks only', 'ranking_guaranteed': False,
            'unmeasured': ['crawlability', 'indexing', 'Core Web Vitals', 'structured data validity', 'local business accuracy', 'international hreflang', 'content quality', 'search performance']}


def capacity_gate(receipt, target=1000):
    positive_int(target)
    if not isinstance(receipt, dict): raise ValueError('receipt required')
    numeric = ('concurrent_users', 'duration_seconds', 'requests', 'error_rate', 'p95_ms')
    valid = all(type(receipt.get(k)) in (int,float) and math.isfinite(receipt[k]) for k in numeric)
    passed = valid and receipt['concurrent_users'] >= target and receipt['duration_seconds'] >= 3600 and receipt['requests'] > 0 and 0 <= receipt['error_rate'] <= .01 and 0 < receipt['p95_ms'] <= 1000
    passed = passed and receipt.get('tenant_isolation_passed') is True and receipt.get('production_equivalent') is True and isinstance(receipt.get('artifact_sha256'), str) and re.fullmatch(r'[0-9a-f]{64}', receipt['artifact_sha256']) is not None and isinstance(receipt.get('service'), str) and bool(receipt['service'].strip())
    return {'target_concurrent_users': target, 'capacity_verified': bool(passed), 'scope': receipt.get('service'), 'production_ready': False}
