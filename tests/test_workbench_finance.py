import pytest
from buddy.workbench.finance import Ledger,paper_order

def test_ledger_balanced_isolated_idempotent(tmp_path):
    l=Ledger(tmp_path/'ledger.db');e=[{'account':'cash','cents':100},{'account':'equity','cents':-100}]
    l.post('a','one','USD',e);l.post('a','one','USD',e)
    assert l.balances('a','USD')['cash']==100 and l.balances('b','USD')=={}
    with pytest.raises(ValueError):l.post('a','one','EUR',e)
    with pytest.raises(ValueError):l.post('a','two','USD',[{'account':'cash','cents':100},{'account':'equity','cents':0}])

def test_paper_trade_risk_and_no_live_claim():
    r=paper_order('EXAMPLE','buy',2,10,30);assert r['submitted_to_broker'] is False
    with pytest.raises(ValueError):paper_order('EXAMPLE','buy',4,10,30)
    with pytest.raises(ValueError):paper_order('EXAMPLE','buy',True,10,30)
    with pytest.raises(ValueError):paper_order('EXAMPLE','buy','NaN',10,30)
