#!/usr/bin/env python3
"""Minimal from-scratch local training loop for a causal language model.

The model class is intentionally supplied by the caller/project runtime; this
script handles reproducible batching, validation, gradient accumulation and
local checkpoint creation without distributed training.
"""
from __future__ import annotations
import argparse, json, random
from pathlib import Path

def seed_all(seed):
    random.seed(seed)
    import torch
    torch.manual_seed(seed)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(seed)

def run(model, train_batches, val_batches, optimizer, device, steps, grad_accum, checkpoint_root, config_name, save_every):
    import torch
    model.to(device); model.train(); optimizer.zero_grad(set_to_none=True)
    step=0; best=float('inf')
    for batch in train_batches:
        step += 1
        ids=batch['input_ids'].to(device); labels=batch['labels'].to(device)
        with torch.autocast(device_type=('cuda' if device.startswith('cuda') else 'cpu'), enabled=device.startswith('cuda')):
            loss=model(input_ids=ids, labels=labels).loss
        (loss/grad_accum).backward()
        if step % grad_accum == 0:
            torch.nn.utils.clip_grad_norm_(model.parameters(),1.0); optimizer.step(); optimizer.zero_grad(set_to_none=True)
        if step % save_every == 0:
            val=validate(model,val_batches,device)
            model.train()
            metrics={'train_loss':float(loss.detach().cpu()),'validation_loss':val}
            out=Path(checkpoint_root)/f'step-{step}'
            from buddy_weights import write_checkpoint
            write_checkpoint(model,optimizer,step,out,config_name,metrics)
            if val < best: best=val; (Path(checkpoint_root)/'BEST').write_text(str(out))
        if step >= steps: break
    return {'steps':step,'best_validation_loss':best}

def validate(model,batches,device):
    import torch
    model.eval(); vals=[]
    with torch.no_grad():
        for batch in batches:
            ids=batch['input_ids'].to(device); labels=batch['labels'].to(device)
            vals.append(float(model(input_ids=ids,labels=labels).loss.detach().cpu()))
    return sum(vals)/len(vals) if vals else float('inf')

def main():
    p=argparse.ArgumentParser(); p.add_argument('--config',default='config/local-buddy-model.yaml'); p.add_argument('--device',default='cpu'); p.add_argument('--steps',type=int,default=100); p.add_argument('--grad-accum',type=int,default=8); p.add_argument('--checkpoint-dir',default='artifacts/buddy-checkpoints'); p.add_argument('--seed',type=int,default=42); p.add_argument('--save-every',type=int,default=50)
    p.add_argument('--dataset-adapter',required=True,help='Python module exposing model, train_batches, val_batches, optimizer')
    a=p.parse_args(); seed_all(a.seed)
    mod=__import__(a.dataset_adapter,fromlist=['*'])
    result=run(mod.model,mod.train_batches,mod.val_batches,mod.optimizer,a.device,a.steps,a.grad_accum,a.checkpoint_dir,a.config,a.save_every)
    print(json.dumps(result,indent=2))
if __name__=='__main__': main()
