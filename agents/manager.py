"""
Manager — MGR-01

Orchestrates the full research pipeline. Sequences specialist agents,
threads context between them, enforces budget limits, and resolves
any conflicting outputs before the final report is issued.

Implementation is not public.
"""

from __future__ import annotations
from typing import Any
from agents.base_agent import BaseAgent


class ManagerAgent(BaseAgent):
    AGENT_ID = "MGR-01"

    def run(self, ticker: str, context: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError("Implementation not public.")
