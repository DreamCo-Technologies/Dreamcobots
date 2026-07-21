"""
DreamCo Global Learning System
================================
A structured, scalable microservice architecture for autonomous AI research,
classification, experimentation, and deployment across DreamCo bots.

Submodules
----------
ingestion      — data ingestion from papers, GitHub, Kaggle, and datasets
classifier     — auto-classification of AI methods and tagging
sandbox_lab    — isolated AI testing, A/B tests, and metrics collection
analytics      — performance analysis and Global Learning Matrix
evolution      — hybrid model generation via genetic and RL algorithms
deployment     — strategy deployment and continuous bot retraining
profit_layer   — ROI tracking and market-adaptation monitoring
governance     — compliance, encryption, and audit logging
database       — schema definitions and database connectivity
api            — REST API endpoints for learning and bot control
dashboards     — monitoring dashboards for learning, sandbox, and profit
"""

__version__ = "1.0.0"
__all__ = [
    "ingestion",
    "classifier",
    "sandbox_lab",
    "analytics",
    "evolution",
    "deployment",
    "profit_layer",
    "governance",
    "database",
    "api",
    "dashboards",
]
