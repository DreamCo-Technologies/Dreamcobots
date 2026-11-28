"""Read-only deterministic adapter for an owner-provisioned O*NET SQLite catalog."""
import sqlite3,re
def match_onet_tasks(description,database_path,limit=5):
    if not description.strip():
        return [{"task_family":"software_requirements_analysis","onet_soc_code":None,"actor":"AI_assisted_human_review","human_required":True,"confidence":"low","review_note":"Provide an owner-authored task description for O*NET matching."}]
    connection=sqlite3.connect(f"file:{database_path}?mode=ro",uri=True)
    try:
        columns={row[1] for row in connection.execute("PRAGMA table_info(onet_tasks)")}
        required={"soc_code","task_id","task"}
        if not required.issubset(columns): raise ValueError("O*NET database must expose onet_tasks(soc_code, task_id, task).")
        words=set(re.findall(r"[a-z0-9]{3,}",description.lower()))
        rows=connection.execute("SELECT soc_code,task_id,task FROM onet_tasks ORDER BY soc_code,task_id").fetchall()
        ranked=[]
        for soc,task_id,task in rows:
            task_words=set(re.findall(r"[a-z0-9]{3,}",str(task).lower()))
            score=len(words&task_words)/max(1,len(words|task_words))
            if score>0: ranked.append((score,soc,task_id))
        ranked.sort(key=lambda item:(-item[0],item[1],item[2]))
        return [{"task_family":"onet_task_match","onet_soc_code":soc,"source_onet_id":task_id,"actor":"AI_assisted_human_review","human_required":True,"confidence":"medium" if score>=0.2 else "low","match_score":round(score,4)} for score,soc,task_id in ranked[:limit]]
    finally:
        connection.close()
