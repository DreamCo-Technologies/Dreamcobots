"""Fail-closed permission, redaction, fixture and similarity checks."""
import re
from dataclasses import dataclass,field
from typing import Any
SECRET=[re.compile(r"""(?i)(api[_-]?key|access[_-]?token|refresh[_-]?token|client[_-]?secret|password|secret)\s*[:=]\s*['\"]?[^\s,'\";}]+"""),re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")]
PII=[re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",re.I),re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),re.compile(r"(?<!\d)(?:\+?1[ .-]?)?\(?\d{3}\)?[ .-]\d{3}[ .-]\d{4}(?!\d)")]
@dataclass
class PolicyResult:
    allowed:bool
    sanitized_content:str=""
    findings:list[str]=field(default_factory=list)
    reason:str=""
class PolicyGate:
    ALLOWED={"user_owned","public_api","open_source","user_authorized_logs","user_authorized_workflow","user_authorized_schema"}
    def authorize_and_scrub(self,content:str,permission:dict[str,Any])->PolicyResult:
        if permission.get("authorized") is not True:return PolicyResult(False,findings=["permission_missing"],reason="Explicit owner authorization required.")
        if permission.get("target_kind") not in self.ALLOWED:return PolicyResult(False,findings=["target_not_allowed"],reason="Target category is not permitted.")
        if permission.get("bypass_requested") is True or permission.get("behind_login_without_authorization") is True:return PolicyResult(False,findings=["prohibited_access"],reason="Access-control bypass is prohibited.")
        clean=content; findings=[]
        for pattern in SECRET:
            clean,n=pattern.subn("[REDACTED_SECRET]",clean)
            if n:findings.append("secrets_redacted")
        for pattern in PII:
            clean,n=pattern.subn("[REDACTED_PII]",clean)
            if n:findings.append("pii_redacted")
        return PolicyResult(True,clean,sorted(set(findings)),"Authorized; heuristic redaction completed.")
    @staticmethod
    def verify_equivalence(expected,observed):
        if len(expected)!=len(observed):return PolicyResult(False,findings=["fixture_count_mismatch"],reason="Fixture counts differ.")
        mismatches=[i for i,(a,b) in enumerate(zip(expected,observed)) if a!=b]
        if mismatches:return PolicyResult(False,findings=["structural_equivalence_failed"],reason=f"Fixture mismatch indexes: {mismatches}")
        return PolicyResult(True,findings=["fixture_equivalence_passed"],reason="Supplied fixtures match; universal equivalence is not established.")
    @staticmethod
    def similarity_audit(source,generated,max_jaccard=0.25):
        tokens=lambda s:set(re.findall(r"[A-Za-z_][A-Za-z0-9_]*|\d+",s))
        a,b=tokens(source),tokens(generated); score=len(a&b)/max(1,len(a|b))
        if score>max_jaccard:return PolicyResult(False,findings=["similarity_threshold_exceeded"],reason=f"Token Jaccard {score:.3f} exceeds {max_jaccard:.3f}.")
        return PolicyResult(True,findings=["similarity_threshold_passed"],reason=f"Token Jaccard {score:.3f}; legal review remains required.")
