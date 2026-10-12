"""Executable local workbench controls. No provider calls or financial writes."""
from __future__ import annotations
import hashlib,json,math,os,platform,random,shutil,sqlite3,time
from collections import Counter,defaultdict
from pathlib import Path


def number(x,lower=0,upper=float('inf')):
    if type(x) not in (int,float) or not math.isfinite(x) or not lower<=x<=upper:raise ValueError('invalid finite number')
    return x


def token_report(text,encode=None,tokenizer_id='utf8-byte-educational'):
    if not isinstance(text,str):raise ValueError('text required')
    tokens=list(encode(text)) if encode else list(text.encode('utf-8'))
    return {'characters':len(text),'utf8_bytes':len(text.encode()),'tokens':len(tokens),'token_ids':tokens,
            'tokenizer':tokenizer_id,'provider_billable_count':None,'scope':'exact for selected tokenizer only'}


def usage(runtime_ms,input_tokens,output_tokens,input_rate=None,output_rate=None):
    number(runtime_ms)
    for n in (input_tokens,output_tokens):
        if type(n) is not int or n<0:raise ValueError('nonnegative integer token counts required')
    cost=None
    if input_rate is not None and output_rate is not None:cost=(input_tokens*number(input_rate)+output_tokens*number(output_rate))/1_000_000
    return {'runtime_ms':runtime_ms,'input_tokens':input_tokens,'output_tokens':output_tokens,'tokens_per_second':output_tokens/(runtime_ms/1000) if runtime_ms else None,'cost':cost,'cost_source':'user_supplied_rates' if cost is not None else 'unknown'}


def system_check(directory='.'):
    from buddy.workbench.readiness import gpu_inventory
    disk=shutil.disk_usage(directory)
    try:ram=os.sysconf('SC_PAGE_SIZE')*os.sysconf('SC_PHYS_PAGES')
    except (ValueError,OSError,AttributeError):ram=None
    return {'platform':platform.platform(),'cpu_count':os.cpu_count(),'ram_bytes':ram,'disk_free_bytes':disk.free,
            'gpu':gpu_inventory(),'large_model_training':'requires_model_specific_memory_probe',
            'local_educational_training':True,'production_capacity':'unverified'}


def compare_attempts(uncertainty,cost_per_attempt,budget,max_attempts=8):
    number(uncertainty,0,1);number(cost_per_attempt);number(budget)
    if type(max_attempts) is not int or not 1<=max_attempts<=100:raise ValueError('attempt limit 1..100')
    desired=min(max_attempts,max(1,math.ceil(uncertainty*max_attempts)))
    affordable=max_attempts if cost_per_attempt==0 else math.floor(budget/cost_per_attempt)
    return {'attempts':min(desired,affordable),'reason':'bounded uncertainty heuristic; validate experimentally'}


def reward(scores,weights,required,allow_partial=False):
    if type(allow_partial) is not bool:raise ValueError('strict partial-score choice required')
    if not weights or any(k not in scores for k in weights):raise ValueError('reward rubric incomplete')
    for w in weights.values():number(w,0,1)
    if abs(sum(weights.values())-1)>1e-9:raise ValueError('weights must sum to one')
    for s in scores.values():number(s,0,1)
    if any(scores.get(k)!=1 for k in required):return {'reward':0.0,'accepted':False,'reason':'required check failed'}
    total=sum(scores[k]*w for k,w in weights.items())
    return {'reward':total if allow_partial or total==1 else 0.0,'accepted':total==1,'reason':'rubric evaluation; no weight update authorized'}


class Workspace:
    """Private tenant-scoped storage. Caller identity must be authenticated upstream."""
    def __init__(self,path):
        self.db=sqlite3.connect(path)
        self.db.execute('CREATE TABLE IF NOT EXISTS records(tenant TEXT,kind TEXT,id TEXT,body TEXT,PRIMARY KEY(tenant,kind,id))')
    def save(self,tenant,kind,id,body,consent=False):
        if not tenant or kind not in ('chat','dashboard','experiment'):raise ValueError('identity and known kind required')
        if kind=='chat' and consent is not True:raise ValueError('explicit chat storage consent required')
        if kind=='dashboard':
            allowed={'usage','experiments','models','system','rewards','memory'}
            if not isinstance(body,dict) or not isinstance(body.get('widgets'),list) or any(x not in allowed for x in body['widgets']):raise ValueError('unknown dashboard widget')
        data=json.dumps(body,allow_nan=False)
        self.db.execute('INSERT INTO records VALUES(?,?,?,?) ON CONFLICT(tenant,kind,id) DO UPDATE SET body=excluded.body',(tenant,kind,id,data));self.db.commit()
    def list(self,tenant,kind):return [{'id':r[0],'body':json.loads(r[1])} for r in self.db.execute('SELECT id,body FROM records WHERE tenant=? AND kind=? ORDER BY id',(tenant,kind))]
    def forget(self,tenant,id):
        self.db.execute("DELETE FROM records WHERE tenant=? AND kind='chat' AND id=?",(tenant,id));self.db.commit()
    def memory_context(self,tenant,ids):
        chosen=set(ids)
        return [r for r in self.list(tenant,'chat') if r['id'] in chosen]


class ByteModel:
    """Small educational autoregressive transition model, not a neural LLM.

    Trains actual parameters locally and generates bytes using a seeded sampler.
    Training rights and maximum corpus size are enforced before updates.
    """
    def __init__(self):self.counts=defaultdict(Counter)
    def train(self,text,training_allowed=False,license=None,max_bytes=1_000_000):
        if training_allowed is not True or not license:raise ValueError('explicit data rights required')
        data=text.encode('utf-8')
        if len(data)<2 or len(data)>max_bytes:raise ValueError('corpus size outside allowed bounds')
        for a,b in zip(data,data[1:]):self.counts[a][b]+=1
        return {'model_type':'educational_byte_transition','vocabulary_size':256,'transitions':len(data)-1,'corpus_sha256':hashlib.sha256(data).hexdigest(),'production_ready':False}
    def generate(self,prompt,length=64,temperature=1.0,seed=0):
        number(temperature,0,2)
        if type(length) is not int or not 1<=length<=4096 or not prompt:raise ValueError('bounded generation length and prompt required')
        rng=random.Random(seed);result=bytearray(prompt.encode())
        for _ in range(length):
            counts=self.counts.get(result[-1])
            if not counts:break
            values=sorted(counts)
            if temperature==0:next_byte=max(values,key=lambda v:counts[v])
            else:
                logits=[math.log(counts[v])/temperature for v in values];peak=max(logits)
                next_byte=rng.choices(values,[math.exp(x-peak) for x in logits])[0]
            result.append(next_byte)
        return {'text':result.decode('utf-8',errors='replace'),'generated_bytes':len(result)-len(prompt.encode()),'seed':seed,'temperature':temperature}
    def save(self,path):Path(path).write_text(json.dumps({str(k):dict(v) for k,v in self.counts.items()},sort_keys=True))


def microsite(region,title,body):
    """Render user-provided regional content; no invented local claims."""
    import html
    if not all(isinstance(x,str) and x.strip() for x in (region,title,body)):raise ValueError('region, title and content required')
    return '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>'+html.escape(title)+'</title><main><h1>'+html.escape(title)+'</h1><p>Region: '+html.escape(region)+'</p><article>'+html.escape(body)+'</article></main></html>'


class BytePairTokenizer:
    """Small deterministic BPE teaching implementation, not a provider tokenizer."""
    def __init__(self):self.merges=[]
    def train(self,text,vocab_size=150001):
        if type(vocab_size) is not int or not 256<=vocab_size<=200000:raise ValueError('vocabulary target 256..200000 required')
        raw=text.encode()
        if not 2<=len(raw)<=20000:raise ValueError('educational corpus must be 2..20000 bytes')
        tokens=[bytes([b]) for b in raw];self.merges=[]
        while len(self.merges)+256<vocab_size:
            counts=Counter(zip(tokens,tokens[1:]))
            if not counts:break
            pair=max(counts,key=lambda p:(counts[p],p))
            if counts[pair]<2:break
            self.merges.append(pair);tokens=self._merge(tokens,pair)
        return {'vocabulary_target':vocab_size,'learned_vocabulary':256+len(self.merges),'target_reached':256+len(self.merges)>=vocab_size,'training_bytes':len(raw),'encoded_tokens':len(tokens)}
    @staticmethod
    def _merge(tokens,pair):
        out=[];i=0
        while i<len(tokens):
            if i+1<len(tokens) and (tokens[i],tokens[i+1])==pair:out.append(tokens[i]+tokens[i+1]);i+=2
            else:out.append(tokens[i]);i+=1
        return out
    def encode(self,text):
        tokens=[bytes([b]) for b in text.encode()]
        for pair in self.merges:tokens=self._merge(tokens,pair)
        return tokens
    def inspect(self,text):
        tokens=self.encode(text)
        return {'tokens':len(tokens),'pieces':[{'utf8_preview':t.decode('utf8',errors='replace'),'hex':t.hex(),'bytes':len(t)} for t in tokens],'exact_reconstruction':b''.join(tokens).decode()==text}
