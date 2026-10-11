import pytest
from buddy.workbench.core import *

def test_token_bytes_are_not_characters():
    r=token_report('é🙂');assert r['characters']==2 and r['utf8_bytes']==6 and r['tokens']==6
    assert r['provider_billable_count'] is None

def test_usage_and_budget():
    assert usage(1000,100,50,1,2)['cost']==.0002
    assert usage(0,0,0)['tokens_per_second'] is None
    assert compare_attempts(1,2,3)['attempts']==1
    with pytest.raises(ValueError):usage(1,True,3)

def test_rubric_cannot_trade_safety_for_score():
    assert reward({'quality':1,'safety':0},{'quality':.9,'safety':.1},['safety'],True)['reward']==0
    assert reward({'quality':.5},{'quality':1},[],True)['reward']==.5
    with pytest.raises(ValueError):reward({'quality':float('nan')},{'quality':1},[])

def test_tenant_memory_and_consent(tmp_path):
    w=Workspace(tmp_path/'store.db')
    with pytest.raises(ValueError):w.save('a','chat','1',{'text':'private'})
    w.save('a','chat','1',{'text':'private'},True)
    assert w.memory_context('b',['1'])==[]
    assert w.memory_context('a',[])==[]
    w.forget('b','1');assert len(w.list('a','chat'))==1
    w.forget('a','1');assert w.list('a','chat')==[]
    with pytest.raises(ValueError):w.save('a','dashboard','x',{'widgets':['script']})

def test_train_generate_and_checkpoint(tmp_path):
    m=ByteModel()
    with pytest.raises(ValueError):m.train('hello')
    r=m.train('hello world '*30,True,'user-owned');assert r['production_ready'] is False
    assert m.generate('h',20,0,1)==m.generate('h',20,0,1)
    assert len(m.generate('h',20)['text'])>1
    m.save(tmp_path/'model.json');assert (tmp_path/'model.json').exists()

def test_microsite_escapes_content():
    s=microsite('Illinois','<script>','<img onerror=alert(1)>')
    assert '<script>' not in s and '<img' not in s

def test_bpe_real_merges_and_vocabulary_truth():
    b=BytePairTokenizer();r=b.train('hello hello hello café café 🙂🙂')
    assert r['learned_vocabulary']>256 and r['target_reached'] is False
    assert len(b.encode('hello hello'))<len('hello hello'.encode())
    assert b.inspect('未知🙂')['exact_reconstruction']
