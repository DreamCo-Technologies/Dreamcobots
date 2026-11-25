import hashlib, tempfile, unittest
from pathlib import Path
from buddy.learning.byte_bpe_trainer import train_byte_bpe, train_from_manifest, encode, decode, prepare_corpus_splits

def authorized_manifest(root,content=b"banana bandana banana"):
 path=root/"data/buddy-authorized-corpora"/"sample.txt"; path.parent.mkdir(parents=True); path.write_bytes(content)
 return {"schema":"dreamco.authorized_tokenizer_corpus_manifest.v1","corpora":[{"source_id":"synthetic-1","path":"data/buddy-authorized-corpora/sample.txt","sha256":hashlib.sha256(content).hexdigest(),"source_type":"synthetic","rights_verified":True,"model_training_permission":True,"privacy_reviewed":True,"holdout":False,"sensitive":False,"license_evidence_ref":"synthetic-test-fixture"}]}

class ByteBpeTrainerTests(unittest.TestCase):
 def test_round_trip_preserves_unicode_and_punctuation(self):
  texts=[b"hello hello", "DreamCo 🚀 tokenizer".encode("utf-8")]
  model=train_byte_bpe(texts,300)
  for text in ["hello hello","DreamCo 🚀 tokenizer","", "漢字 — café"]:
   self.assertEqual(decode(encode(text,model)),text)
 def test_vocab_size_never_exceeds_target(self):
  model=train_byte_bpe([b"abababababab"],260)
  self.assertLessEqual(model["vocab_size"],260)
 def test_rights_gated_manifest_trains_only_authorized_local_corpus(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); manifest=authorized_manifest(root); model=train_from_manifest(manifest,root=root,vocab_size=270)
   self.assertTrue(model["rights_gate_passed"]); self.assertFalse(model["model_weight_training_executed"]); self.assertFalse(model["training_data_downloaded"])
 def test_unknown_rights_block_training(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); manifest=authorized_manifest(root); manifest["corpora"][0]["model_training_permission"]=False
   with self.assertRaisesRegex(PermissionError,"model_training_permission"): train_from_manifest(manifest,root=root)
 def test_holdout_data_cannot_be_used_for_training(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); manifest=authorized_manifest(root); manifest["corpora"][0]["holdout"]=True
   with self.assertRaisesRegex(PermissionError,"holdout"): train_from_manifest(manifest,root=root)
 def test_path_traversal_is_blocked(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); manifest=authorized_manifest(root); manifest["corpora"][0]["path"]="data/buddy-authorized-corpora/../../secret.txt"
   with self.assertRaisesRegex(PermissionError,"escapes"): train_from_manifest(manifest,root=root)
 def test_changed_corpus_hash_is_blocked(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); manifest=authorized_manifest(root); manifest["corpora"][0]["sha256"]="0"*64
   with self.assertRaisesRegex(ValueError,"SHA-256 mismatch"): train_from_manifest(manifest,root=root)

 def test_model_foundry_bpe_split_trains_tokenizer_on_train_only(self):
  raw=(b"abcd " * 640)+(b"ZZZZ " * 128)
  prepared=prepare_corpus_splits(raw,tokenizer_type="byte_bpe",vocab_size=280)
  self.assertTrue(prepared["tokenizer"]["trained_on_training_split_only"])
  self.assertFalse(prepared["tokenizer"]["holdout_used_for_training"])
  self.assertEqual(prepared["tokenizer"]["training_split_sha256"],hashlib.sha256(raw[:int(len(raw)*0.8)]).hexdigest())
  self.assertFalse(any("5a5a" in merge["token_hex"] for merge in prepared["tokenizer_artifact"]["merges"]))
  self.assertTrue(all(0<=token<prepared["tokenizer"]["vocabulary_size"] for token in prepared["holdout_ids"]))

 def test_byte_level_split_keeps_existing_256_token_contract(self):
  prepared=prepare_corpus_splits(b"abcde " * 400,tokenizer_type="byte_level")
  self.assertEqual(prepared["tokenizer"]["vocabulary_size"],256)
  self.assertFalse(prepared["tokenizer"]["holdout_used_for_training"])

 def test_bpe_mode_rejects_invalid_utf8_and_unknown_tokenizer(self):
  with self.assertRaisesRegex(ValueError,"UTF-8"):
   prepare_corpus_splits(b"a"*1000+b"\\xff"*24,tokenizer_type="byte_bpe")
  with self.assertRaisesRegex(ValueError,"tokenizer_type"):
   prepare_corpus_splits(b"abcde "*300,tokenizer_type="unknown")


if __name__=="__main__": unittest.main()
