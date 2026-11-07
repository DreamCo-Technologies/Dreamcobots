"""Day-1 pinned SST-2 eval (PR #14396). Usage: python run_sst2_pin.py <run_id>"""
import sys, os, json, hashlib, platform, subprocess, datetime, random
from zoneinfo import ZoneInfo
MODEL="distilbert/distilbert-base-uncased-finetuned-sst-2-english"; MREV="714eb0fa89d2f80546fda750413ed43d93601a13"
DS="stanfordnlp/sst2"; DREV="8d51e7e4887a4caaa95b3fbebbf53c0490b58bbb"; SPLIT="validation"; SEED=0
run_id=sys.argv[1]
root=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
outdir=os.path.join(root,"evidence","sst2",run_id); os.makedirs(outdir,exist_ok=True)
CT=ZoneInfo("America/Chicago"); start=datetime.datetime.now(CT)
import torch, transformers, datasets, huggingface_hub
from transformers import pipeline
random.seed(SEED); torch.manual_seed(SEED); torch.use_deterministic_algorithms(True)
ds=datasets.load_dataset(DS,revision=DREV,split=SPLIT)
clf=pipeline("text-classification",model=MODEL,revision=MREV,device=-1)
texts=list(ds["sentence"]); gold=list(ds["label"])
outs=clf(texts,batch_size=32,truncation=True)
l2i={"NEGATIVE":0,"POSITIVE":1}
preds=[]; 
for r,t,o in zip(ds,texts,outs):
    preds.append({"idx":int(r["idx"]),"text_sha256":hashlib.sha256(t.encode()).hexdigest(),"pred_label":l2i[o["label"]],"pred_label_name":o["label"],"score":float(o["score"])})
with open(os.path.join(outdir,"predictions.jsonl"),"w") as f:
    for p in preds: f.write(json.dumps(p)+"\n")
with open(os.path.join(outdir,"gold_labels.jsonl"),"w") as f:
    for r,t in zip(ds,texts): f.write(json.dumps({"idx":int(r["idx"]),"text_sha256":hashlib.sha256(t.encode()).hexdigest(),"gold_label":int(r["label"])})+"\n")
# metrics recomputed from the written files
P={json.loads(l)["idx"]:json.loads(l)["pred_label"] for l in open(os.path.join(outdir,"predictions.jsonl"))}
G={json.loads(l)["idx"]:json.loads(l)["gold_label"] for l in open(os.path.join(outdir,"gold_labels.jsonl"))}
n=len(G); tp=sum(1 for i in G if G[i]==1 and P[i]==1); tn=sum(1 for i in G if G[i]==0 and P[i]==0)
fp=sum(1 for i in G if G[i]==0 and P[i]==1); fn=sum(1 for i in G if G[i]==1 and P[i]==0)
prec=tp/(tp+fp) if tp+fp else 0; rec=tp/(tp+fn) if tp+fn else 0
metrics={"n":n,"correct":tp+tn,"accuracy":(tp+tn)/n,"tp":tp,"tn":tn,"fp":fp,"fn":fn,"precision_pos":prec,"recall_pos":rec,"f1_pos":2*prec*rec/(prec+rec) if prec+rec else 0,"computed_from":["predictions.jsonl","gold_labels.jsonl"]}
json.dump(metrics,open(os.path.join(outdir,"metrics.json"),"w"),indent=2)
cpu=next((l.split(":",1)[1].strip() for l in open("/proc/cpuinfo") if l.startswith("model name")),platform.processor())
env={"python":platform.python_version(),"torch":torch.__version__,"transformers":transformers.__version__,"datasets":datasets.__version__,"huggingface_hub":huggingface_hub.__version__,"platform":platform.platform(),"cpu":cpu,"cpu_count":os.cpu_count(),"torch_threads":torch.get_num_threads(),"device":"cpu","seed":SEED,"deterministic_algorithms":True,"batch_size":32,"truncation":True}
json.dump(env,open(os.path.join(outdir,"env.json"),"w"),indent=2)
git=subprocess.run(["git","rev-parse","HEAD"],cwd=root,capture_output=True,text=True).stdout.strip()
end=datetime.datetime.now(CT)
ev={"schema":"dreamco.hf_eval_evidence.v1","run_id":run_id,"pin_source":"PR #14396 reports/HF_TOMORROW_SWARM_STATUS.md","model_id":MODEL,"model_revision":MREV,"dataset_id":DS,"dataset_revision":DREV,"split":SPLIT,"dataset_use":"eval-only (license unknown)","command":"python study_packs/nlp-tasks/classification/tools/run_sst2_pin.py "+run_id,"started_ct":start.isoformat(),"finished_ct":end.isoformat(),"git_sha":git,"env":env,"metrics":metrics,"pass_floor":{"accuracy_min":0.85,"meets_floor":metrics["accuracy"]>=0.85},"artifacts":{k:f"study_packs/nlp-tasks/classification/evidence/sst2/{run_id}/{k}" for k in ["predictions.jsonl","gold_labels.jsonl","metrics.json","env.json","run.log"]},"claimable":False,"production_ready":False,"mastered":False}
json.dump(ev,open(os.path.join(root,"evidence",f"run_{run_id}.json"),"w"),indent=2)
print(json.dumps(metrics))
