import argparse,subprocess,tempfile,pathlib,shutil,re,sys,uuid
from ..common import read_json,write_json,validate

def similarity(a,b):
    tokens=lambda value:set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+",value))
    left,right=tokens(a),tokens(b)
    return len(left&right)/max(1,len(left|right))

def docker_command(root,image="dreamco-verifier:local",name="dreamco-verifier-test"):
    return ["docker","run","--name",name,"--network","none","--read-only","--cap-drop=ALL","--security-opt=no-new-privileges","--pids-limit","64","--memory","256m","--memory-swap","256m","--cpus","0.5","--user","65532:65532","--tmpfs","/tmp:rw,noexec,nosuid,size=32m,mode=1777","-v",f"{root}:/work:ro","-w","/tmp",image,"sh","-lc","cp -R /work /tmp/work && cd /tmp/work && python -m pytest -q"]

def main():
    p=argparse.ArgumentParser(description="DreamCo Stage 5 rootless Docker verifier")
    p.add_argument("--input",required=True); p.add_argument("--output",required=True)
    p.add_argument("--reference",help="Owner-authorized source reference used only for similarity triage")
    p.add_argument("--threshold",type=float,default=.25); p.add_argument("--timeout",type=int,default=10)
    p.add_argument("--image",default="dreamco-verifier:local"); args=p.parse_args()
    if not 1<=args.timeout<=10 or not 0<args.threshold<=1: raise ValueError("Timeout must be 1..10 seconds and threshold must be in (0,1].")
    module=read_json(args.input); validate(module,"course_module.schema.json")
    files=module["reference_implementation"]["files"]+module["tests"]
    if len(files)>100 or sum(len(item.get("content","").encode("utf-8")) for item in files)>5*1024*1024:
        raise ValueError("Generated artifact exceeds sandbox file or size limits.")
    report={"schema_version":"dreamco.eval_report.v1","job_id":module["job_id"],"status":"BLOCKED","tests_passed":False,"similarity_score":1.0,"policy_check":"FAIL","sandbox":{"network_disabled":True,"rootless_requested":True,"timed_out":False,"exit_code":None}}
    if not args.reference:
        report["sandbox"]["error"]="authorized_similarity_reference_required"
    else:
        reference=pathlib.Path(args.reference).read_text(encoding="utf-8")
        generated="\n".join(item["content"] for item in module["reference_implementation"]["files"])
        report["similarity_score"]=similarity(reference,generated)
        report["policy_check"]="PASS" if report["similarity_score"]<args.threshold else "FAIL"
    if report["policy_check"]=="PASS":
        if not shutil.which("docker"):
            report["sandbox"]["error"]="docker_unavailable"
        else:
            info=subprocess.run(["docker","info","--format","{{json .SecurityOptions}}"],capture_output=True,text=True,timeout=5)
            if info.returncode!=0 or "rootless" not in info.stdout.lower():
                report["sandbox"]["error"]="rootless_docker_required"
            else:
                with tempfile.TemporaryDirectory(prefix="dreamco-verify-") as td:
                    root=pathlib.Path(td).resolve()
                    for item in files:
                        dest=(root/item["path"]).resolve()
                        if root not in dest.parents: raise ValueError("Unsafe generated path.")
                        dest.parent.mkdir(parents=True,exist_ok=True)
                        dest.write_text(item["content"],encoding="utf-8")
                    container_name="dreamco-verify-"+uuid.uuid4().hex[:16]
                    try:
                        proc=subprocess.run(docker_command(root,args.image,container_name),capture_output=True,text=True,timeout=args.timeout)
                        report["sandbox"]["exit_code"]=proc.returncode
                        report["tests_passed"]=proc.returncode==0
                        report["status"]="PASS" if proc.returncode==0 else "FAIL"
                        report["sandbox"]["stdout_tail"]=proc.stdout[-2000:]
                        report["sandbox"]["stderr_tail"]=proc.stderr[-2000:]
                    except subprocess.TimeoutExpired:
                        report["sandbox"]["timed_out"]=True; report["status"]="FAIL"
                        subprocess.run(["docker","kill",container_name],capture_output=True,text=True,timeout=3)
                    finally:
                        subprocess.run(["docker","rm","-f",container_name],capture_output=True,text=True,timeout=3)
    if report["tests_passed"] and report["policy_check"]=="PASS": report["status"]="PASS"
    validate(report,"eval_report.schema.json"); write_json(args.output,report)
    if report["status"]!="PASS": sys.exit(2)

if __name__=="__main__": main()
