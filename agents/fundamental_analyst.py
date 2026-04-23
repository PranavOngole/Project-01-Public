"""
agents/fundamental_analyst.py
Fundamental Analyst — FA-01

The core conviction engine. Evaluates financial statements, calculates
intrinsic value, and produces the Value Conviction Score (0–100) plus a
recommended purchase price.

Agent ID:  FA-01
Model:     Claude Opus 4.7  (premium reasoning — the most critical agent)
Role:      analyst

Execution order in the pipeline:
  1. World Researcher (WR-01) runs first — deposits research packet to DB
  2. FA-01 does its independent financial analysis
  3. FA-01 reads WR-01's research packet
  4. FA-01 issues final report (adjusting conviction if world context warrants it)

This sequence prevents anchoring: FA-01 forms its financial view before
reading headlines, then stress-tests that view against real-world context.

Prompt:    Loaded from PROMPT_DIR/fundamental_analyst.md (private repo) or
           PROMPT_FUNDAMENTAL_ANALYST_SYSTEM env var (Railway).
"""

from __future__ import annotations

import json
import logging
from datetime import date, datetime, timezone
from typing import Any

from agents.base_agent import BaseAgent
from config import settings
from data.schema import get_connection

logger = logging.getLogger(__name__)


class FundamentalAnalyst(BaseAgent):

    AGENT_ID = "FA-01"

    def __init__(self) -> None:
        super().__init__(
            agent_name="fundamental_analyst",
            model=settings.FUNDAMENTAL_ANALYST_MODEL,
            agent_id=self.AGENT_ID,
        )

    # ── Main entry point ──────────────────────────────────────────────────────

    def run(self, ticker: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Full analysis sequence for one ticker:
          1. Load financial data from DB (populated by Data Engineer)
          2. Run independent financial analysis via Opus 4.7
          3. Load World Researcher packet from DB (if available)
          4. Synthesize — issue final conviction call

        Args:
            ticker:  Uppercase ticker (e.g. 'AAPL').
            context: Shared pipeline dict. Must contain 'run_id'.
                     Reads: 'financial_data' (from Data Engineer)
                     Writes: 'fundamental_analysis' (consumed by Manager)

        Returns:
            status          — 'success' | 'partial' | 'failed'
            cost_usd        — total API spend for this agent's calls
            output          — dict with all FA-01 results
        """
        run_id = context.get("run_id")
        financial_data = context.get("financial_data", {})

        try:
            # Step 1: Independent financial analysis
            financial_analysis = self._analyze_financials(
                ticker=ticker,
                financial_data=financial_data,
                run_id=run_id,
            )

            # Step 2: Load World Researcher context
            world_context = self._load_world_research(ticker)

            # Step 3: Synthesize — final conviction with world context applied
            if world_context:
                final_output = self._synthesize_with_world_context(
                    ticker=ticker,
                    financial_analysis=financial_analysis,
                    world_context=world_context,
                    run_id=run_id,
                )
            else:
                logger.warning(
                    "[FA-01] No world research found for %s — issuing "
                    "conviction from financials only.", ticker
                )
                final_output = financial_analysis

            # Write results to DB
            self._save_results(ticker=ticker, run_id=run_id, output=final_output)

            # Update shared context for downstream agents (Manager)
            context["fundamental_analysis"] = final_output

            total_cost = (
                financial_analysis.get("_meta", {}).get("cost_usd", 0.0)
                + final_output.get("_meta", {}).get("synthesis_cost_usd", 0.0)
            )

            self.log_activity(
                what_i_did=f"Full fundamental analysis for {ticker}",
                wins=f"Signal: {final_output.get('signal')} | VCS: {final_output.get('vcs_score')}",
            )

            return {
                "status": "success",
                "cost_usd": total_cost,
                "output": final_output,
            }

        except Exception as exc:
            logger.error("[FA-01] Analysis failed for %s: %s", ticker, exc, exc_info=True)
            self.log_activity(
                what_i_did=f"Attempted analysis for {ticker}",
                losses=str(exc),
            )
            return {
                "status": "failed",
                "cost_usd": 0.0,
                "output": {"error": str(exc)},
            }

    # ── Step 1: Financial analysis ────────────────────────────────────────────

    def _analyze_financials(
        self,
        ticker: str,
        financial_data: dict[str, Any],
        run_id: str | None,
    ) -> dict[str, Any]:
        """
        Call Opus 4.7 with financial data only — no world context yet.
        Forms a pure fundamentals-based conviction.
        """
        system_prompt = self._build_system_prompt()

        user_message = (
            f"Analyze the following financial data for {ticker} and produce "
            f"your Value Conviction Score, signal, intrinsic value range, and "
            f"recommended purchase price.

"
            f"```json
{json.dumps(financial_data, indent=2, default=str)}
```"
        )

        result = self.call_api(
            messages=[{"role": "user", "content": user_message}],
            system=system_prompt,
            ticker=ticker,
            run_id=run_id,
            triggered_by="user_analysis",
            enable_thinking=True,
            thinking_budget_tokens=10_000,
        )

        parsed = self._parse_response(result["content"])
        parsed["_meta"] = {
            "cost_usd": result["cost"]["total_cost_usd"],
            "duration_ms": result["duration_ms"],
            "stage": "financial_analysis",
        }
        return parsed

    # ── Step 2: Load World Research ───────────────────────────────────────────

    def _load_world_research(self, ticker: str) -> dict[str, Any] | None:
        """
        Read the most recent WR-01 research packet for this ticker from DB.
        Returns None if no packet exists (World Researcher hasn't run yet or failed).
        """
        try:
            conn = get_connection()
            row = conn.execute(
                """
                SELECT research_packet
                FROM world_research
                WHERE ticker = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                [ticker],
            ).fetchone()
            conn.close()

            if row and row[0]:
                return json.loads(row[0]) if isinstance(row[0], str) else row[0]
            return None

        except Exception as exc:
            logger.warning("[FA-01] Could not load world research for %s: %s", ticker, exc)
            return None

    # ── Step 3: Synthesize with world context ─────────────────────────────────

    def _synthesize_with_world_context(
        self,
        ticker: str,
        financial_analysis: dict[str, Any],
        world_context: dict[str, Any],
        run_id: str | None,
    ) -> dict[str, Any]:
        """
        Second Opus 4.7 call: review financial conviction against world context.
        Adjust VCS and signal only if world context materially changes the thesis.
        """
        system_prompt = self._build_system_prompt()

        user_message = (
            f"You have completed your financial analysis of {ticker}. "
            f"Now review it against the following real-world research context "
            f"gathered by the World Researcher.

"
            f"YOUR FINANCIAL ANALYSIS:
"
            f"```json
{json.dumps(financial_analysis, indent=2, default=str)}
```

"
            f"WORLD RESEARCH CONTEXT:
"
            f"```json
{json.dumps(world_context, indent=2, default=str)}
```

"
            f"Issue your FINAL report. Maintain your financial conviction unless "
            f"the world context reveals something that materially changes the thesis "
            f"(e.g. fraud, major catalyst, existential risk). "
            f"Explain any adjustments."
        )

        result = self.call_api(
            messages=[{"role": "user", "content": user_message}],
            system=system_prompt,
            ticker=ticker,
            run_id=run_id,
            triggered_by="user_analysis",
            enable_thinking=True,
            thinking_budget_tokens=6_000,
        )

        parsed = self._parse_response(result["content"])
        parsed["_meta"] = {
            "cost_usd": result["cost"]["total_cost_usd"],
            "synthesis_cost_usd": result["cost"]["total_cost_usd"],
            "duration_ms": result["duration_ms"],
            "stage": "synthesis_with_world_context",
            "world_context_applied": True,
        }
        return parsed

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _build_system_prompt(self) -> list[dict[str, Any]]:
        """
        Load the FA-01 system prompt with prompt caching enabled.
        Prompt file lives in Project-01-Private/prompts/fundamental_analyst.md.
        On Railway, inject as PROMPT_FUNDAMENTAL_ANALYST_SYSTEM env var.
        """
        prompt_text = self.load_prompt_env(
            env_key="PROMPT_FUNDAMENTAL_ANALYST_SYSTEM",
            fallback_key="fundamental_analyst",
        )
        return [
            {
                "type": "text",
                "text": prompt_text,
                "cache_control": {"type": "ephemeral"},
            }
        ]

    def _parse_response(self, content: list) -> dict[str, Any]:
        """
        Extract text from Anthropic content blocks and attempt JSON parse.
        Falls back to raw text if the model doesn't return valid JSON.
        """
        text_blocks = [
            getattr(block, "text", "")
            for block in content
            if getattr(block, "type", "") == "text"
        ]
        full_text = "
".join(text_blocks).strip()

        # Try to extract JSON from a ```json ... ``` block
        import re
        json_match = re.search(r"```json\s*([\s\S]+?)\s*```", full_text)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except json.JSONDecodeError:
                pass

        # Try bare JSON
        try:
            return json.loads(full_text)
        except json.JSONDecodeError:
            pass

        # Return structured fallback with raw text
        return {
            "signal": "UNKNOWN",
            "vcs_score": None,
            "purchase_price": None,
            "intrinsic_value_low": None,
            "intrinsic_value_high": None,
            "raw_analysis": full_text,
            "parse_error": True,
        }

    def _save_results(
        self,
        ticker: str,
        run_id: str | None,
        output: dict[str, Any],
    ) -> None:
        """
        Persist FA-01 results to analysis_results table.
        Silently absorbs DB errors — a write failure must not crash the pipeline.
        """
        try:
            conn = get_connection()
            conn.execute(
                """
                INSERT INTO analysis_results (
                    run_id, ticker, agent_id, agent_name,
                    output_json, signal, vcs_score, purchase_price,
                    created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    run_id, ticker, self.AGENT_ID, self.agent_name,
                    json.dumps(output, default=str),
                    output.get("signal"),
                    output.get("vcs_score"),
                    output.get("purchase_price"),
                    datetime.now(timezone.utc),
                ],
            )
            conn.commit()
            conn.close()
        except Exception as exc:
            logger.error("[FA-01] Failed to save results to DB: %s", exc)
