"""
Data Engineer — DE-01

Handles the raw data pipeline: price history, financial statements,
options data. Populates the database before specialist agents run.

Implementation is not public.
"""

from __future__ import annotations
from typing import Any
from agents.base_agent import BaseAgent


class DataEngineer(BaseAgent):
    AGENT_ID = "DE-01"

    def run(self, ticker: str, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Implementation not public.")
