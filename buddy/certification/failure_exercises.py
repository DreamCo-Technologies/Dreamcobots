"""Convert measured task failures into reviewable exercises without exposing holdouts."""
import hashlib

SKILLS={"coding":"Python functions, unit tests, debugging and runtime errors",
        "research":"source provenance, factual verification and quantitative reasoning",
        "multi_step_tools":"tool schemas, prerequisite ordering, state validation and recovery"}
SOURCES={"coding":["Official Python tutorial","Python unittest documentation"],
         "research":["Authorized primary sources","Research methods and evidence grading"],
         "multi_step_tools":["Approved API/tool contracts","Workflow and sandbox documentation"]}

def propose_exercises(comparison):
    if comparison.get("schema")!="dreamco.executable_task_comparison.v1":
        raise ValueError("unexpected comparison schema")
    items=[]
    for row in comparison.get("results",[]):
        if row.get("passed") is not False:
            continue
        domain=row.get("domain")
        if domain not in SKILLS:
            continue
        items.append({"id":hashlib.sha256((row["model"]+":"+row["task_id"]).encode()).hexdigest()[:20],
                      "model":row["model"],"task_id":row["task_id"],"domain":domain,
                      "study_topic":SKILLS[domain],"authorized_source_suggestions":SOURCES[domain],
                      "exercise":"Create a NEW analogous practice task, not a held-out benchmark copy.",
                      "observed_failure_receipt":row.get("output_sha256"),
                      "review_required":True,"training_started":False,
                      "holdout_content_included":False})
    return {"schema":"dreamco.executable_study_proposals.v1","proposals":items,
            "automatic_training":False}
