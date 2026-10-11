from tools.compile_division_catalog import compile_source,ROOT,CAPABILITIES,render

def test_authoritative_source_no_invention():
    result=compile_source((ROOT/'docs/imports/dreamco-superbot-source.txt').read_text())
    assert len(result['divisions'])==62
    assert len(CAPABILITIES)==20
    assert len(result['operations'])==1000
    assert result['catalog_complete'] is False
    assert all(not r['production_ready'] for r in result['operations'])
    assert sum(r['division_id']==61 for r in result['operations'])==200
    assert sum(r['division_id']==62 for r in result['operations'])==200

def test_dedup_and_source_hash():
    source='Division 1: One\nUpgrades 1–10\n1. Thing\n'
    assert len(compile_source(source*2)['operations'])==1
    assert compile_source(source)['source_sha256']!=compile_source(source+'\n')['source_sha256']

def test_html_escape(tmp_path):
    c=compile_source('Division 1: <script>\nUpgrades 1–10\n1. <img>\n')
    render(c,tmp_path)
    s=(tmp_path/'division-01.html').read_text()
    assert '<script>' not in s and '&lt;script&gt;' in s
