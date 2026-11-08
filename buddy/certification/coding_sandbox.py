"""Execute generated Python against hidden tests in a hardened ephemeral Docker container.

Docker isolation is required; no host fallback. Run only on trusted isolated runners.
"""
import json
import subprocess

BOOTSTRAP = """
import json, pathlib, subprocess, sys, tempfile
data=json.load(sys.stdin)
with tempfile.TemporaryDirectory() as d:
    p=pathlib.Path(d)
    (p/'solution.py').write_text(data['code'])
    (p/'test_solution.py').write_text(data['tests'])
    try:
        proc=subprocess.run([sys.executable,'-I','-m','unittest','discover','-s',d,'-p','test_solution.py','-v'],
                            cwd=d,capture_output=True,text=True,timeout=8)
        print(json.dumps({'passed':proc.returncode==0,'exit_code':proc.returncode,
                          'output':(proc.stdout+proc.stderr)[-4000:]}))
    except subprocess.TimeoutExpired:
        print(json.dumps({'passed':False,'error':'test_timeout'}))
"""

def run_python_tests(code, tests, *, image="python:3.11-alpine", timeout=20):
    if not isinstance(code,str) or not isinstance(tests,str):
        raise TypeError("code and tests must be text")
    if len(code)>30000 or len(tests)>30000:
        raise ValueError("test payload exceeds budget")
    if not image.startswith("python:3.11-"):
        raise ValueError("only pinned Python 3.11 image family permitted")
    cmd=["docker","run","--rm","-i","--network","none","--read-only",
         "--cap-drop","ALL","--security-opt","no-new-privileges",
         "--pids-limit","64","--memory","256m","--cpus","1",
         "--user","65534:65534","--tmpfs","/tmp:rw,nosuid,nodev,size=32m",
         image,"python","-I","-c",BOOTSTRAP]
    try:
        proc=subprocess.run(cmd,input=json.dumps({"code":code,"tests":tests}),
                            capture_output=True,text=True,timeout=timeout,check=False)
    except (FileNotFoundError,subprocess.TimeoutExpired) as exc:
        return {"passed":False,"error":type(exc).__name__,"sandbox_executed":False}
    if proc.returncode!=0:
        return {"passed":False,"error":"container_failed","sandbox_executed":False,
                "diagnostic":proc.stderr[-400:]}
    try:
        result=json.loads(proc.stdout.strip())
    except ValueError:
        return {"passed":False,"error":"invalid_sandbox_receipt","sandbox_executed":False}
    return {"passed":result.get("passed") is True,"sandbox_executed":True,
            "exit_code":result.get("exit_code"),"output":result.get("output","")[-4000:]}
