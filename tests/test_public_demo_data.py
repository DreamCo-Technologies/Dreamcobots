from tools.generate_public_demo_data import ROOT, SOURCES, generate


def test_public_demo_data_matches_complete_canonical_inputs():
    assert generate(check=True) == []
    for name, source in SOURCES.items():
        assert (ROOT/'website/data/live-demos'/name).read_bytes() == (ROOT/source).read_bytes()


def test_generation_preserves_source_and_detects_drift(tmp_path):
    for source in SOURCES.values():
        path=tmp_path/source
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text('{"canonical":true}')
    assert len(generate(tmp_path,check=True)) == 4
    generate(tmp_path)
    assert generate(tmp_path,check=True) == []
    assert all((tmp_path/source).read_text() == '{"canonical":true}' for source in SOURCES.values())
