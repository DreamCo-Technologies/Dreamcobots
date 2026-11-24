import json
from pathlib import Path

def test_tolkien_track_is_curriculum_only_and_copyright_gated():
 root=Path(__file__).resolve().parents[1];track=json.loads((root/"config/buddy-tolkien-study-track.json").read_text(encoding="utf-8"))
 rights=track["rights_policy"]
 assert rights["copyrighted_tolkien_text_ingestion"] is False
 assert rights["training_on_copyrighted_tolkien_text"] is False
 assert rights["verbatim_text_reproduction"] is False
 assert rights["unknown_rights"]=="BLOCK"
 assert len(track["curriculum"])>=8
 assert track["assessment"]["holdout_policy"]

def test_tolkien_track_requires_item_level_translation_and_edition_review():
 root=Path(__file__).resolve().parents[1];track=json.loads((root/"config/buddy-tolkien-study-track.json").read_text(encoding="utf-8"))
 assert any("verify edition and translation rights individually" in x["scope"] for x in track["source_families"])
 assert "Do not ingest Tolkien novels" in track["safeguards"][0]
