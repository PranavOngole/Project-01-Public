"""
agents/__init__.py
Agent registry for Project-01.

Current agents (Baby Steps build):
  WR-01  WorldResearcher    — OpenAI GPT-4.1, runs first every pipeline
  FA-01  FundamentalAnalyst — Claude Opus 4.7, core conviction engine

Pipeline order: WR-01 → FA-01
"""

from agents.world_researcher import WorldResearcher
from agents.fundamental_analyst import FundamentalAnalyst

__all__ = [
    "WorldResearcher",
    "FundamentalAnalyst",
]
