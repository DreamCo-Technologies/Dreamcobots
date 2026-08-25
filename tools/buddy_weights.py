#!/usr/bin/env python3
"""Local checkpoint lifecycle for Buddy model weights.

Weights are produced by the local training process and stored as versioned
artifacts with metadata. No hosted checkpoint is implied by this module.
"""
from __future__ import annotations
import argparse, hashlib, json, os, time
from pathlib import Path


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest()


def write_checkpoint(model, optimizer, step: int, output: Path, config_name: str, metrics: dict):
    import torch
    output.mkdir(parents=True, exist_ok=True)
    weights=output/'model.safetensors'
    try:
        from safetensors.torch import save_file
        save_file(model.state_dict(), str(weights))
    except ImportError:
        weights=output/'model.pt'
        torch.save(model.state_dict(), weights)
    if optimizer is not None:
        torch.save(optimizer.state_dict(), output/'optimizer.pt')
    meta={
        'schema':'dreamco.buddy.checkpoint.v1',
        'created_at_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
        'step':step,
        'config':config_name,
        'weights_file':weights.name,
        'weights_sha256':sha256_file(weights),
        'metrics':metrics,
        'source':'locally_trained_checkpoint',
        'mastery_claim':False,
    }
    (output/'metadata.json').write_text(json.dumps(meta,indent=2)+'\n')
    return meta


def main():
    p=argparse.ArgumentParser(description='Buddy local weight artifact utility')
    p.add_argument('checkpoint_dir')
    p.add_argument('--verify',action='store_true')
    a=p.parse_args(); d=Path(a.checkpoint_dir); m=json.loads((d/'metadata.json').read_text())
    weights=d/m['weights_file']
    actual=sha256_file(weights)
    if actual != m['weights_sha256']:
        raise SystemExit('checkpoint integrity failure: SHA-256 mismatch')
    print(json.dumps({'valid':True,'step':m['step'],'weights':str(weights),'sha256':actual,'mastery_claim':False},indent=2))

if __name__=='__main__': main()
