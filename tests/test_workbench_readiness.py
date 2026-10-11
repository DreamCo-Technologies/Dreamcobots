import pytest
from buddy.workbench.readiness import qualify_model,payment_readiness,audit_seo,capacity_gate,gpu_inventory


def test_vocabulary_is_tokens_and_not_qualification():
    r=qualify_model(1_000_000_000,training=True,available_bytes=24*1024**3)
    assert r['vocabulary_tokens']==150000 and r['vocabulary_words'] is None
    assert r['fits_lower_bound'] and not r['qualified']
    with pytest.raises(ValueError): qualify_model(True)
    with pytest.raises(ValueError): qualify_model(100)


def test_card_alone_does_not_enable_payments():
    assert not payment_readiness({'tenant_id':'a','card_connected':True},'a')['payment_collection_ready']
    with pytest.raises(ValueError): payment_readiness({'tenant_id':'b'},'a')
    a=dict(tenant_id='a',provider_verified=True,charges_enabled=True,payouts_enabled=True,details_submitted=True,requirements_due=[],capabilities={'card_payments':'active'})
    assert payment_readiness(a,'a')['payment_collection_ready']
    a['payouts_enabled']='true'
    assert not payment_readiness(a,'a')['payment_collection_ready']


def test_seo_reports_missing_and_valid_metadata():
    assert 'title' in audit_seo('<html><img src="x"></html>')['failed']
    html='<html lang="en"><title>Shop</title><meta name="description" content="Local shop"><link rel="canonical" href="https://example.com"><h1>Shop</h1><img alt="" src="x"></html>'
    assert not audit_seo(html)['failed']
    assert not audit_seo(html)['ranking_guaranteed']


def test_capacity_requires_actual_receipt():
    assert not capacity_gate({})['capacity_verified']
    assert not capacity_gate(dict(concurrent_users=1000,duration_seconds=3600,requests=10,error_rate=float('nan'),p95_ms=20))['capacity_verified']


def test_missing_gpu_does_not_qualify(monkeypatch):
    monkeypatch.setattr('buddy.workbench.readiness.shutil.which',lambda _:None)
    assert gpu_inventory()['status']=='unavailable'
