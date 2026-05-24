"""
DreamCo SDK
=============

Python client library for the DreamCo platform.  Install via::

    pip install dreamco-sdk  # coming to PyPI

Usage::

    from dreamco_sdk import DreamCoClient

    client = DreamCoClient(api_url="http://localhost:8000", api_key="dc_prod_...")
    bots = await client.list_bots()
    result = await client.run_bot("lead_gen_bot", payload={"target": "ACME Corp"})
"""

from dreamco_sdk.client import DreamCoClient
from dreamco_sdk.models import BotResult, BotStatus, RunRequest

__version__ = "1.0.0"
__all__ = ["DreamCoClient", "BotResult", "BotStatus", "RunRequest"]
