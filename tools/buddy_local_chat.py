#!/usr/bin/env python3
"""Minimal dependency-light local chat interface.

Uses a compatible local model adapter when installed. The CLI itself does not
ship model weights and therefore never claims a model is available locally.
"""
from __future__ import annotations
import argparse,json

def main():
    p=argparse.ArgumentParser(description='Buddy local chat')
    p.add_argument('--model',default='buddy-local-500m')
    p.add_argument('--json',action='store_true',help='emit structured response envelope')
    p.add_argument('--system',default='You are Buddy, a DreamCo local assistant.')
    a=p.parse_args()
    try:
        from buddy_local_runtime import LocalModel
    except ImportError:
        raise SystemExit('Local runtime adapter not installed. Install the selected local backend before chatting.')
    model=LocalModel.from_config(a.model)
    messages=[{'role':'system','content':a.system}]
    print(f'{a.model} local chat. Type /exit to quit.')
    while True:
        text=input('you> ').strip()
        if text=='/exit': break
        messages.append({'role':'user','content':text})
        answer=model.chat(messages)
        messages.append({'role':'assistant','content':answer})
        if a.json: print(json.dumps({'model':a.model,'role':'assistant','content':answer},ensure_ascii=False))
        else: print('buddy>',answer)

if __name__=='__main__': main()
