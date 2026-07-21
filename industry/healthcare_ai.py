"""
Healthcare AI module for Dreamcobots platform.

Provides AI-powered tools for patient data analysis, symptom triage,
appointment management, medication tracking, and medical report generation.
"""

import uuid
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional

from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Patient:
    """Simplified patient record."""
    patient_id: str
    name: str
    date_of_birth: date
    conditions: List[str] = field(default_factory=list)
    medications: List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class TriageResult:
    """Result of an automated symptom triage assessment."""
    patient_id: str
    symptoms: List[str]
    urgency: str          # 'low', 'moderate', 'high', 'emergency'
    recommendation: str
    confidence: float     # 0.0 – 1.0
    triage_id: str = field(default_factory=lambda: str(uuid.uuid4()))


# High-priority symptoms that warrant immediate escalation
_EMERGENCY_SYMPTOMS = {
    "chest pain", "difficulty breathing", "stroke", "unconscious",
    "severe bleeding", "anaphylaxis", "cardiac arrest",
}

_HIGH_SYMPTOMS = {
    "high fever", "severe headache", "confusion", "abdominal pain",
    "vomiting blood", "severe allergic reaction",
}


# ---------------------------------------------------------------------------
# HealthcareAI bot
# ---------------------------------------------------------------------------

class HealthcareAI(BotBase):
    """
    AI-powered healthcare assistant bot.

    Manages patient records, performs symptom triage, tracks medications,
    schedules appointments, and generates analytics reports.

    Args:
        autonomy: Autonomy level (default SEMI_AUTONOMOUS for clinical safety).
        scaling: Scaling level.
    """

    def __init__(
        self,
        autonomy: AutonomyLevel = AutonomyLevel.SEMI_AUTONOMOUS,
        scaling: ScalingLevel = ScalingLevel.MODERATE,
    ) -> None:
        super().__init__("HealthcareAI", autonomy, scaling)
        self._patients: Dict[str, Patient] = {}
        self._appointments: List[Dict[str, Any]] = []
        self._triage_log: List[TriageResult] = []

    # ------------------------------------------------------------------
    # Patient management
    # ------------------------------------------------------------------

    def add_patient(self, patient: Patient) -> Patient:
        """Register a patient record."""
        self._patients[patient.patient_id] = patient
        return patient

    def get_patient(self, patient_id: str) -> Optional[Patient]:
        """Return a patient record or None."""
        return self._patients.get(patient_id)

    def update_patient(self, patient_id: str, **kwargs: Any) -> Optional[Patient]:
        """Update mutable fields on a patient record."""
        patient = self._patients.get(patient_id)
        if not patient:
            return None
        for key, value in kwargs.items():
            if hasattr(patient, key):
                setattr(patient, key, value)
        return patient

    def list_patients(self) -> List[Patient]:
        """Return all registered patients."""
        return list(self._patients.values())

    # ------------------------------------------------------------------
    # Symptom triage
    # ------------------------------------------------------------------

    def triage(self, patient_id: str, symptoms: List[str]) -> TriageResult:
        """
        Perform an automated triage assessment.

        Maps reported symptoms to an urgency level and provides a
        recommended action.

        Args:
            patient_id: Patient being triaged.
            symptoms: List of symptom descriptions.

        Returns:
            TriageResult with urgency and recommendation.
        """
        lower_symptoms = {s.lower() for s in symptoms}

        if lower_symptoms & _EMERGENCY_SYMPTOMS:
            urgency = "emergency"
            recommendation = "Call emergency services (911) immediately."
            confidence = 0.95
        elif lower_symptoms & _HIGH_SYMPTOMS:
            urgency = "high"
            recommendation = "Seek urgent care within the next few hours."
            confidence = 0.85
        elif symptoms:
            urgency = "moderate"
            recommendation = "Schedule a same-day or next-day appointment."
            confidence = 0.70
        else:
            urgency = "low"
            recommendation = "Monitor symptoms; book a routine appointment if persistent."
            confidence = 0.60

        result = TriageResult(
            patient_id=patient_id,
            symptoms=symptoms,
            urgency=urgency,
            recommendation=recommendation,
            confidence=confidence,
        )
        self._triage_log.append(result)
        return result

    def get_triage_log(self) -> List[TriageResult]:
        """Return all triage records."""
        return list(self._triage_log)

    # ------------------------------------------------------------------
    # Appointments
    # ------------------------------------------------------------------

    def schedule_appointment(
        self,
        patient_id: str,
        appointment_date: date,
        provider: str,
        reason: str,
    ) -> Dict[str, Any]:
        """Schedule an appointment for a patient."""
        appt = {
            "appointment_id": str(uuid.uuid4()),
            "patient_id": patient_id,
            "date": appointment_date.isoformat(),
            "provider": provider,
            "reason": reason,
            "status": "scheduled",
        }
        self._appointments.append(appt)
        return appt

    def get_appointments(self, patient_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return all (or patient-filtered) appointments."""
        if patient_id:
            return [a for a in self._appointments if a["patient_id"] == patient_id]
        return list(self._appointments)

    # ------------------------------------------------------------------
    # Analytics / reporting
    # ------------------------------------------------------------------

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate a summary analytics report for the healthcare practice.

        Returns:
            Dict with patient count, triage breakdown, and appointment stats.
        """
        urgency_counts: Dict[str, int] = {"emergency": 0, "high": 0, "moderate": 0, "low": 0}
        for t in self._triage_log:
            urgency_counts[t.urgency] = urgency_counts.get(t.urgency, 0) + 1

        return {
            "total_patients": len(self._patients),
            "total_appointments": len(self._appointments),
            "triage_summary": urgency_counts,
            "total_triage_assessments": len(self._triage_log),
        }

    # ------------------------------------------------------------------
    # Task runner
    # ------------------------------------------------------------------

    def _run_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        task_type = task.get("type", "")
        if task_type == "triage":
            result = self.triage(task.get("patient_id", ""), task.get("symptoms", []))
            return {"status": "ok", "triage_id": result.triage_id, "urgency": result.urgency}
        if task_type == "schedule_appointment":
            appt = self.schedule_appointment(
                task.get("patient_id", ""),
                date.fromisoformat(task.get("date", date.today().isoformat())),
                task.get("provider", ""),
                task.get("reason", ""),
            )
            return {"status": "ok", "appointment_id": appt["appointment_id"]}
        return super()._run_task(task)
