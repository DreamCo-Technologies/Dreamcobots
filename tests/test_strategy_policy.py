import copy
import hashlib
import pytest
from buddy.learning.strategy_policy import registry,select,validate_data,promotion,rollback_decision


def candidate(s='prompt_optimization', cost=0):
    return dict(strategy_id=s,estimated_cost_usd=cost,pilot_gain_lower_bound=.2,pilot_receipt_hash='a'*64,baseline_revision='v1',adapter_verified=True,compatible=True)


def test_catalog_and_cheapest_tier():
    assert len(registry()['strategies']) >= 78
    r=select([candidate(cost=3),candidate('router_optimization',1)],.1,5,{},[],[])
    assert r['selected']['strategy_id']=='router_optimization'
    assert r['execution_authorized'] is False


@pytest.mark.parametrize('bad',[True,float('nan'),float('inf'),-1,'2'])
def test_invalid_cost(bad):
    assert select([candidate(cost=bad)],.1,5,{},[],[])['selected'] is None


def test_rights_and_contamination():
    c=candidate('lora_adapter')
    assert select([c],.1,5,{},[],[])['selected'] is None
    row=dict(text='example',training_allowed=True,rights_verified=True,license='MIT',provenance='owned fixture')
    with pytest.raises(ValueError):validate_data([row,row],['heldout'])
    with pytest.raises(ValueError):validate_data([row],[hashlib.sha256(b'example').hexdigest()])
    with pytest.raises(ValueError):validate_data([{**row,'training_allowed':'true'}],['heldout'])


def test_promotion_and_rollback():
    base=dict(revision='v1',quality=.5,safety=1,factuality=1,retention=1)
    runs=[dict(id=str(i),seed=i,quality=.7,safety=1,factuality=1,retention=1,cost_usd=0,latency_ms=1,heldout=True,uncontaminated=True,rights_verified=True,regression_passed=True,receipt_hash='a'*64,config_hash='b'*64,hardware='fixture') for i in range(3)]
    c=dict(baseline_revision='v1',runs=runs,rollback_revision='v1')
    assert promotion(c,base)['eligible_for_review']
    assert promotion(c,base)['production_ready'] is False
    bad=copy.deepcopy(c);bad['runs'][0]['retention']=.2
    assert not promotion(bad,base)['eligible_for_review']
    bad=copy.deepcopy(c);bad['runs'][1]['seed']=0
    assert not promotion(bad,base)['eligible_for_review']
    assert rollback_decision({},base,'v1')['rollback_required']
