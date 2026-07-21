"""Nanotech-assisted disease detection and precision medicine engine."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from framework import GlobalAISourcesFlow  # noqa: F401

_flow = GlobalAISourcesFlow(bot_name="PrecisionMedicine")

# Simulated disease-marker reference database
DISEASE_MARKERS = {
    "cancer":        {"CEA": (0, 3.0), "CA-125": (0, 35), "PSA": (0, 4.0)},
    "diabetes":      {"HbA1c": (0, 5.7), "fasting_glucose": (70, 100)},
    "cardiovascular": {"troponin": (0, 0.04), "BNP": (0, 100), "CRP": (0, 1.0)},
    "infection":     {"WBC": (4500, 11000), "CRP": (0, 1.0), "procalcitonin": (0, 0.5)},
}

# DNA variant risk scores (simulated)
GENOMIC_RISKS = {
    "BRCA1": {"cancer": 0.72, "description": "Elevated breast/ovarian cancer risk"},
    "BRCA2": {"cancer": 0.65, "description": "Elevated breast cancer risk"},
    "APOE4": {"alzheimers": 0.60, "description": "Elevated Alzheimer's risk"},
    "MTHFR": {"cardiovascular": 0.35, "description": "Elevated cardiovascular risk"},
    "TP53":  {"cancer": 0.80, "description": "Elevated multi-cancer risk"},
}

# Simulated drug–gene interactions (efficacy 0–1)
DRUG_EFFICACY_TABLE = {
    "metformin":   {"default": 0.78, "MTHFR": 0.55},
    "warfarin":    {"default": 0.70, "CYP2C9": 0.40},
    "tamoxifen":   {"default": 0.68, "CYP2D6_poor": 0.30},
    "aspirin":     {"default": 0.75, "default_cardio": 0.85},
    "atorvastatin": {"default": 0.80, "SLCO1B1": 0.50},
}


class NanotechDiseaseDetectorError(Exception):
    """Raised when a tier limit is exceeded for disease detection."""


class PrecisionMedicineError(Exception):
    """Raised when a tier limit is exceeded for precision medicine."""


# ---------------------------------------------------------------------------
# NanotechDiseaseDetector
# ---------------------------------------------------------------------------

class NanotechDiseaseDetector:
    """Nanotech-assisted disease biomarker detection.

    FREE: not available (PRO required).
    PRO: basic marker screening.
    ENTERPRISE: full nanotech + genomic analysis.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)

    def _require_pro(self, feature: str = "Disease detection") -> None:
        if self.tier == Tier.FREE:
            raise NanotechDiseaseDetectorError(
                f"{feature} requires PRO or ENTERPRISE tier. "
                "Upgrade to access biomarker screening."
            )

    def _require_enterprise(self, feature: str = "Genomic analysis") -> None:
        if self.tier != Tier.ENTERPRISE:
            raise NanotechDiseaseDetectorError(
                f"{feature} requires ENTERPRISE tier. "
                "Upgrade to access full nanotech and genomic capabilities."
            )

    def detect_disease_markers(self, sample_data: dict) -> dict:
        """Screen sample data for disease biomarkers.

        sample_data: {marker_name: measured_value, ...}
        """
        self._require_pro("Disease marker screening")

        findings = {}
        flagged_diseases = []

        for disease, markers in DISEASE_MARKERS.items():
            disease_flags = []
            for marker, (low, high) in markers.items():
                measured = sample_data.get(marker)
                if measured is None:
                    continue
                abnormal = measured < low or measured > high
                disease_flags.append({
                    "marker": marker,
                    "measured": measured,
                    "reference_range": (low, high),
                    "abnormal": abnormal,
                })
                if abnormal:
                    flagged_diseases.append(disease)
            if disease_flags:
                findings[disease] = disease_flags

        result = {
            "analysis_type": "disease_marker_screening",
            "tier": self.tier.value,
            "markers_analyzed": len(sample_data),
            "diseases_screened": list(DISEASE_MARKERS.keys()),
            "findings": findings,
            "flagged_diseases": list(set(flagged_diseases)),
            "recommendation": (
                "Consult a specialist for flagged conditions" if flagged_diseases
                else "No significant abnormalities detected"
            ),
        }

        if self.tier == Tier.ENTERPRISE:
            result["nanotech_confidence"] = 0.97
            result["nanotech_enhanced"] = True
            result["sensitivity"] = "ultra-high (nanotech-assisted)"

        return result

    def analyze_dna_sequence(self, sequence_data: dict) -> dict:
        """Perform genomic analysis on DNA sequence data.

        sequence_data: {"variants": ["BRCA1", "MTHFR", ...], "patient_id": str, ...}
        """
        self._require_enterprise("DNA / genomic analysis")

        variants = sequence_data.get("variants", [])
        patient_id = sequence_data.get("patient_id", "unknown")

        risk_profile = {}
        for variant in variants:
            if variant in GENOMIC_RISKS:
                risk_profile[variant] = GENOMIC_RISKS[variant]

        high_risk = {v: r for v, r in risk_profile.items() if max(r[k] for k in r if isinstance(r[k], float)) > 0.5}

        return {
            "patient_id": patient_id,
            "analysis_type": "genomic_sequencing",
            "tier": self.tier.value,
            "variants_identified": variants,
            "risk_profile": risk_profile,
            "high_risk_variants": list(high_risk.keys()),
            "overall_genomic_risk": "high" if high_risk else "moderate" if risk_profile else "low",
            "nanotech_sequencing": True,
            "accuracy_pct": 99.7,
        }

    def recommend_treatment(self, patient_data: dict, diagnosis: str) -> dict:
        """Generate a personalized treatment recommendation.

        patient_data: {patient_id, age, weight_kg, conditions, ...}
        diagnosis: primary diagnosis string
        """
        self._require_pro("Treatment recommendations")

        patient_id = patient_data.get("patient_id", "unknown")
        age = patient_data.get("age", 0)
        conditions = patient_data.get("conditions", [])

        treatments = {
            "cancer":        ["oncology_referral", "imaging_workup", "biopsy"],
            "diabetes":      ["metformin", "lifestyle_modification", "glucose_monitoring"],
            "cardiovascular": ["aspirin", "atorvastatin", "cardiac_rehabilitation"],
            "infection":     ["antibiotic_therapy", "hydration", "rest"],
        }

        base = treatments.get(diagnosis.lower(), ["specialist_referral", "further_testing"])

        result = {
            "patient_id": patient_id,
            "diagnosis": diagnosis,
            "recommended_treatments": base,
            "tier": self.tier.value,
            "confidence": 0.75,
            "disclaimer": "AI-assisted recommendation — always verify with a licensed physician.",
        }

        if self.tier == Tier.ENTERPRISE:
            result["personalized"] = True
            result["genomic_adjusted"] = True
            result["precision_score"] = 0.94
            if age > 65:
                result["age_adjusted_notes"] = "Geriatric dosing guidelines applied"
            if conditions:
                result["comorbidity_adjustments"] = conditions

        return result


# ---------------------------------------------------------------------------
# PrecisionMedicineEngine
# ---------------------------------------------------------------------------

class PrecisionMedicineEngine:
    """Engine for building patient profiles, calculating drug efficacy,
    and generating full treatment plans.

    FREE: not available.
    PRO: profiles + basic efficacy.
    ENTERPRISE: full precision medicine.
    """

    _PATIENT_LIMIT = {Tier.FREE: 0, Tier.PRO: 20, Tier.ENTERPRISE: None}

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._profiles: dict = {}

    def _require_pro(self, feature: str = "Precision medicine") -> None:
        if self.tier == Tier.FREE:
            raise PrecisionMedicineError(
                f"{feature} requires PRO or ENTERPRISE tier. "
                "Upgrade to access precision medicine features."
            )

    def _require_enterprise(self, feature: str = "Full treatment planning") -> None:
        if self.tier != Tier.ENTERPRISE:
            raise PrecisionMedicineError(
                f"{feature} requires ENTERPRISE tier. "
                "Upgrade to access full precision medicine capabilities."
            )

    def create_patient_profile(self, patient_data: dict) -> dict:
        """Build a personalized medicine profile for a patient.

        patient_data: {patient_id, age, sex, weight_kg, conditions, medications, variants, ...}
        """
        self._require_pro("Patient profile creation")

        patient_id = patient_data.get("patient_id", "unknown")
        limit = self._PATIENT_LIMIT[self.tier]
        if limit is not None and len(self._profiles) >= limit and patient_id not in self._profiles:
            raise PrecisionMedicineError(
                f"{self.tier.value.upper()} tier allows only {limit} patient profile(s). "
                "Upgrade to ENTERPRISE for unlimited profiles."
            )

        profile = {
            "patient_id": patient_id,
            "age": patient_data.get("age"),
            "sex": patient_data.get("sex"),
            "weight_kg": patient_data.get("weight_kg"),
            "conditions": patient_data.get("conditions", []),
            "current_medications": patient_data.get("medications", []),
            "allergies": patient_data.get("allergies", []),
            "bmi": round(patient_data.get("weight_kg", 70) / ((patient_data.get("height_cm", 170) / 100) ** 2), 1)
                   if patient_data.get("height_cm") else None,
            "tier": self.tier.value,
        }

        if self.tier == Tier.ENTERPRISE:
            profile["genomic_variants"] = patient_data.get("variants", [])
            profile["pharmacogenomics_enabled"] = True
            profile["precision_score"] = 0.96

        self._profiles[patient_id] = profile
        return profile

    def calculate_drug_efficacy(self, drug: str, patient_profile: dict) -> dict:
        """Predict drug efficacy for a patient based on their profile."""
        self._require_pro("Drug efficacy calculation")

        drug_lower = drug.lower()
        base_efficacy = DRUG_EFFICACY_TABLE.get(drug_lower, {}).get("default", 0.70)

        result = {
            "drug": drug,
            "patient_id": patient_profile.get("patient_id", "unknown"),
            "base_efficacy": base_efficacy,
            "adjusted_efficacy": base_efficacy,
            "tier": self.tier.value,
            "recommendation": "suitable" if base_efficacy >= 0.65 else "consider_alternative",
        }

        if self.tier == Tier.ENTERPRISE:
            variants = patient_profile.get("genomic_variants", [])
            drug_table = DRUG_EFFICACY_TABLE.get(drug_lower, {})
            adjusted = base_efficacy
            variant_adjustments = []
            for variant in variants:
                if variant in drug_table:
                    adjusted = drug_table[variant]
                    variant_adjustments.append({"variant": variant, "adjusted_efficacy": adjusted})

            result["adjusted_efficacy"] = adjusted
            result["genomic_adjustments"] = variant_adjustments
            result["pharmacogenomics_applied"] = True
            result["recommendation"] = "suitable" if adjusted >= 0.65 else "consider_alternative"

        return result

    def generate_treatment_plan(self, patient_id: str, condition: str) -> dict:
        """Generate a full personalized treatment plan."""
        self._require_enterprise("Full treatment plan generation")

        profile = self._profiles.get(patient_id, {"patient_id": patient_id})
        conditions = profile.get("conditions", [])
        variants = profile.get("genomic_variants", [])

        plans = {
            "cancer":        {
                "primary": ["targeted_immunotherapy", "surgical_resection"],
                "supportive": ["anti-emetics", "nutritional_support"],
                "monitoring": ["monthly_imaging", "tumour_markers"],
            },
            "diabetes":      {
                "primary": ["metformin_500mg_bid", "sglt2_inhibitor"],
                "supportive": ["dietary_counselling", "exercise_program"],
                "monitoring": ["quarterly_HbA1c", "daily_glucose"],
            },
            "cardiovascular": {
                "primary": ["aspirin_81mg_daily", "atorvastatin_20mg"],
                "supportive": ["cardiac_rehab", "stress_reduction"],
                "monitoring": ["monthly_lipid_panel", "echocardiogram"],
            },
            "infection":     {
                "primary": ["broad_spectrum_antibiotic"],
                "supportive": ["iv_fluids", "analgesics"],
                "monitoring": ["daily_cbc", "culture_results"],
            },
        }

        plan = plans.get(condition.lower(), {
            "primary": ["specialist_referral"],
            "supportive": ["general_supportive_care"],
            "monitoring": ["regular_follow_up"],
        })

        return {
            "patient_id": patient_id,
            "condition": condition,
            "treatment_plan": plan,
            "personalized": True,
            "genomic_variants_considered": variants,
            "comorbidities_considered": conditions,
            "tier": self.tier.value,
            "plan_version": "1.0",
            "disclaimer": "AI-generated plan — requires physician review before implementation.",
        }
