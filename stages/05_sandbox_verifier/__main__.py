import argparse,subprocess,tempfile,pathlib,shutil,hashlib,re,sys,json
from ..common import read_json,write_json,validate
def similarity(a,b):
    toks=lambda s:set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+",s))
    x,y=toks(a),toks(b); return len(x&y)/max(1,len(x|y))
def main():
    p=argparse.ArgumentParser(description="DreamCo Stage 5 rootless Docker verifier"); p.add_argument("--input",required=True); p.add_argument("--output",required=True); p.add_argument("--reference",help="Optional independently authorized reference text for similarity triage"); p.add_argument("--threshold",type=float,default=.25); p.add_argument("--timeout",type=int,default=10); a=p.parse_args()
    mod=read_json(a.input); files=mod["reference_implementation"]["files"]+mod["tests"]
    report={"schema_version":"dreamco.eval_report.v1","job_id":mod["job_id"],"status":"BLOCKED","tests_passed":False,"similarity_score":0.0,"policy_check":"PASS","sandbox":{"network_disabled":True,"rootless_requested":True,"timed_out":False,"exit_code":None}}
    if a.reference:
        ref=pathlib.Path(a.reference).read_text(); generated="\n".join(x["content"] for x in mod["reference_implementation"]["files"]); report["similarity_score"]=similarity(ref,generated)
        if report["similarity_score"]>=a.threshold: report["policy_check"]="FAIL"
    if report["policy_check"]=="PASS":
        if not shutil.which("docker"): report["sandbox"]["error"]="docker_unavailable"
        else:
            with tempfile.TemporaryDirectory(prefix="dreamco-verify-") as td:
                root=pathlib.Path(td)
                for f in files:
                    dest=(root/f["path"]).resolve()
                    if root.resolve() not in dest.parents: raise ValueError("Unsafe generated path.")
                    dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(f["content"],encoding="utf-8")
                cmd=["docker","run","--rm","--network","none","--read-only","--cap-drop","ALL","--security-opt","no-new-privileges","--pids-limit","64","--memory","256m","--cpus","0.5","--userns=host","--user",f"{__import__('os').getuid()}:{__import__('os').getgid()}","--tmpfs","/tmp:rw,noexec,nosuid,size=32m","-v",f"{root}:/work:ro","-w","/tmp","python:3.11-alpine","sh","-lc","cp -R /work /tmp/work && cd /tmp/work && python -m pip install --no-cache-dir pytest >/dev/null 2>&1 && python -m pytest -q"]
                try:
                    proc=subprocess.run(cmd,capture_output=True,text=True,timeout=a.timeout)
                    report["sandbox"]["exit_code"]=proc.returncode; report["tests_passed"]=proc.returncode==0; report["status"]="PASS" if proc.returncode==0 else "FAIL"
                    report["sandbox"]["stdout_tail"]=proc.stdout[-2000:]; report["sandbox"]["stderr_tail"]=proc.stderr[-2000:]
                except subprocess.TimeoutExpired: report["sandbox"]["timed_out"]=True; report["status"]="FAIL"
    if report["tests_passed"] and report["policy_check"]=="PASS": report["status"]="PASS"
    validate(report,"eval_report.schema.json"); write_json(a.output,report)
    if report["status"]!="PASS": sys.exit(2)
if __name__=="__main__":main()
