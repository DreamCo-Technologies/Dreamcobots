"""
Configuration module for the 211 Resource and Eligibility Checker Bot.
Loads settings from environment variables with sensible defaults.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

import os

# -------------------------------------------------------------------
# 211 API settings
# Register for a free key at https://developer.211.org
# -------------------------------------------------------------------
API_211_BASE_URL = os.getenv("API_211_BASE_URL", "https://api.211.org/search/v1/resources")
API_211_KEY = os.getenv("API_211_KEY", "")

# -------------------------------------------------------------------
# Bot / session settings
# -------------------------------------------------------------------
SESSION_TTL_SECONDS = int(os.getenv("SESSION_TTL_SECONDS", "3600"))  # 1 hour

# -------------------------------------------------------------------
# Supported languages (ISO 639-1 codes)
# Only languages that have entries in TRANSLATIONS are listed here.
# Add a translation dict to TRANSLATIONS and then add the code below
# before advertising a new language.
# -------------------------------------------------------------------
SUPPORTED_LANGUAGES = ["en", "es"]

# -------------------------------------------------------------------
# Eligibility program definitions
# Each entry maps a program name to its federal poverty level (FPL)
# threshold as a fraction (e.g. 1.30 = 130 % of FPL) and household-
# size adjustment table (annual FPL base amounts for 2024).
# Sources:
#   SNAP  – 130 % FPL  (https://www.fns.usda.gov/snap/recipient/eligibility)
#   Medicaid – 138 % FPL (ACA expansion states)
#   CHIP  – 200 % FPL
#   WIC   – 185 % FPL
#   Rent Assistance – 50 % AMI (approximated via 80 % FPL)
# -------------------------------------------------------------------
# Annual FPL amounts by household size (contiguous US, 2024)
FPL_BASE = {
    1: 15060,
    2: 20440,
    3: 25820,
    4: 31200,
    5: 36580,
    6: 41960,
    7: 47340,
    8: 52720,
}
FPL_ADDITIONAL_PER_PERSON = 5380  # for households > 8

PROGRAMS = {
    "SNAP": {
        "description": "Supplemental Nutrition Assistance Program (food stamps)",
        "fpl_threshold": 1.30,
        "category": "food",
    },
    "Medicaid": {
        "description": "Free or low-cost health coverage for adults and children",
        "fpl_threshold": 1.38,
        "category": "health",
    },
    "CHIP": {
        "description": "Children's Health Insurance Program",
        "fpl_threshold": 2.00,
        "category": "health",
    },
    "WIC": {
        "description": "Women, Infants, and Children nutrition program",
        "fpl_threshold": 1.85,
        "category": "food",
    },
    "RentAssistance": {
        "description": "Emergency rental assistance and housing programs",
        "fpl_threshold": 0.80,
        "category": "housing",
    },
}

# -------------------------------------------------------------------
# Resource categories supported for 211 search
# -------------------------------------------------------------------
RESOURCE_CATEGORIES = [
    "housing",
    "food",
    "mental_health",
    "health",
    "employment",
    "childcare",
    "transportation",
    "utilities",
    "legal",
    "education",
]

# -------------------------------------------------------------------
# Multilingual prompts (simple phrase map – extend as needed)
# -------------------------------------------------------------------
TRANSLATIONS = {
    "en": {
        "welcome": (
            "Hello! I'm the 211 Resource & Eligibility Checker. "
            "I can help you find local resources and check if you qualify for assistance programs. "
            "What do you need help with today?"
        ),
        "ask_location": "What city or zip code are you in?",
        "ask_income": "What is your approximate annual household income (in USD)?",
        "ask_household_size": "How many people are in your household (including yourself)?",
        "no_results": "I couldn't find resources matching your request. Try a different category or location.",
        "eligibility_header": "Based on the information you provided, here is your eligibility:",
        "resource_header": "Here are resources near you:",
        "goodbye": "Thank you for using the 211 Resource Checker. Take care!",
        "unknown_input": "I'm not sure I understood that. Could you rephrase or type 'help' for options?",
        "help": (
            "You can ask me to:\n"
            "  • Find resources  (e.g., 'I need food assistance')\n"
            "  • Check eligibility (e.g., 'Am I eligible for SNAP?')\n"
            "  • Change language  (e.g., 'Speak Spanish')\n"
            "  • Quit  (type 'quit' or 'exit')"
        ),
    },
    "es": {
        "welcome": (
            "¡Hola! Soy el Verificador de Recursos y Elegibilidad 211. "
            "Puedo ayudarte a encontrar recursos locales y verificar si calificas para programas de asistencia. "
            "¿En qué necesitas ayuda hoy?"
        ),
        "ask_location": "¿En qué ciudad o código postal te encuentras?",
        "ask_income": "¿Cuál es el ingreso anual aproximado de tu hogar (en USD)?",
        "ask_household_size": "¿Cuántas personas viven en tu hogar (incluyéndote a ti)?",
        "no_results": "No encontré recursos que coincidan con tu solicitud. Intenta con otra categoría o ubicación.",
        "eligibility_header": "Según la información proporcionada, aquí está tu elegibilidad:",
        "resource_header": "Aquí hay recursos cerca de ti:",
        "goodbye": "¡Gracias por usar el Verificador de Recursos 211! ¡Cuídate!",
        "unknown_input": "No entendí eso. ¿Puedes reformularlo o escribir 'ayuda' para ver las opciones?",
        "help": (
            "Puedes pedirme que:\n"
            "  • Encuentre recursos  (ej., 'Necesito ayuda con comida')\n"
            "  • Verifique elegibilidad (ej., '¿Soy elegible para SNAP?')\n"
            "  • Cambie de idioma  (ej., 'Habla inglés')\n"
            "  • Salga  (escribe 'salir' o 'exit')"
        ),
    },
}
