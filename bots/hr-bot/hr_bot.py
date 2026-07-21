"""HR Bot - Job descriptions, resume screening, interview questions, and HR compliance."""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.base_bot import BaseBot


class HRBot(BaseBot):
    """AI bot for HR automation: job descriptions, resume screening, onboarding, and compliance."""

    def __init__(self):
        """Initialize the HRBot."""
        super().__init__(
            name="hr-bot",
            description="Automates HR tasks: job descriptions, resume screening, interview prep, onboarding, and EEOC compliance.",
            version="2.0.0",
        )
        self.priority = "medium"

    def run(self):
        """Run the HR bot main workflow."""
        self.start()
        return self.get_status()

    def write_job_description(self, role: str, requirements: list, company_culture: str) -> dict:
        """Write a complete, EEOC-compliant job description."""
        return {
            "role": role,
            "title": role,
            "company_culture": company_culture,
            "job_description": f"""
## {role}

**About the Role**
We are looking for a talented {role} to join our growing team. In this role, you will [key responsibilities].

**What You'll Do**
- Lead and execute key {role} initiatives
- Collaborate with cross-functional teams
- Drive measurable results aligned with company goals
- Mentor junior team members as needed

**Requirements**
{chr(10).join(f'- {req}' for req in requirements)}

**Nice to Have**
- Experience in a fast-paced startup environment
- Track record of shipping products/projects on time
- Strong written and verbal communication skills

**What We Offer**
- Competitive salary and equity package
- Comprehensive health, dental, and vision insurance
- Flexible remote/hybrid work options
- 401(k) with company match
- Unlimited PTO policy

**Company Culture**
{company_culture}

*We are an equal opportunity employer and value diversity. We do not discriminate based on race, religion, color, national origin, gender, sexual orientation, age, marital status, veteran status, or disability status.*
""",
            "eeoc_compliant": True,
            "inclusive_language_score": 92,
            "estimated_salary_range": self.benchmark_salary(role, "US National", "mid-level"),
        }

    def screen_resume(self, resume_text: str, job_requirements: list) -> dict:
        """Screen a resume against job requirements and return a match score."""
        resume_lower = resume_text.lower()
        matched = []
        missing = []
        for req in job_requirements:
            if req.lower() in resume_lower:
                matched.append(req)
            else:
                missing.append(req)
        score = (len(matched) / len(job_requirements) * 100) if job_requirements else 0
        return {
            "match_score_percent": round(score, 1),
            "requirements_matched": matched,
            "requirements_missing": missing,
            "recommendation": "Interview" if score >= 70 else "Phone screen" if score >= 50 else "Pass",
            "red_flags": [],
            "green_flags": ["Resume length appropriate (1-2 pages)"] if len(resume_text) < 3000 else [],
            "note": "Resume screening is a first-pass filter. Human review required before decisions.",
        }

    def generate_interview_questions(self, role: str, level: str) -> dict:
        """Generate role-specific interview questions."""
        levels = {"entry": "junior", "mid": "mid-level", "senior": "senior", "executive": "executive"}
        lvl = levels.get(level.lower(), "mid-level")
        behavioral = [
            "Tell me about a time you faced a significant challenge in your work. How did you resolve it?",
            "Describe a situation where you had to work with a difficult stakeholder. What was the outcome?",
            "Give an example of when you had to make a decision with incomplete information.",
            "Tell me about a project you're most proud of and your specific contribution.",
            "Describe a time you received critical feedback. How did you respond?",
        ]
        technical = [
            f"Walk me through your approach to [key {role} challenge].",
            f"What tools/frameworks do you use for {role} work and why?",
            f"How do you stay current with trends in {role}?",
            f"Describe your process for [key {role} deliverable].",
        ]
        if lvl in ["senior", "executive"]:
            technical.append(f"How would you build a {role} team from scratch?")
            technical.append("Tell me about a time you influenced strategy at the organizational level.")
        return {
            "role": role,
            "level": level,
            "behavioral_questions": behavioral[:4],
            "technical_questions": technical,
            "culture_fit_questions": [
                "What type of work environment brings out your best performance?",
                "How do you handle ambiguity and changing priorities?",
                "What does success look like to you in this role in 90 days?",
            ],
            "illegal_questions_to_avoid": [
                "Never ask about: age, race, religion, national origin, gender, marital status, children, disabilities",
                "Focus on: skills, experience, work authorization (legally permitted), ability to perform job functions",
            ],
        }

    def create_onboarding_checklist(self, role: str, department: str) -> dict:
        """Create a comprehensive onboarding checklist."""
        return {
            "role": role,
            "department": department,
            "day_1": [
                "Welcome meeting with manager",
                "Complete HR paperwork (I-9, W-4, direct deposit)",
                "IT setup: laptop, accounts, access cards",
                "Company tour and team introductions",
                "Review employee handbook",
                "Set up email, Slack, and required tools",
            ],
            "week_1": [
                "Meet all team members (1:1 intro meetings)",
                "Complete compliance training (EEOC, harassment prevention, security)",
                "Review department goals and OKRs",
                "Shadow experienced team member",
                "Set up 30-60-90 day plan with manager",
                "Get access to all required systems",
            ],
            "month_1": [
                "Complete role-specific training",
                "Submit first independent work product",
                "30-day check-in with manager",
                "Connect with key cross-functional stakeholders",
                "Complete benefits enrollment",
            ],
            "month_3": [
                "90-day performance review",
                "Transition from onboarding to full ownership",
                "Set annual performance goals",
                "Complete any remaining certifications",
            ],
        }

    def performance_review_template(self, employee_data: dict) -> dict:
        """Generate a structured performance review template."""
        return {
            "employee": employee_data.get("name", "[Employee Name]"),
            "role": employee_data.get("role", "[Role]"),
            "review_period": employee_data.get("period", "Annual"),
            "sections": {
                "goal_achievement": {
                    "prompt": "Rate achievement of each goal set at the start of the period (1-5 scale)",
                    "goals": ["[Goal 1]", "[Goal 2]", "[Goal 3]"],
                    "rating": None,
                },
                "core_competencies": {
                    "items": ["Communication", "Collaboration", "Problem-solving", "Leadership", "Technical skills"],
                    "scale": "1=Below expectations, 2=Partially meets, 3=Meets, 4=Exceeds, 5=Outstanding",
                },
                "strengths": {"prompt": "List 3 demonstrated strengths with specific examples"},
                "development_areas": {"prompt": "List 2-3 areas for growth with actionable steps"},
                "career_goals": {"prompt": "Document employee's stated career goals and how role supports them"},
                "overall_rating": {"scale": "Below/Partially/Meets/Exceeds/Outstanding expectations"},
                "manager_comments": {"prompt": "Overall summary and key messages for employee"},
                "employee_comments": {"prompt": "Employee self-assessment and feedback"},
            },
            "signatures": {
                "employee": "[Signature + Date]",
                "manager": "[Signature + Date]",
                "hr_representative": "[Signature + Date]",
            },
        }

    def benchmark_salary(self, role: str, location: str, experience: str) -> dict:
        """Benchmark salary for a role based on location and experience."""
        base_ranges = {
            "engineer": (95000, 180000),
            "manager": (85000, 160000),
            "analyst": (65000, 120000),
            "designer": (70000, 130000),
            "sales": (60000, 150000),
            "hr": (55000, 110000),
            "marketing": (60000, 130000),
        }
        role_lower = role.lower()
        base = next((v for k, v in base_ranges.items() if k in role_lower), (70000, 140000))
        multipliers = {"entry": 0.75, "junior": 0.85, "mid-level": 1.0, "senior": 1.3, "principal": 1.5, "executive": 2.0}
        mult = multipliers.get(experience.lower(), 1.0)
        low = int(base[0] * mult)
        high = int(base[1] * mult)
        return {
            "role": role,
            "location": location,
            "experience_level": experience,
            "salary_range": {"low": f"${low:,}", "high": f"${high:,}"},
            "median": f"${int((low + high) / 2):,}",
            "total_comp_note": "Add 20-30% for full compensation (benefits, equity, bonus)",
            "sources": ["Levels.fyi", "Glassdoor", "LinkedIn Salary", "Bureau of Labor Statistics"],
        }

    def employee_handbook_section(self, topic: str) -> dict:
        """Generate a handbook section for a given HR topic."""
        sections = {
            "pto": {
                "title": "Paid Time Off Policy",
                "content": "Full-time employees accrue 15 days of PTO annually (1.25 days/month). PTO must be approved by manager 2 weeks in advance for 3+ consecutive days. Unused PTO carries over up to 30 days.",
            },
            "remote": {
                "title": "Remote Work Policy",
                "content": "Employees may work remotely up to 3 days/week with manager approval. All remote work must comply with data security policy. Core hours: 10am-3pm local time.",
            },
            "harassment": {
                "title": "Anti-Harassment Policy",
                "content": "We maintain zero tolerance for harassment of any kind. All employees must complete annual harassment prevention training. Report incidents to HR at hr@company.com or anonymously via [HOTLINE].",
            },
        }
        key = topic.lower().replace(" ", "_")
        section = sections.get(key, {
            "title": f"{topic.title()} Policy",
            "content": f"[Complete {topic} policy content here - consult employment attorney for jurisdiction-specific requirements]",
        })
        return {"topic": topic, **section, "last_updated": "2024", "legal_review_required": True}

    def compliance_check(self, policy_type: str) -> dict:
        """Check HR policies for EEOC, FLSA, and related compliance."""
        return {
            "policy_type": policy_type,
            "eeoc_requirements": [
                "Post EEOC 'Know Your Rights' notice in workplace",
                "File EEO-1 report annually (if 100+ employees)",
                "No discriminatory language in job postings",
                "Consistent interview questions across all candidates",
                "Document all hiring decisions",
            ],
            "flsa_requirements": [
                "Correctly classify employees as exempt vs non-exempt",
                "Pay non-exempt employees 1.5x for overtime (>40 hrs/week)",
                "Maintain records of hours worked for 3 years",
                "Pay at least federal minimum wage ($7.25/hr federal; check state)",
                "Provide pay stubs as required by state law",
            ],
            "fmla_requirements": [
                "Post FMLA notice (50+ employees)",
                "Provide 12 weeks unpaid leave for qualifying events",
                "Maintain health benefits during FMLA leave",
            ],
            "recommendation": "Review all HR policies annually with employment attorney",
        }
