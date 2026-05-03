"""Base class for all research pipeline agents. Implementation not public."""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any


class BaseAgent(ABC):
    """Abstract base for all Project-01 research agents."""

    @abstractmethod
    def run(self, ticker: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Run this agent for the given ticker.

        Returns:
            dict with keys: status ('success'|'partial'|'failed'), cost_usd, output
        """
