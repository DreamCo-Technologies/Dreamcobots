import importlib.util
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("dreamco_global_reconciliation",ROOT/"tools/dreamco_global_reconciliation.py")
MODULE=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)

def test_requirement_ids_are_stable():
    assert MODULE.stable_id("docs/a.md","same requirement") == MODULE.stable_id("docs/a.md","same   requirement")

def test_requirement_ids_include_source_path():
    assert MODULE.stable_id("docs/a.md","same") != MODULE.stable_id("docs/b.md","same")

def test_chat_sources_are_scoped_to_explicit_intake():
    assert MODULE.CHAT_ROOT == ROOT/"governance"/"dreamco-chat-sources"

def test_evidence_map_does_not_claim_automatic_verification():
    assert MODULE.EVIDENCE_MAP.name == "dreamco-requirement-evidence.json"
    assert '"requirements": {}' in MODULE.EVIDENCE_MAP.read_text(encoding="utf-8")

def test_markdown_extraction_preserves_line_and_section(tmp_path):
    p=tmp_path/"sample.md"
    p.write_text("# Section\n\n- [ ] Implement durable reconciliation evidence mapping.\n",encoding="utf-8")
    rows=MODULE.extract_requirements(p)
    assert len(rows)==1
    assert rows[0]["line"]==3
    assert rows[0]["section"]=="Section"
    assert rows[0]["source_type"]=="markdown"
