"""Reproducible task evaluation: real code tests, evidence checks, stateful tool actions.

No external model calls unless the caller supplies an approved adapter.
"""
import hashlib
import json
import re
import time
from .coding_sandbox import run_python_tests
from .research_evidence import verify_research_answer
from .tool_execution_bench import execute

def evaluate(task, adapter):
    start=time.monotonic()
    prompt=task["prompt"]
    output=adapter.complete(prompt)
    elapsed=time.monotonic()-start
    if not isinstance(output,str):
        raise TypeError("model output must be text")
    kind=task["kind"]
    if kind=="coding_python":
        code=output.strip()
        if code.startswith("```") and code.endswith("```"):
            code="\n".join(code.splitlines()[1:-1])
        receipt=run_python_tests(code,task["hidden_tests"])
        passed=receipt["passed"] and receipt["sandbox_executed"]
    elif kind=="research":
        # Independently authored expected answer; citation validity needs separate source checks.
        if task.get("sources"):
            receipt=verify_research_answer(output,task)
            passed=receipt["passed"]
        else:
            passed=output.strip().casefold()==task["expected"].strip().casefold()
            receipt={"passed":passed,"scorer":"exact_match","source_verified":False}
    elif kind=="multi_step_tools":
        try:
            actions=json.loads(output)
            if not isinstance(actions,list) or not all(isinstance(a,str) for a in actions):
                raise ValueError("expected action list")
            receipt=execute(actions,inventory=task["inventory"],reserved=task["reserved"])
            passed=(receipt["sandbox_executed"] and receipt["state"]["available"]==
                    task["inventory"]-task["reserved"] and receipt["state"]["published"])
        except (ValueError,TypeError,KeyError):
            passed=False
            receipt={"passed":False,"error":"invalid_tool_plan"}
    else:
        raise ValueError("unknown benchmark kind")
    return {"task_id":task["id"],"domain":task["domain"],"model":adapter.name,
            "passed":bool(passed),"elapsed_seconds":round(elapsed,4),
            "output_sha256":hashlib.sha256(output.encode()).hexdigest(),
            "receipt":receipt,"independent_verified":False,
            "note":"Automated local scoring only; independent verification requires external review."}

def compare(tasks, adapters):
    if not tasks or not adapters:
        raise ValueError("tasks and adapters required")
    return {"schema":"dreamco.executable_task_comparison.v1",
            "task_set_hash":hashlib.sha256(json.dumps(tasks,sort_keys=True).encode()).hexdigest(),
            "results":[evaluate(task,adapter) for task in tasks for adapter in adapters],
            "champions_certified":False}
