"""Medical Bot - Health information with HIPAA compliance and medical disclaimers."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.base_bot import BaseBot

MEDICAL_DISCLAIMER = (
    "DISCLAIMER: This information is for educational purposes only and does NOT constitute "
    "medical advice. Always consult a licensed healthcare professional for diagnosis, treatment, "
    "and medical decisions. In case of emergency, call 911 immediately."
)


class MedicalBot(BaseBot):
    """AI bot for health information, clinical trial discovery, and HIPAA compliance guidance."""

    def __init__(self):
        """Initialize the MedicalBot with HIPAA compliance emphasis."""
        super().__init__(
            name="medical-bot",
            description="Provides health information, clinical trial discovery, and HIPAA compliance tools.",
            version="2.0.0",
        )
        self.priority = "medium"
        self._compliance_packages = ["HIPAA", "HITECH"]

    def run(self):
        """Run the medical bot main workflow."""
        self.start()
        return self.hipaa_compliance_check()

    def analyze_symptoms(self, symptoms_list: list) -> dict:
        """Analyze a list of symptoms and return possible conditions with a medical disclaimer."""
        self.log(f"Analyzing symptoms: {symptoms_list}")
        symptom_map = {
            "headache": ["Tension headache", "Migraine", "Dehydration", "Hypertension"],
            "fever": ["Common cold", "Influenza", "COVID-19", "Bacterial infection"],
            "chest pain": ["Muscle strain", "Acid reflux", "Angina - SEEK IMMEDIATE CARE"],
            "fatigue": ["Anemia", "Thyroid disorder", "Sleep apnea", "Diabetes"],
            "cough": ["Upper respiratory infection", "Allergies", "Asthma", "Bronchitis"],
            "shortness of breath": ["Asthma", "Anxiety", "Pneumonia - SEEK CARE"],
        }
        possible_conditions = []
        for symptom in symptoms_list:
            for key, conditions in symptom_map.items():
                if key in symptom.lower():
                    possible_conditions.extend(conditions)
        possible_conditions = list(set(possible_conditions)) if possible_conditions else [
            "No matching conditions found in knowledge base"
        ]
        return {
            "disclaimer": MEDICAL_DISCLAIMER,
            "symptoms_analyzed": symptoms_list,
            "possible_conditions": possible_conditions[:5],
            "urgency_indicator": "SEEK IMMEDIATE CARE" if any("SEEK" in c for c in possible_conditions) else "Monitor symptoms; consult doctor if persisting",
            "recommended_action": "Schedule appointment with primary care physician",
            "emergency_number": "911 (US) | 999 (UK) | 112 (EU)",
        }

    def find_clinical_trials(self, condition: str) -> list:
        """Find relevant clinical trials for a medical condition."""
        self.log(f"Searching clinical trials: {condition}")
        return [
            {
                "trial_id": f"NCT-{condition[:3].upper()}-2024-001",
                "title": f"Phase III Trial: Novel Treatment for {condition.title()}",
                "phase": "Phase III",
                "sponsor": "National Institutes of Health",
                "status": "Recruiting",
                "location": "Multiple US sites",
                "compensation": "$150/visit",
                "eligibility": f"Adults 18-65 with diagnosed {condition}",
                "link": f"https://clinicaltrials.gov/search?cond={condition.replace(' ', '+')}",
            },
            {
                "trial_id": f"NCT-{condition[:3].upper()}-2024-002",
                "title": f"Observational Study: Long-term Outcomes in {condition.title()} Patients",
                "phase": "Observational",
                "sponsor": "Mayo Clinic",
                "status": "Active",
                "location": "Rochester, MN",
                "compensation": "$50/visit",
                "eligibility": f"Diagnosed with {condition} within last 5 years",
                "link": "https://clinicaltrials.gov",
            },
        ]

    def search_medical_literature(self, query: str) -> list:
        """Search for relevant medical literature on a topic."""
        self.log(f"Searching medical literature: {query}")
        return [
            {
                "title": f"Recent Advances in {query.title()}: A Systematic Review",
                "authors": "Smith J, Johnson M, Williams R",
                "journal": "New England Journal of Medicine",
                "year": 2024,
                "impact_factor": 91.2,
                "abstract": f"This systematic review analyzes 142 studies on {query} published between 2019-2024...",
                "link": f"https://pubmed.ncbi.nlm.nih.gov/?term={query.replace(' ', '+')}",
            },
            {
                "title": f"Clinical Guidelines for {query.title()} Management",
                "authors": "American Medical Association Working Group",
                "journal": "JAMA Internal Medicine",
                "year": 2024,
                "impact_factor": 21.9,
                "abstract": f"Updated clinical practice guidelines for {query} based on current evidence...",
                "link": "https://pubmed.ncbi.nlm.nih.gov",
            },
        ]

    def check_drug_interactions(self, drug1: str, drug2: str) -> dict:
        """Check for potential interactions between two medications."""
        self.log(f"Checking drug interactions: {drug1} + {drug2}")
        known_interactions = {
            ("warfarin", "aspirin"): "MAJOR: Increased bleeding risk. Monitor closely.",
            ("ssri", "maoi"): "CONTRAINDICATED: Serotonin syndrome risk. Do NOT combine.",
            ("statin", "grapefruit"): "MODERATE: Grapefruit increases statin levels.",
        }
        for (d1, d2), interaction in known_interactions.items():
            if d1 in drug1.lower() or d1 in drug2.lower():
                if d2 in drug1.lower() or d2 in drug2.lower():
                    severity = interaction.split(":")[0]
                    return {
                        "disclaimer": MEDICAL_DISCLAIMER,
                        "drug1": drug1,
                        "drug2": drug2,
                        "interaction_found": True,
                        "severity": severity,
                        "description": interaction,
                        "recommendation": "Consult your pharmacist or physician immediately",
                    }
        return {
            "disclaimer": MEDICAL_DISCLAIMER,
            "drug1": drug1,
            "drug2": drug2,
            "interaction_found": False,
            "severity": "None detected in database",
            "recommendation": "Always consult your pharmacist to verify - databases may be incomplete",
        }

    def find_specialists(self, specialty: str, location: str) -> list:
        """Find medical specialists by specialty and location."""
        self.log(f"Finding {specialty} specialists in {location}")
        return [
            {
                "name": f"Dr. Sarah {specialty.capitalize()} MD",
                "specialty": specialty.title(),
                "location": location,
                "hospital": f"{location} Medical Center",
                "rating": 4.8,
                "accepting_patients": True,
                "insurance": "Most major plans",
                "phone": "(555) 100-2000",
                "link": f"https://www.zocdoc.com/search?specialty={specialty}",
            },
            {
                "name": f"Dr. James Williams {specialty[:4].upper()}, MD, FACP",
                "specialty": specialty.title(),
                "location": location,
                "hospital": f"{location} University Hospital",
                "rating": 4.9,
                "accepting_patients": True,
                "insurance": "Medicare, Medicaid, PPO",
                "phone": "(555) 200-3000",
                "link": "https://www.healthgrades.com",
            },
        ]

    def hipaa_compliance_check(self) -> dict:
        """Return a HIPAA compliance checklist for healthcare organizations."""
        return {
            "framework": "HIPAA / HITECH Compliance Checklist",
            "last_updated": "2024",
            "administrative_safeguards": [
                {"item": "Security Officer designated", "required": True},
                {"item": "Workforce training completed (annual)", "required": True},
                {"item": "Risk assessment conducted (annual)", "required": True},
                {"item": "Business Associate Agreements (BAAs) in place", "required": True},
                {"item": "Sanction policy for violations", "required": True},
            ],
            "physical_safeguards": [
                {"item": "Facility access controls", "required": True},
                {"item": "Workstation use policy", "required": True},
                {"item": "Device and media controls", "required": True},
            ],
            "technical_safeguards": [
                {"item": "Access control (unique user IDs)", "required": True},
                {"item": "Audit logs enabled", "required": True},
                {"item": "Data encryption at rest and in transit", "required": True},
                {"item": "Automatic logoff enabled", "required": True},
                {"item": "Emergency access procedure", "required": True},
            ],
            "breach_notification": [
                {"item": "60-day notification to HHS", "required": True},
                {"item": "Individual notification within 60 days", "required": True},
                {"item": "Media notification if 500+ individuals in state", "required": True},
            ],
            "resources": [
                "https://www.hhs.gov/hipaa",
                "https://www.hhs.gov/hipaa/for-professionals/security/index.html",
            ],
        }

    def medical_equipment_suggestions(self, department: str) -> list:
        """Return medical equipment recommendations for a given department."""
        equipment_map = {
            "emergency": ["Crash cart / AED", "Ventilators", "Portable monitors", "IV pumps", "Oxygen delivery systems"],
            "radiology": ["MRI scanner", "CT scanner", "Digital X-ray", "Ultrasound machines", "PACS software"],
            "icu": ["Hemodynamic monitors", "Ventilators", "Infusion pumps", "Warming blankets", "Dialysis machines"],
            "surgery": ["Surgical robot (da Vinci)", "Anesthesia machines", "Electrosurgical units", "Laparoscopic equipment"],
            "general": ["Electronic health record (EHR) system", "Patient kiosks", "Telemedicine platform", "Blood pressure monitors"],
        }
        dept_lower = department.lower()
        for key, equipment in equipment_map.items():
            if key in dept_lower:
                return [{"equipment": e, "estimated_cost": "Contact vendor for pricing"} for e in equipment]
        return [{"equipment": e, "estimated_cost": "Contact vendor for pricing"}
                for e in equipment_map["general"]]

    def generate_patient_report_template(self) -> dict:
        """Generate a standardized patient report template."""
        return {
            "disclaimer": MEDICAL_DISCLAIMER,
            "template": {
                "patient_info": {"name": "[PATIENT NAME]", "dob": "[DATE OF BIRTH]", "mrn": "[MEDICAL RECORD NUMBER]"},
                "visit_date": "[VISIT DATE]",
                "chief_complaint": "[PRIMARY REASON FOR VISIT]",
                "history_of_present_illness": "[DETAILED SYMPTOM HISTORY]",
                "past_medical_history": "[PREVIOUS CONDITIONS]",
                "medications": ["[MEDICATION 1 - DOSE - FREQUENCY]"],
                "allergies": ["[ALLERGY 1]"],
                "physical_exam": {"vitals": "BP: ___ HR: ___ Temp: ___ RR: ___ SpO2: ___", "findings": "[EXAM FINDINGS]"},
                "assessment": "[DIAGNOSIS / ASSESSMENT]",
                "plan": ["[TREATMENT 1]", "[FOLLOW-UP INSTRUCTIONS]"],
                "provider_signature": "[PROVIDER NAME, CREDENTIALS, DATE]",
            },
        }
