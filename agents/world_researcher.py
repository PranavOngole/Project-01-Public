"""
World Researcher — WR-01

Gathers real-world context for a ticker before the conviction engine runs:
news, filings, analyst sentiment, insider moves, macro environment, catalysts.

Runs first in the pipeline. Deposits a structured research packet that the
conviction engine reads after forming its independent financial view.

Implementation is not public.
"""

from __future__ import annotations
from typing import Any
from agents.base_agent import BaseAgent


class WorldResearcher(BaseAgent):
    AGENT_ID = "WR-01"

    def run(self, ticker: str, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Implementation not public.")
