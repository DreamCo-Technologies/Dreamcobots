"""Shared deterministic JSON and schema helpers."""
import argparse,json,hashlib
from pathlib import Path

def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def write_json(path,value):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def digest(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def validate(value,schema_name):
    try:
        import jsonschema
    except ImportError as exc:
        raise RuntimeError("Install requirements-reverse-engineer.txt (jsonschema) for contract validation.") from exc
    schema=read_json(Path(__file__).resolve().parents[1]/"contracts"/schema_name)
    jsonschema.Draft202012Validator(schema).validate(value)

def parser(description):
    p=argparse.ArgumentParser(description=description)
    p.add_argument("--input",required=True)
    p.add_argument("--output",required=True)
    return p
