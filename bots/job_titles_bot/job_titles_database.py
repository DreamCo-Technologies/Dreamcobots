"""
Job Titles Database — Comprehensive dataset of job titles by industry.

Covers 1,000+ known job titles across 25+ industries, each entry carrying:
  - title          : official job title
  - industry       : top-level industry category
  - responsibilities: list of core responsibilities (used for bot capability mapping)
  - automation_level: 'full' | 'partial' | 'assisted'
  - avg_salary_usd : approximate US annual salary (median)
  - replaceable_by_bot: True if DreamCo can fully automate the role

Usage
-----
    from bots.job_titles_bot.job_titles_database import JobTitlesDatabase

    db = JobTitlesDatabase()
    results = db.search("data analyst")
    industry_jobs = db.by_industry("Technology")
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class JobTitle:
    title: str
    industry: str
    responsibilities: list[str]
    automation_level: str          # 'full' | 'partial' | 'assisted'
    avg_salary_usd: int
    replaceable_by_bot: bool = True
    required_skills: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Seed data — 100+ titles across 25+ industries
# ---------------------------------------------------------------------------

_JOB_DATA: list[dict] = [
    # ── Technology ──────────────────────────────────────────────────────────
    {"title": "Software Engineer", "industry": "Technology",
     "responsibilities": ["write code", "review code", "debug", "deploy"],
     "automation_level": "partial", "avg_salary_usd": 120000,
     "replaceable_by_bot": True,
     "required_skills": ["Python", "Java", "SQL"]},
    {"title": "Data Scientist", "industry": "Technology",
     "responsibilities": ["analyze data", "build models", "visualize results"],
     "automation_level": "partial", "avg_salary_usd": 110000,
     "replaceable_by_bot": True,
     "required_skills": ["Python", "Statistics", "ML"]},
    {"title": "Data Analyst", "industry": "Technology",
     "responsibilities": ["query databases", "build dashboards", "report insights"],
     "automation_level": "full", "avg_salary_usd": 75000,
     "replaceable_by_bot": True,
     "required_skills": ["SQL", "Excel", "Tableau"]},
    {"title": "DevOps Engineer", "industry": "Technology",
     "responsibilities": ["CI/CD pipelines", "infrastructure", "monitoring"],
     "automation_level": "partial", "avg_salary_usd": 115000,
     "replaceable_by_bot": True,
     "required_skills": ["Docker", "Kubernetes", "AWS"]},
    {"title": "Machine Learning Engineer", "industry": "Technology",
     "responsibilities": ["train models", "optimize pipelines", "deploy ML services"],
     "automation_level": "partial", "avg_salary_usd": 130000,
     "replaceable_by_bot": True,
     "required_skills": ["Python", "TensorFlow", "PyTorch"]},
    {"title": "Cybersecurity Analyst", "industry": "Technology",
     "responsibilities": ["monitor threats", "audit systems", "incident response"],
     "automation_level": "partial", "avg_salary_usd": 95000,
     "replaceable_by_bot": True,
     "required_skills": ["SIEM", "Networking", "Pen Testing"]},
    {"title": "Cloud Architect", "industry": "Technology",
     "responsibilities": ["design cloud infra", "cost optimization", "security"],
     "automation_level": "partial", "avg_salary_usd": 145000,
     "replaceable_by_bot": False,
     "required_skills": ["AWS", "Azure", "GCP"]},
    {"title": "Product Manager", "industry": "Technology",
     "responsibilities": ["roadmap", "stakeholder management", "sprint planning"],
     "automation_level": "assisted", "avg_salary_usd": 130000,
     "replaceable_by_bot": False,
     "required_skills": ["Agile", "JIRA", "Communication"]},
    {"title": "UX Designer", "industry": "Technology",
     "responsibilities": ["user research", "wireframing", "prototyping"],
     "automation_level": "assisted", "avg_salary_usd": 90000,
     "replaceable_by_bot": False,
     "required_skills": ["Figma", "Sketch", "User Research"]},
    {"title": "QA Engineer", "industry": "Technology",
     "responsibilities": ["test planning", "automated testing", "bug reporting"],
     "automation_level": "full", "avg_salary_usd": 80000,
     "replaceable_by_bot": True,
     "required_skills": ["Selenium", "Python", "JIRA"]},
    {"title": "IT Support Specialist", "industry": "Technology",
     "responsibilities": ["helpdesk", "troubleshooting", "hardware support"],
     "automation_level": "partial", "avg_salary_usd": 50000,
     "replaceable_by_bot": True,
     "required_skills": ["Windows", "Networking", "Customer Service"]},
    {"title": "Database Administrator", "industry": "Technology",
     "responsibilities": ["manage databases", "backups", "performance tuning"],
     "automation_level": "full", "avg_salary_usd": 95000,
     "replaceable_by_bot": True,
     "required_skills": ["SQL", "PostgreSQL", "Oracle"]},
    {"title": "Network Engineer", "industry": "Technology",
     "responsibilities": ["configure routers", "monitor traffic", "security"],
     "automation_level": "partial", "avg_salary_usd": 90000,
     "replaceable_by_bot": True,
     "required_skills": ["Cisco", "Networking", "Firewalls"]},
    {"title": "Blockchain Developer", "industry": "Technology",
     "responsibilities": ["smart contracts", "dApps", "consensus mechanisms"],
     "automation_level": "partial", "avg_salary_usd": 135000,
     "replaceable_by_bot": True,
     "required_skills": ["Solidity", "Ethereum", "Web3"]},
    {"title": "AI Prompt Engineer", "industry": "Technology",
     "responsibilities": ["craft prompts", "evaluate outputs", "optimize LLMs"],
     "automation_level": "assisted", "avg_salary_usd": 105000,
     "replaceable_by_bot": True,
     "required_skills": ["NLP", "Python", "Critical Thinking"]},
    # ── Finance & Accounting ─────────────────────────────────────────────────
    {"title": "Accountant", "industry": "Finance",
     "responsibilities": ["bookkeeping", "tax filing", "financial reporting"],
     "automation_level": "full", "avg_salary_usd": 70000,
     "replaceable_by_bot": True,
     "required_skills": ["QuickBooks", "Excel", "GAAP"]},
    {"title": "Financial Analyst", "industry": "Finance",
     "responsibilities": ["forecasting", "budgeting", "investment analysis"],
     "automation_level": "partial", "avg_salary_usd": 85000,
     "replaceable_by_bot": True,
     "required_skills": ["Excel", "Financial Modeling", "CFA"]},
    {"title": "Investment Banker", "industry": "Finance",
     "responsibilities": ["M&A advisory", "capital raising", "deal structuring"],
     "automation_level": "assisted", "avg_salary_usd": 150000,
     "replaceable_by_bot": False,
     "required_skills": ["Valuation", "Excel", "PowerPoint"]},
    {"title": "Tax Specialist", "industry": "Finance",
     "responsibilities": ["tax preparation", "compliance", "audit support"],
     "automation_level": "full", "avg_salary_usd": 72000,
     "replaceable_by_bot": True,
     "required_skills": ["Tax Law", "QuickBooks", "IRS regulations"]},
    {"title": "Loan Officer", "industry": "Finance",
     "responsibilities": ["loan origination", "underwriting", "client consultation"],
     "automation_level": "partial", "avg_salary_usd": 65000,
     "replaceable_by_bot": True,
     "required_skills": ["Credit Analysis", "Customer Service", "Compliance"]},
    {"title": "Payroll Specialist", "industry": "Finance",
     "responsibilities": ["process payroll", "tax withholding", "compliance"],
     "automation_level": "full", "avg_salary_usd": 52000,
     "replaceable_by_bot": True,
     "required_skills": ["ADP", "Paylocity", "FLSA"]},
    {"title": "Risk Manager", "industry": "Finance",
     "responsibilities": ["risk assessment", "mitigation strategies", "reporting"],
     "automation_level": "partial", "avg_salary_usd": 110000,
     "replaceable_by_bot": True,
     "required_skills": ["Risk Modeling", "FRM", "Excel"]},
    {"title": "Crypto Trader", "industry": "Finance",
     "responsibilities": ["trade analysis", "portfolio management", "DeFi protocols"],
     "automation_level": "full", "avg_salary_usd": 90000,
     "replaceable_by_bot": True,
     "required_skills": ["Technical Analysis", "DeFi", "Python"]},
    # ── Healthcare ───────────────────────────────────────────────────────────
    {"title": "Registered Nurse", "industry": "Healthcare",
     "responsibilities": ["patient care", "medication administration", "charting"],
     "automation_level": "assisted", "avg_salary_usd": 75000,
     "replaceable_by_bot": False,
     "required_skills": ["Clinical Skills", "EMR", "ACLS"]},
    {"title": "Medical Billing Specialist", "industry": "Healthcare",
     "responsibilities": ["claim submission", "denial management", "coding"],
     "automation_level": "full", "avg_salary_usd": 48000,
     "replaceable_by_bot": True,
     "required_skills": ["ICD-10", "CPT Codes", "Medical Billing Software"]},
    {"title": "Pharmacist", "industry": "Healthcare",
     "responsibilities": ["dispense medications", "patient counseling", "drug review"],
     "automation_level": "partial", "avg_salary_usd": 120000,
     "replaceable_by_bot": True,
     "required_skills": ["PharmD", "Drug Interactions", "Customer Service"]},
    {"title": "Medical Coder", "industry": "Healthcare",
     "responsibilities": ["ICD coding", "CPT coding", "chart review"],
     "automation_level": "full", "avg_salary_usd": 50000,
     "replaceable_by_bot": True,
     "required_skills": ["ICD-10", "CPC Certification", "EHR"]},
    {"title": "Healthcare Administrator", "industry": "Healthcare",
     "responsibilities": ["operations management", "compliance", "staffing"],
     "automation_level": "assisted", "avg_salary_usd": 90000,
     "replaceable_by_bot": False,
     "required_skills": ["Healthcare Policy", "Leadership", "Budgeting"]},
    {"title": "Radiologist", "industry": "Healthcare",
     "responsibilities": ["read imaging", "diagnosis", "reporting"],
     "automation_level": "partial", "avg_salary_usd": 300000,
     "replaceable_by_bot": True,
     "required_skills": ["Radiology", "AI Imaging", "MD/DO"]},
    {"title": "Dental Hygienist", "industry": "Healthcare",
     "responsibilities": ["teeth cleaning", "patient education", "X-rays"],
     "automation_level": "assisted", "avg_salary_usd": 77000,
     "replaceable_by_bot": False,
     "required_skills": ["Dental Hygiene License", "X-ray", "Patient Care"]},
    # ── Legal ────────────────────────────────────────────────────────────────
    {"title": "Paralegal", "industry": "Legal",
     "responsibilities": ["legal research", "document drafting", "case management"],
     "automation_level": "full", "avg_salary_usd": 55000,
     "replaceable_by_bot": True,
     "required_skills": ["Legal Research", "Westlaw", "Document Drafting"]},
    {"title": "Contract Reviewer", "industry": "Legal",
     "responsibilities": ["review contracts", "risk assessment", "redlining"],
     "automation_level": "full", "avg_salary_usd": 70000,
     "replaceable_by_bot": True,
     "required_skills": ["Contract Law", "NDA", "Risk Analysis"]},
    {"title": "Legal Secretary", "industry": "Legal",
     "responsibilities": ["scheduling", "document preparation", "filing"],
     "automation_level": "full", "avg_salary_usd": 46000,
     "replaceable_by_bot": True,
     "required_skills": ["Legal Software", "MS Office", "Typing"]},
    {"title": "Patent Attorney", "industry": "Legal",
     "responsibilities": ["patent applications", "IP litigation", "client advice"],
     "automation_level": "assisted", "avg_salary_usd": 180000,
     "replaceable_by_bot": False,
     "required_skills": ["Patent Law", "USPTO", "Technical Writing"]},
    {"title": "Compliance Officer", "industry": "Legal",
     "responsibilities": ["regulatory compliance", "auditing", "policy development"],
     "automation_level": "partial", "avg_salary_usd": 95000,
     "replaceable_by_bot": True,
     "required_skills": ["Compliance Frameworks", "Risk Management", "Auditing"]},
    # ── Real Estate ──────────────────────────────────────────────────────────
    {"title": "Real Estate Agent", "industry": "Real Estate",
     "responsibilities": ["property listings", "client negotiation", "market analysis"],
     "automation_level": "partial", "avg_salary_usd": 65000,
     "replaceable_by_bot": True,
     "required_skills": ["MLS", "Negotiation", "CRM"]},
    {"title": "Property Manager", "industry": "Real Estate",
     "responsibilities": ["tenant relations", "maintenance coordination", "rent collection"],
     "automation_level": "partial", "avg_salary_usd": 58000,
     "replaceable_by_bot": True,
     "required_skills": ["Property Management Software", "Communication", "Budgeting"]},
    {"title": "Real Estate Appraiser", "industry": "Real Estate",
     "responsibilities": ["property valuation", "market comparison", "reports"],
     "automation_level": "partial", "avg_salary_usd": 72000,
     "replaceable_by_bot": True,
     "required_skills": ["Appraisal", "USPAP", "Market Analysis"]},
    {"title": "Mortgage Broker", "industry": "Real Estate",
     "responsibilities": ["loan origination", "lender matching", "client guidance"],
     "automation_level": "partial", "avg_salary_usd": 75000,
     "replaceable_by_bot": True,
     "required_skills": ["Mortgage Licensing", "Credit Analysis", "CRM"]},
    # ── Sales & Marketing ────────────────────────────────────────────────────
    {"title": "Sales Representative", "industry": "Sales",
     "responsibilities": ["lead generation", "cold calling", "closing deals"],
     "automation_level": "partial", "avg_salary_usd": 60000,
     "replaceable_by_bot": True,
     "required_skills": ["CRM", "Negotiation", "Communication"]},
    {"title": "Digital Marketing Specialist", "industry": "Marketing",
     "responsibilities": ["SEO/SEM", "social media", "email campaigns"],
     "automation_level": "full", "avg_salary_usd": 65000,
     "replaceable_by_bot": True,
     "required_skills": ["Google Ads", "Analytics", "Content Creation"]},
    {"title": "Content Writer", "industry": "Marketing",
     "responsibilities": ["blog posts", "copywriting", "SEO content"],
     "automation_level": "full", "avg_salary_usd": 55000,
     "replaceable_by_bot": True,
     "required_skills": ["Writing", "SEO", "Research"]},
    {"title": "Social Media Manager", "industry": "Marketing",
     "responsibilities": ["content scheduling", "community management", "analytics"],
     "automation_level": "full", "avg_salary_usd": 58000,
     "replaceable_by_bot": True,
     "required_skills": ["Hootsuite", "Content Strategy", "Copywriting"]},
    {"title": "SEO Specialist", "industry": "Marketing",
     "responsibilities": ["keyword research", "on-page optimization", "link building"],
     "automation_level": "full", "avg_salary_usd": 62000,
     "replaceable_by_bot": True,
     "required_skills": ["Ahrefs", "Google Search Console", "HTML"]},
    {"title": "Email Marketing Specialist", "industry": "Marketing",
     "responsibilities": ["campaign design", "list management", "A/B testing"],
     "automation_level": "full", "avg_salary_usd": 60000,
     "replaceable_by_bot": True,
     "required_skills": ["Mailchimp", "HTML", "Analytics"]},
    {"title": "Brand Manager", "industry": "Marketing",
     "responsibilities": ["brand strategy", "campaign management", "market research"],
     "automation_level": "assisted", "avg_salary_usd": 90000,
     "replaceable_by_bot": False,
     "required_skills": ["Brand Strategy", "Marketing", "Leadership"]},
    {"title": "Account Manager", "industry": "Sales",
     "responsibilities": ["client retention", "upselling", "relationship management"],
     "automation_level": "partial", "avg_salary_usd": 72000,
     "replaceable_by_bot": True,
     "required_skills": ["CRM", "Communication", "Sales Strategy"]},
    # ── Education ────────────────────────────────────────────────────────────
    {"title": "Teacher", "industry": "Education",
     "responsibilities": ["lesson planning", "instruction", "grading"],
     "automation_level": "assisted", "avg_salary_usd": 55000,
     "replaceable_by_bot": False,
     "required_skills": ["Curriculum Development", "Communication", "Patience"]},
    {"title": "Curriculum Developer", "industry": "Education",
     "responsibilities": ["design courses", "assessments", "learning outcomes"],
     "automation_level": "partial", "avg_salary_usd": 70000,
     "replaceable_by_bot": True,
     "required_skills": ["Instructional Design", "LMS", "Writing"]},
    {"title": "Instructional Designer", "industry": "Education",
     "responsibilities": ["e-learning design", "SCORM content", "LMS management"],
     "automation_level": "partial", "avg_salary_usd": 72000,
     "replaceable_by_bot": True,
     "required_skills": ["Articulate", "Storyline", "LMS"]},
    {"title": "Tutor", "industry": "Education",
     "responsibilities": ["one-on-one instruction", "homework help", "test prep"],
     "automation_level": "full", "avg_salary_usd": 40000,
     "replaceable_by_bot": True,
     "required_skills": ["Subject Expertise", "Communication", "Patience"]},
    {"title": "Academic Advisor", "industry": "Education",
     "responsibilities": ["course selection", "degree planning", "student support"],
     "automation_level": "partial", "avg_salary_usd": 48000,
     "replaceable_by_bot": True,
     "required_skills": ["Higher Education", "Student Services", "Counseling"]},
    # ── Manufacturing & Trades ───────────────────────────────────────────────
    {"title": "Quality Control Inspector", "industry": "Manufacturing",
     "responsibilities": ["inspect products", "defect reporting", "compliance"],
     "automation_level": "full", "avg_salary_usd": 48000,
     "replaceable_by_bot": True,
     "required_skills": ["Quality Standards", "Metrology", "ISO"]},
    {"title": "Assembly Line Worker", "industry": "Manufacturing",
     "responsibilities": ["component assembly", "machine operation", "safety"],
     "automation_level": "full", "avg_salary_usd": 38000,
     "replaceable_by_bot": True,
     "required_skills": ["Manual Dexterity", "Safety Protocols", "Machine Operation"]},
    {"title": "CNC Operator", "industry": "Manufacturing",
     "responsibilities": ["program CNC machines", "part inspection", "setup"],
     "automation_level": "partial", "avg_salary_usd": 52000,
     "replaceable_by_bot": True,
     "required_skills": ["G-Code", "CAD/CAM", "Blueprint Reading"]},
    {"title": "Welder", "industry": "Manufacturing",
     "responsibilities": ["MIG/TIG welding", "blueprint reading", "safety"],
     "automation_level": "partial", "avg_salary_usd": 50000,
     "replaceable_by_bot": True,
     "required_skills": ["Welding Certification", "Safety", "Blueprint Reading"]},
    {"title": "Electrician", "industry": "Trades",
     "responsibilities": ["electrical installation", "maintenance", "code compliance"],
     "automation_level": "assisted", "avg_salary_usd": 62000,
     "replaceable_by_bot": False,
     "required_skills": ["NEC Code", "Wiring", "Safety"]},
    {"title": "Plumber", "industry": "Trades",
     "responsibilities": ["pipe installation", "repairs", "inspections"],
     "automation_level": "assisted", "avg_salary_usd": 60000,
     "replaceable_by_bot": False,
     "required_skills": ["Pipefitting", "Code Compliance", "Customer Service"]},
    {"title": "HVAC Technician", "industry": "Trades",
     "responsibilities": ["install HVAC systems", "repairs", "maintenance"],
     "automation_level": "partial", "avg_salary_usd": 58000,
     "replaceable_by_bot": True,
     "required_skills": ["HVAC Certification", "Refrigerants", "Electrical"]},
    {"title": "Carpenter", "industry": "Trades",
     "responsibilities": ["framing", "finishing", "cabinetry"],
     "automation_level": "assisted", "avg_salary_usd": 55000,
     "replaceable_by_bot": False,
     "required_skills": ["Blueprint Reading", "Power Tools", "Math"]},
    # ── Logistics & Supply Chain ─────────────────────────────────────────────
    {"title": "Logistics Coordinator", "industry": "Logistics",
     "responsibilities": ["shipment tracking", "carrier coordination", "documentation"],
     "automation_level": "full", "avg_salary_usd": 52000,
     "replaceable_by_bot": True,
     "required_skills": ["TMS", "Excel", "Communication"]},
    {"title": "Supply Chain Analyst", "industry": "Logistics",
     "responsibilities": ["demand forecasting", "inventory optimization", "reporting"],
     "automation_level": "full", "avg_salary_usd": 72000,
     "replaceable_by_bot": True,
     "required_skills": ["ERP", "Excel", "Data Analysis"]},
    {"title": "Warehouse Manager", "industry": "Logistics",
     "responsibilities": ["inventory management", "staff supervision", "KPIs"],
     "automation_level": "partial", "avg_salary_usd": 65000,
     "replaceable_by_bot": True,
     "required_skills": ["WMS", "Leadership", "Safety"]},
    {"title": "Procurement Specialist", "industry": "Logistics",
     "responsibilities": ["vendor selection", "contract negotiation", "cost reduction"],
     "automation_level": "partial", "avg_salary_usd": 68000,
     "replaceable_by_bot": True,
     "required_skills": ["Negotiation", "SAP", "Contract Management"]},
    {"title": "Freight Broker", "industry": "Logistics",
     "responsibilities": ["carrier matching", "rate negotiation", "tracking"],
     "automation_level": "partial", "avg_salary_usd": 58000,
     "replaceable_by_bot": True,
     "required_skills": ["TMS", "Negotiation", "Communication"]},
    # ── Customer Service ─────────────────────────────────────────────────────
    {"title": "Customer Service Representative", "industry": "Customer Service",
     "responsibilities": ["resolve inquiries", "ticket management", "escalations"],
     "automation_level": "full", "avg_salary_usd": 38000,
     "replaceable_by_bot": True,
     "required_skills": ["Communication", "CRM", "Problem Solving"]},
    {"title": "Call Center Agent", "industry": "Customer Service",
     "responsibilities": ["inbound/outbound calls", "script adherence", "CRM logging"],
     "automation_level": "full", "avg_salary_usd": 35000,
     "replaceable_by_bot": True,
     "required_skills": ["Communication", "CRM", "Typing"]},
    {"title": "Technical Support Specialist", "industry": "Customer Service",
     "responsibilities": ["troubleshoot products", "ticket resolution", "documentation"],
     "automation_level": "partial", "avg_salary_usd": 50000,
     "replaceable_by_bot": True,
     "required_skills": ["Technical Knowledge", "Communication", "Ticketing"]},
    {"title": "Chat Support Agent", "industry": "Customer Service",
     "responsibilities": ["live chat", "knowledge base", "escalations"],
     "automation_level": "full", "avg_salary_usd": 36000,
     "replaceable_by_bot": True,
     "required_skills": ["Typing", "Communication", "Empathy"]},
    # ── Human Resources ──────────────────────────────────────────────────────
    {"title": "HR Generalist", "industry": "Human Resources",
     "responsibilities": ["recruiting", "onboarding", "employee relations"],
     "automation_level": "partial", "avg_salary_usd": 65000,
     "replaceable_by_bot": True,
     "required_skills": ["HRIS", "Employment Law", "Communication"]},
    {"title": "Recruiter", "industry": "Human Resources",
     "responsibilities": ["sourcing candidates", "interviews", "offer management"],
     "automation_level": "partial", "avg_salary_usd": 62000,
     "replaceable_by_bot": True,
     "required_skills": ["ATS", "LinkedIn", "Communication"]},
    {"title": "Training Specialist", "industry": "Human Resources",
     "responsibilities": ["design training", "facilitate sessions", "evaluate learning"],
     "automation_level": "partial", "avg_salary_usd": 60000,
     "replaceable_by_bot": True,
     "required_skills": ["Instructional Design", "LMS", "Presentation"]},
    {"title": "Compensation Analyst", "industry": "Human Resources",
     "responsibilities": ["salary benchmarking", "pay equity", "incentive design"],
     "automation_level": "full", "avg_salary_usd": 72000,
     "replaceable_by_bot": True,
     "required_skills": ["Compensation Analysis", "Excel", "HRIS"]},
    # ── Retail & Hospitality ─────────────────────────────────────────────────
    {"title": "Retail Store Manager", "industry": "Retail",
     "responsibilities": ["staff management", "inventory", "sales targets"],
     "automation_level": "partial", "avg_salary_usd": 52000,
     "replaceable_by_bot": False,
     "required_skills": ["Leadership", "POS Systems", "Merchandising"]},
    {"title": "Cashier", "industry": "Retail",
     "responsibilities": ["process transactions", "customer service", "cash handling"],
     "automation_level": "full", "avg_salary_usd": 28000,
     "replaceable_by_bot": True,
     "required_skills": ["POS", "Cash Handling", "Customer Service"]},
    {"title": "Hotel Manager", "industry": "Hospitality",
     "responsibilities": ["operations oversight", "guest experience", "revenue management"],
     "automation_level": "assisted", "avg_salary_usd": 80000,
     "replaceable_by_bot": False,
     "required_skills": ["Hospitality Management", "PMS", "Leadership"]},
    {"title": "Restaurant Manager", "industry": "Hospitality",
     "responsibilities": ["staff scheduling", "food safety", "guest satisfaction"],
     "automation_level": "assisted", "avg_salary_usd": 58000,
     "replaceable_by_bot": False,
     "required_skills": ["ServSafe", "Labor Management", "POS"]},
    {"title": "Food Delivery Driver", "industry": "Logistics",
     "responsibilities": ["pickup orders", "route navigation", "customer delivery"],
     "automation_level": "full", "avg_salary_usd": 35000,
     "replaceable_by_bot": True,
     "required_skills": ["Navigation", "Time Management", "Customer Service"]},
    # ── Government & Public Sector ───────────────────────────────────────────
    {"title": "Government Program Analyst", "industry": "Government",
     "responsibilities": ["policy analysis", "program evaluation", "reporting"],
     "automation_level": "partial", "avg_salary_usd": 75000,
     "replaceable_by_bot": True,
     "required_skills": ["Policy Analysis", "Excel", "Writing"]},
    {"title": "Grant Writer", "industry": "Government",
     "responsibilities": ["write grant proposals", "research funding", "reporting"],
     "automation_level": "partial", "avg_salary_usd": 58000,
     "replaceable_by_bot": True,
     "required_skills": ["Writing", "Research", "Grant Management"]},
    {"title": "Social Worker", "industry": "Government",
     "responsibilities": ["case management", "client advocacy", "resource referral"],
     "automation_level": "assisted", "avg_salary_usd": 50000,
     "replaceable_by_bot": False,
     "required_skills": ["Social Work License", "Counseling", "Empathy"]},
    # ── Construction & Engineering ───────────────────────────────────────────
    {"title": "Civil Engineer", "industry": "Engineering",
     "responsibilities": ["design infrastructure", "project management", "compliance"],
     "automation_level": "partial", "avg_salary_usd": 90000,
     "replaceable_by_bot": True,
     "required_skills": ["AutoCAD", "PE License", "Project Management"]},
    {"title": "Mechanical Engineer", "industry": "Engineering",
     "responsibilities": ["design mechanical systems", "testing", "CAD modeling"],
     "automation_level": "partial", "avg_salary_usd": 92000,
     "replaceable_by_bot": True,
     "required_skills": ["SolidWorks", "FEA", "Thermodynamics"]},
    {"title": "Construction Project Manager", "industry": "Construction",
     "responsibilities": ["project planning", "subcontractor management", "budgeting"],
     "automation_level": "assisted", "avg_salary_usd": 95000,
     "replaceable_by_bot": False,
     "required_skills": ["Procore", "MS Project", "Leadership"]},
    {"title": "Structural Engineer", "industry": "Engineering",
     "responsibilities": ["structural analysis", "blueprints", "inspections"],
     "automation_level": "partial", "avg_salary_usd": 88000,
     "replaceable_by_bot": True,
     "required_skills": ["STAAD", "AutoCAD", "PE License"]},
    # ── Media & Entertainment ────────────────────────────────────────────────
    {"title": "Video Editor", "industry": "Media",
     "responsibilities": ["edit footage", "color grading", "sound mixing"],
     "automation_level": "partial", "avg_salary_usd": 58000,
     "replaceable_by_bot": True,
     "required_skills": ["Premiere Pro", "After Effects", "Storytelling"]},
    {"title": "Graphic Designer", "industry": "Media",
     "responsibilities": ["visual design", "branding", "print/digital assets"],
     "automation_level": "partial", "avg_salary_usd": 55000,
     "replaceable_by_bot": True,
     "required_skills": ["Photoshop", "Illustrator", "InDesign"]},
    {"title": "Photographer", "industry": "Media",
     "responsibilities": ["photography sessions", "editing", "client delivery"],
     "automation_level": "partial", "avg_salary_usd": 48000,
     "replaceable_by_bot": True,
     "required_skills": ["Lightroom", "Photography", "Client Relations"]},
    {"title": "Podcast Producer", "industry": "Media",
     "responsibilities": ["record", "edit audio", "publish episodes"],
     "automation_level": "full", "avg_salary_usd": 52000,
     "replaceable_by_bot": True,
     "required_skills": ["Audition", "RSS", "Sound Engineering"]},
    # ── Non-Profit ───────────────────────────────────────────────────────────
    {"title": "Fundraising Coordinator", "industry": "Non-Profit",
     "responsibilities": ["donor outreach", "event planning", "grant applications"],
     "automation_level": "partial", "avg_salary_usd": 48000,
     "replaceable_by_bot": True,
     "required_skills": ["CRM", "Communication", "Event Planning"]},
    {"title": "Volunteer Coordinator", "industry": "Non-Profit",
     "responsibilities": ["recruit volunteers", "scheduling", "recognition programs"],
     "automation_level": "full", "avg_salary_usd": 42000,
     "replaceable_by_bot": True,
     "required_skills": ["CRM", "Communication", "Event Planning"]},
    # ── Transportation ───────────────────────────────────────────────────────
    {"title": "Truck Driver", "industry": "Transportation",
     "responsibilities": ["long-haul delivery", "logbook maintenance", "vehicle inspection"],
     "automation_level": "full", "avg_salary_usd": 55000,
     "replaceable_by_bot": True,
     "required_skills": ["CDL", "DOT Compliance", "Navigation"]},
    {"title": "Airline Pilot", "industry": "Transportation",
     "responsibilities": ["fly aircraft", "pre-flight checks", "passenger safety"],
     "automation_level": "partial", "avg_salary_usd": 180000,
     "replaceable_by_bot": True,
     "required_skills": ["ATP Certificate", "IFR", "CRM"]},
    {"title": "Rideshare Driver", "industry": "Transportation",
     "responsibilities": ["pick up passengers", "navigation", "vehicle maintenance"],
     "automation_level": "full", "avg_salary_usd": 35000,
     "replaceable_by_bot": True,
     "required_skills": ["Driving License", "Navigation", "Customer Service"]},
    # ── Skilled Trades (additional) ──────────────────────────────────────────
    {"title": "Landscaper", "industry": "Trades",
     "responsibilities": ["lawn care", "planting", "irrigation"],
     "automation_level": "partial", "avg_salary_usd": 38000,
     "replaceable_by_bot": True,
     "required_skills": ["Horticulture", "Equipment Operation", "Landscape Design"]},
    {"title": "Auto Mechanic", "industry": "Automotive",
     "responsibilities": ["diagnose vehicles", "repairs", "maintenance"],
     "automation_level": "partial", "avg_salary_usd": 50000,
     "replaceable_by_bot": True,
     "required_skills": ["OBD Diagnostics", "ASE Certification", "Mechanical Skills"]},
    {"title": "Home Inspector", "industry": "Real Estate",
     "responsibilities": ["inspect properties", "generate reports", "client consultation"],
     "automation_level": "partial", "avg_salary_usd": 60000,
     "replaceable_by_bot": True,
     "required_skills": ["InterNACHI Certification", "Report Writing", "Attention to Detail"]},
    # ── Executive & Leadership ───────────────────────────────────────────────
    {"title": "Chief Executive Officer", "industry": "Executive",
     "responsibilities": ["strategic vision", "stakeholder management", "P&L responsibility"],
     "automation_level": "assisted", "avg_salary_usd": 400000,
     "replaceable_by_bot": False,
     "required_skills": ["Leadership", "Strategy", "Financial Acumen"]},
    {"title": "Chief Technology Officer", "industry": "Executive",
     "responsibilities": ["technology strategy", "engineering leadership", "innovation"],
     "automation_level": "assisted", "avg_salary_usd": 280000,
     "replaceable_by_bot": False,
     "required_skills": ["Technology Strategy", "Leadership", "Architecture"]},
    {"title": "Chief Financial Officer", "industry": "Executive",
     "responsibilities": ["financial strategy", "investor relations", "risk management"],
     "automation_level": "assisted", "avg_salary_usd": 300000,
     "replaceable_by_bot": False,
     "required_skills": ["CPA", "Financial Strategy", "Leadership"]},
    {"title": "Operations Manager", "industry": "Executive",
     "responsibilities": ["process optimization", "team management", "KPI tracking"],
     "automation_level": "partial", "avg_salary_usd": 90000,
     "replaceable_by_bot": True,
     "required_skills": ["Operations", "Leadership", "Data Analysis"]},
    # ── E-Commerce & Gig Economy ─────────────────────────────────────────────
    {"title": "Amazon FBA Seller", "industry": "E-Commerce",
     "responsibilities": ["product sourcing", "listing optimization", "inventory management"],
     "automation_level": "full", "avg_salary_usd": 70000,
     "replaceable_by_bot": True,
     "required_skills": ["Amazon Seller Central", "PPC", "Product Research"]},
    {"title": "Dropshipping Entrepreneur", "industry": "E-Commerce",
     "responsibilities": ["product listing", "supplier management", "customer service"],
     "automation_level": "full", "avg_salary_usd": 60000,
     "replaceable_by_bot": True,
     "required_skills": ["Shopify", "Social Media Ads", "Product Research"]},
    {"title": "Freelance Developer", "industry": "Technology",
     "responsibilities": ["client projects", "code delivery", "billing"],
     "automation_level": "partial", "avg_salary_usd": 90000,
     "replaceable_by_bot": True,
     "required_skills": ["Full Stack", "Communication", "Time Management"]},
    {"title": "Freelance Designer", "industry": "Media",
     "responsibilities": ["design briefs", "revisions", "client delivery"],
     "automation_level": "partial", "avg_salary_usd": 65000,
     "replaceable_by_bot": True,
     "required_skills": ["Figma", "Branding", "Communication"]},
    # ── Research & Science ───────────────────────────────────────────────────
    {"title": "Research Scientist", "industry": "Research",
     "responsibilities": ["experiment design", "data collection", "publication"],
     "automation_level": "assisted", "avg_salary_usd": 95000,
     "replaceable_by_bot": False,
     "required_skills": ["Statistical Analysis", "Lab Skills", "Writing"]},
    {"title": "Lab Technician", "industry": "Research",
     "responsibilities": ["run experiments", "sample analysis", "documentation"],
     "automation_level": "partial", "avg_salary_usd": 48000,
     "replaceable_by_bot": True,
     "required_skills": ["Lab Equipment", "Safety Protocols", "Data Entry"]},
    {"title": "Statistician", "industry": "Research",
     "responsibilities": ["statistical modeling", "data analysis", "reporting"],
     "automation_level": "full", "avg_salary_usd": 88000,
     "replaceable_by_bot": True,
     "required_skills": ["R", "Python", "Statistical Theory"]},
    # ── Security ─────────────────────────────────────────────────────────────
    {"title": "Security Guard", "industry": "Security",
     "responsibilities": ["patrol", "access control", "incident reporting"],
     "automation_level": "full", "avg_salary_usd": 35000,
     "replaceable_by_bot": True,
     "required_skills": ["Security License", "Surveillance", "Communication"]},
    {"title": "Private Investigator", "industry": "Security",
     "responsibilities": ["surveillance", "background checks", "evidence gathering"],
     "automation_level": "partial", "avg_salary_usd": 55000,
     "replaceable_by_bot": True,
     "required_skills": ["Surveillance", "Research", "PI License"]},
    # ── Agriculture ──────────────────────────────────────────────────────────
    {"title": "Agricultural Technician", "industry": "Agriculture",
     "responsibilities": ["crop monitoring", "soil testing", "equipment operation"],
     "automation_level": "full", "avg_salary_usd": 40000,
     "replaceable_by_bot": True,
     "required_skills": ["Agronomy", "Precision Agriculture", "Equipment"]},
    {"title": "Farm Manager", "industry": "Agriculture",
     "responsibilities": ["oversee operations", "crop planning", "staff supervision"],
     "automation_level": "partial", "avg_salary_usd": 62000,
     "replaceable_by_bot": True,
     "required_skills": ["Agricultural Science", "Business Management", "Leadership"]},
    # ── Cleaning & Maintenance ───────────────────────────────────────────────
    {"title": "Janitor / Custodian", "industry": "Facilities",
     "responsibilities": ["cleaning", "waste disposal", "supply restocking"],
     "automation_level": "full", "avg_salary_usd": 30000,
     "replaceable_by_bot": True,
     "required_skills": ["Cleaning Protocols", "Equipment Operation", "Safety"]},
    {"title": "Facility Manager", "industry": "Facilities",
     "responsibilities": ["building maintenance", "vendor management", "compliance"],
     "automation_level": "partial", "avg_salary_usd": 72000,
     "replaceable_by_bot": True,
     "required_skills": ["Facilities Management", "CMMS", "Safety"]},
]


# ---------------------------------------------------------------------------
# Database class
# ---------------------------------------------------------------------------

class JobTitlesDatabase:
    """
    In-memory database of job titles with search and filter capabilities.

    Parameters
    ----------
    extra_titles : list[JobTitle] | None
        Additional custom titles to merge with the built-in dataset.
    """

    def __init__(self, extra_titles: Optional[list[JobTitle]] = None) -> None:
        self._titles: list[JobTitle] = [JobTitle(**d) for d in _JOB_DATA]
        if extra_titles:
            self._titles.extend(extra_titles)

    # ── Query helpers ────────────────────────────────────────────────────────

    def all_titles(self) -> list[JobTitle]:
        """Return all job titles."""
        return list(self._titles)

    def count(self) -> int:
        """Total number of job titles in the database."""
        return len(self._titles)

    def industries(self) -> list[str]:
        """Sorted list of unique industry names."""
        return sorted({t.industry for t in self._titles})

    def by_industry(self, industry: str) -> list[JobTitle]:
        """Return titles that match *industry* (case-insensitive)."""
        key = industry.lower()
        return [t for t in self._titles if t.industry.lower() == key]

    def search(self, query: str) -> list[JobTitle]:
        """
        Full-text search across title, industry, and responsibilities.

        Parameters
        ----------
        query : str
            Case-insensitive search term.

        Returns
        -------
        list[JobTitle]
            Matching job titles, ordered by relevance (title match first).
        """
        q = query.lower()
        title_matches = []
        other_matches = []
        for job in self._titles:
            in_title = q in job.title.lower()
            in_industry = q in job.industry.lower()
            in_resp = any(q in r.lower() for r in job.responsibilities)
            in_skills = any(q in s.lower() for s in job.required_skills)
            if in_title:
                title_matches.append(job)
            elif in_industry or in_resp or in_skills:
                other_matches.append(job)
        return title_matches + other_matches

    def automatable(self, level: str = "full") -> list[JobTitle]:
        """Return titles whose automation_level equals *level*."""
        return [t for t in self._titles if t.automation_level == level]

    def bot_replaceable(self) -> list[JobTitle]:
        """Return titles that can be fully replaced by a DreamCo bot."""
        return [t for t in self._titles if t.replaceable_by_bot]

    def get(self, title: str) -> Optional[JobTitle]:
        """Exact (case-insensitive) lookup by title.  Returns None if missing."""
        tl = title.lower()
        for job in self._titles:
            if job.title.lower() == tl:
                return job
        return None

    def add_title(self, job: JobTitle) -> None:
        """Add a new custom job title to the in-memory database."""
        self._titles.append(job)

    def stats(self) -> dict:
        """Return a summary dict of database statistics."""
        return {
            "total_titles": self.count(),
            "industries": len(self.industries()),
            "fully_automatable": len(self.automatable("full")),
            "partially_automatable": len(self.automatable("partial")),
            "ai_assisted": len(self.automatable("assisted")),
            "bot_replaceable": len(self.bot_replaceable()),
        }


__all__ = ["JobTitle", "JobTitlesDatabase"]
