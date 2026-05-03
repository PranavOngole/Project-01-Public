"""
Fundamental Analyst — FA-01

The conviction engine. Evaluates financial statements and produces the
Value Conviction Score (0-100) and a recommended purchase price.

Runs after the World Researcher deposits its context packet.
Forms an independent financial view first, then stress-tests it against
real-world context before issuing the final verdict.

Implementation is not public.
"""

from __future__ import annotations
from typing import Any
from agents.base_agent import BaseAgent


class FundamentalAnalyst(BaseAgent):
    AGENT_ID = "FA-01"

    def run(self, ticker: str, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Implementation not public.")
