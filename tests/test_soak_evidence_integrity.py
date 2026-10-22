import hashlib
import json
import unittest
from datetime import datetime, timedelta, timezone
from tools.soak_evidence_integrity import validate_runtime_soak


def digest(body):
    return hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def fixture():
    start = datetime(2026, 10, 1, tzinfo=timezone.utc)
    receipts = []
    previous = ""
    for i in range(25):
        r = {"schema":"dreamco.sandbox_runtime_receipt.v1","status":"runtime_probe_passed","runtime_verified":True,
             "probe":{"ok":True},"run_id":f"run-{i}","repo_commit":"a"*40,"fleet_sha256":"b"*64,
             "generated_at":(start+timedelta(hours=i)).isoformat(),"previous_sha256":previous}
        r["receipt_sha256"] = digest(r)
        receipts.append(r)
        previous = r["receipt_sha256"]
    tick = {**receipts[-1],"status":"sandbox_tick_ok","coverage":{"runtime_24h_verified":True,"coverage_seconds":86400}}
    return tick, receipts

class TestSoak(unittest.TestCase):
    def assert_invalid(self, tick, history):
        errors=[]
        self.assertFalse(validate_runtime_soak(tick,history,errors))
        self.assertTrue(errors)
    def test_valid_structure(self):
        tick, history=fixture()
        self.assertTrue(validate_runtime_soak(tick,history,[]))
    def test_inventory_only(self):
        tick, history=fixture();tick['runtime_verified']=False
        self.assert_invalid(tick,history)
    def test_status_only_fake(self):
        self.assert_invalid({'status':'sandbox_tick_ok'},[])
    def test_missing_history(self):
        tick, history=fixture();self.assert_invalid(tick,history[:2])
    def test_hash_tamper(self):
        tick, history=fixture();history[3]['probe']['ok']=False
        self.assert_invalid(tick,history)
    def test_gap(self):
        tick, history=fixture();history[3]['generated_at']=(datetime(2026,10,1,tzinfo=timezone.utc)+timedelta(hours=6)).isoformat()
        for i,r in enumerate(history):
            r['previous_sha256']=history[i-1]['receipt_sha256'] if i else ''
            r['receipt_sha256']=digest({k:v for k,v in r.items() if k!='receipt_sha256'})
        tick['receipt_sha256']=history[-1]['receipt_sha256']
        self.assert_invalid(tick,history)
    def test_mixed_commit(self):
        tick, history=fixture();history[12]['repo_commit']='c'*40
        self.assert_invalid(tick,history)
    def test_false_coverage(self):
        tick, history=fixture();tick['coverage']['coverage_seconds']=86401
        self.assert_invalid(tick,history)
    def test_duplicate_run(self):
        tick, history=fixture();history[3]['run_id']=history[2]['run_id']
        self.assert_invalid(tick,history)
    def test_missing_probe(self):
        tick, history=fixture();history[1].pop('probe')
        self.assert_invalid(tick,history)

if __name__ == '__main__': unittest.main()
