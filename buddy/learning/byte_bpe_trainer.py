"""Rights-gated deterministic byte-level BPE tokenizer trainer.

No network access, third-party downloads, model-weight training, or automatic
training is performed. The CLI requires a local rights-cleared corpus manifest
and an explicit confirmation flag.
"""
from __future__ import annotations
import argparse, hashlib, json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

SCHEMA="dreamco.byte_bpe_tokenizer.v1"
MANIFEST_SCHEMA="dreamco.authorized_tokenizer_corpus_manifest.v1"
ALLOWED_ROOT="data/buddy-authorized-corpora"

def sha256_file(path:Path)->str:
 digest=hashlib.sha256()
 with path.open("rb") as handle:
  for chunk in iter(lambda:handle.read(1024*1024),b""): digest.update(chunk)
 return digest.hexdigest()

def _safe_path(value:str,root:Path)->Path:
 if not isinstance(value,str) or not value.startswith(ALLOWED_ROOT+"/"):
  raise PermissionError("corpus path must be inside "+ALLOWED_ROOT)
 allowed=(root/ALLOWED_ROOT).resolve()
 candidate=(root/value).resolve()
 try: candidate.relative_to(allowed)
 except ValueError as exc: raise PermissionError("corpus path escapes the authorized corpus directory") from exc
 if not candidate.is_file(): raise FileNotFoundError(candidate)
 return candidate

def load_authorized_corpus(manifest:dict[str,Any],*,root:Path)->tuple[list[bytes],list[dict[str,str]]]:
 if manifest.get("schema")!=MANIFEST_SCHEMA: raise ValueError("unsupported authorized tokenizer corpus manifest")
 entries=manifest.get("corpora")
 if not isinstance(entries,list) or not entries: raise ValueError("at least one corpus record is required")
 sequences=[]; provenance=[]; seen=set()
 for entry in entries:
  if not isinstance(entry,dict): raise ValueError("corpus entries must be objects")
  source_id=entry.get("source_id")
  if not isinstance(source_id,str) or not source_id.strip() or source_id in seen: raise ValueError("source_id values must be unique and non-empty")
  seen.add(source_id)
  for key in ("rights_verified","model_training_permission","privacy_reviewed"):
   if entry.get(key) is not True: raise PermissionError(f"{source_id}: {key} must be explicitly true")
  if entry.get("holdout") is not False: raise PermissionError(f"{source_id}: holdout corpora cannot be used for training")
  if entry.get("sensitive") is not False: raise PermissionError(f"{source_id}: sensitive data is blocked")
  if entry.get("source_type") not in {"synthetic","first_party","public_domain","licensed"}: raise PermissionError(f"{source_id}: source_type is not approved")
  if not isinstance(entry.get("license_evidence_ref"),str) or not entry["license_evidence_ref"].strip(): raise PermissionError(f"{source_id}: license evidence reference is required")
  path=_safe_path(entry.get("path",""),root)
  actual=sha256_file(path)
  if entry.get("sha256")!=actual: raise ValueError(f"{source_id}: corpus SHA-256 mismatch")
  raw=path.read_bytes()
  try: raw.decode("utf-8")
  except UnicodeDecodeError as exc: raise ValueError(f"{source_id}: corpus must be valid UTF-8") from exc
  if raw: sequences.append(list(raw))
  provenance.append({"source_id":source_id,"path":entry["path"],"sha256":actual,"source_type":entry["source_type"],"license_evidence_ref":entry["license_evidence_ref"]})
 if not sequences: raise ValueError("authorized corpus contains no training bytes")
 return [bytes(row) for row in sequences],provenance

def train_byte_bpe(texts:Iterable[bytes],vocab_size:int=512)->dict[str,Any]:
 if not isinstance(vocab_size,int) or isinstance(vocab_size,bool) or not 256<=vocab_size<=65536:
  raise ValueError("vocab_size must be an integer between 256 and 65536")
 sequences=[list(text) for text in texts if text]
 if not sequences: raise ValueError("at least one non-empty training sequence is required")
 merges=[]
 while 256+len(merges)<vocab_size:
  counts=Counter()
  for seq in sequences: counts.update(zip(seq,seq[1:]))
  if not counts: break
  best_count=max(counts.values())
  if best_count<2: break
  pair=min(pair for pair,count in counts.items() if count==best_count)
  merged=pair[0]+pair[1]
  updated=[]
  for seq in sequences:
   out=[]; i=0
   while i<len(seq):
    if i+1<len(seq) and (seq[i],seq[i+1])==pair:
     out.append(merged); i+=2
    else: out.append(seq[i]); i+=1
   updated.append(out)
  sequences=updated
  merges.append({"left_hex":pair[0].hex(),"right_hex":pair[1].hex(),"token_hex":merged.hex(),"frequency":best_count})
 vocab=list(dict.fromkeys([bytes([i]).hex() for i in range(256)]+[row["token_hex"] for row in merges]))
 return {"schema":SCHEMA,"algorithm":"deterministic_byte_level_bpe","vocab_size":len(vocab),"requested_vocab_size":vocab_size,"vocab_hex":vocab,"merges":merges,"training_executed":True,"model_weight_training_executed":False,"training_data_downloaded":False}

def encode(text:str,tokenizer:dict[str,Any])->list[str]:
 pieces=[bytes([value]) for value in text.encode("utf-8")]
 for merge in tokenizer["merges"]:
  left=bytes.fromhex(merge["left_hex"]); right=bytes.fromhex(merge["right_hex"]); merged=bytes.fromhex(merge["token_hex"])
  output=[]; i=0
  while i<len(pieces):
   if i+1<len(pieces) and pieces[i]==left and pieces[i+1]==right:
    output.append(merged); i+=2
   else: output.append(pieces[i]); i+=1
  pieces=output
 return [piece.hex() for piece in pieces]

def decode(token_hex:list[str])->str:
 return b"".join(bytes.fromhex(token) for token in token_hex).decode("utf-8")

def train_from_manifest(manifest:dict[str,Any],*,root:Path,vocab_size:int=512)->dict[str,Any]:
 texts,provenance=load_authorized_corpus(manifest,root=root)
 tokenizer=train_byte_bpe(texts,vocab_size)
 tokenizer["training_provenance"]=provenance
 tokenizer["rights_gate_passed"]=True
 tokenizer["holdout_used_for_training"]=False
 tokenizer["model_weight_training_executed"]=False
 return tokenizer

def main()->int:
 parser=argparse.ArgumentParser(description=__doc__)
 parser.add_argument("--manifest",required=True,type=Path)
 parser.add_argument("--output",required=True,type=Path)
 parser.add_argument("--root",type=Path,default=Path.cwd())
 parser.add_argument("--vocab-size",type=int,default=512)
 parser.add_argument("--confirm-authorized-training",action="store_true")
 args=parser.parse_args()
 if not args.confirm_authorized_training: raise SystemExit("Refusing to train: pass --confirm-authorized-training only after confirming corpus rights and scope.")
 manifest=json.loads(args.manifest.read_text(encoding="utf-8"))
 model=train_from_manifest(manifest,root=args.root.resolve(),vocab_size=args.vocab_size)
 args.output.parent.mkdir(parents=True,exist_ok=True)
 args.output.write_text(json.dumps(model,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({"status":"tokenizer_trained","vocab_size":model["vocab_size"],"model_weight_training_executed":False,"corpus_count":len(model["training_provenance"])},indent=2))
 return 0
if __name__=="__main__": raise SystemExit(main())
