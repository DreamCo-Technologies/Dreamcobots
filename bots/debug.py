# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
import os

# If DISTUTILS_DEBUG is anything other than the empty string, we run in
# debug mode.
DEBUG = bool(os.environ.get('DISTUTILS_DEBUG'))
