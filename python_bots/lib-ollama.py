"""Ollama Local AI Bot
Division: DreamCodeLab | Tier: pro
Expert in Ollama for running LLMs locally: model management, API integration, and GPU optimization.
Revenue: SaaS subscription | Price: $99/mo
"""
import os
from openai import OpenAI
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
SYSTEM_PROMPT = """You are Ollama Local AI Bot, a DreamCo Empire OS DreamCodeLab AI coding expert specializing in Ollama, llama.cpp, LocalAI, LM Studio, Whisper. Expert in Ollama for running LLMs locally: model management, API integration, and GPU optimization. You write production-quality code, explain concepts clearly, debug with precision, and build complete solutions. You can replicate any feature of any app using your library expertise. Generate working code, suggest best practices, create tool libraries, and mentor developers at any level."""
BOT = {"slug":"lib-ollama","division":"DreamCodeLab","tier":"pro","revenue":"SaaS subscription"}
def run(msg, history=None):
    msgs = [{"role":"system","content":SYSTEM_PROMPT}]
    if history: msgs.extend(history)
    msgs.append({"role":"user","content":msg})
    return client.chat.completions.create(model="gpt-4o-mini",messages=msgs,max_tokens=2000).choices[0].message.content
def make_money(task="Generate revenue opportunities"):
    return run(f"MONEY MODE: {task}")
if __name__=="__main__":
    print(f"🤖 {BOT['display_name'] if 'display_name' in BOT else 'Ollama Local AI Bot'} | {BOT['tier'].upper()}")
    print(run("What can you help me make money with today?"))
