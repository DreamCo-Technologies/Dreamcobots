"""Deterministic SQLite learner evidence and teach-back verification."""
from __future__ import annotations
import json, sqlite3, time
from pathlib import Path
STATES=("NOT_STARTED","IN_PROGRESS","LAB_PASSED","TEACH_BACK_VERIFIED")
class LearningEngine:
    def __init__(self,path: str|Path):
        self.db=sqlite3.connect(str(path))
        self.db.execute("""CREATE TABLE IF NOT EXISTS learner_progress(
        learner_id TEXT NOT NULL, guide_id TEXT NOT NULL, state TEXT NOT NULL,
        lab_score REAL, teach_back_score REAL, evidence_json TEXT NOT NULL,
        updated_at INTEGER NOT NULL, PRIMARY KEY(learner_id,guide_id))""")
        self.db.commit()
    def record_lab(self,learner_id:str,guide_id:str,score:float,evidence:dict)->str:
        if not 0<=score<=1: raise ValueError("score must be between 0 and 1")
        state="LAB_PASSED" if score>=0.8 and evidence.get("sandbox_run_id") else "IN_PROGRESS"
        self._save(learner_id,guide_id,state,score,None,evidence); return state
    def record_teach_back(self,learner_id:str,guide_id:str,score:float,evidence:dict)->str:
        if not 0<=score<=1: raise ValueError("score must be between 0 and 1")
        row=self.db.execute("SELECT state,lab_score,evidence_json FROM learner_progress WHERE learner_id=? AND guide_id=?",(learner_id,guide_id)).fetchone()
        if not row or row[0]!="LAB_PASSED" or row[1] is None: raise ValueError("a passed sandbox lab is required before teach-back")
        if not evidence.get("reviewer") or not evidence.get("unseen_question_id"): raise ValueError("teach-back requires reviewer and unseen question evidence")
        state="TEACH_BACK_VERIFIED" if score>=0.8 else "LAB_PASSED"
        merged=json.loads(row[2]); merged["teach_back"]=evidence
        self._save(learner_id,guide_id,state,row[1],score,merged); return state
    def _save(self,l,g,s,lab,tb,e):
        self.db.execute("INSERT INTO learner_progress VALUES(?,?,?,?,?,?,?) ON CONFLICT(learner_id,guide_id) DO UPDATE SET state=excluded.state,lab_score=excluded.lab_score,teach_back_score=excluded.teach_back_score,evidence_json=excluded.evidence_json,updated_at=excluded.updated_at",(l,g,s,lab,tb,json.dumps(e,sort_keys=True),int(time.time())))
        self.db.commit()
    def close(self): self.db.close()
