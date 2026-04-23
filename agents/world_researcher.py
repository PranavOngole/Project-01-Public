"""
agents/world_researcher.py
World Researcher — WR-01

Runs FIRST in every analysis pipeline. Gathers all real-world context about
a company — news, filings, analyst sentiment, insider moves, macro environment,
upcoming catalysts — and deposits a structured research packet into the database.

Fundamental Analyst (FA-01) reads this packet after forming its own independent
financial view, before issuing the final report.

Agent ID:  WR-01
Model:     OpenAI (gpt-4.1 by default — configurable via WORLD_RESEARCHER_MODEL)
           OpenAI is chosen here for its strong web-grounded retrieval capabilities.
Role:      analyst

Pipeline position:
  WR-01 → FA-01 → (future: TA-01, MGR-01, ...)

Prompt:    Loaded from PROMPT_DIR/world_researcher.md (private repo) or
           PROMPT_WORLD_RESEARCHER_SYSTEM env var (Railway).

Output stored in:  world_research table (DuckDB)
"""

from __future__ import annotations

import json
import logging
import time
from datetime import date, datetime, timezone
from typing import Any

from openai import OpenAI

from config import settings
from data.schema import get_connection

logger = logging.getLogger(__name__)


class WorldResearcher:
    """
    World Researcher — WR-01.

    Not a subclass of BaseAgent because it uses the OpenAI SDK, not Anthropic.
    Mirrors BaseAgent's logging contract: writes to api_usage and agent_logs.
    """

    AGENT_ID  = "WR-01"
    AGENT_NAME = "world_researcher"
    AGENT_ROLE = "analyst"

    def __init__(self) -> None:
        self.model  = settings.WORLD_RESEARCHER_MODEL
        self._client = OpenAI(api_key=settings.OPENAI_API_KEY)
        logger.debug("WorldResearcher (WR-01) initialised → model=%s", self.model)

    # ── Main entry point ──────────────────────────────────────────────────────

    def run(self, ticker: str, context: dict[str, Any]) -> dict[str, Any]:
        """
        Research everything about `ticker` and deposit a structured packet to DB.

        Args:
            ticker:  Uppercase ticker (e.g. 'AAPL').
            context: Shared pipeline dict. Must contain 'run_id'.
                     Writes: 'world_research' (consumed by FA-01 via DB read)

        Returns:
            status   — 'success' | 'partial' | 'failed'
            cost_usd — estimated API spend
            output   — the research packet dict
        """
        run_id = context.get("run_id")

        try:
            packet = self._research(ticker=ticker, run_id=run_id)
            self._save_packet(ticker=ticker, run_id=run_id, packet=packet)
            context["world_research"] = packet

            self._log_activity(
                what_i_did=f"Full world research for {ticker}",
                wins=f"Found {len(packet.get('news_items', []))} news items, "
                     f"{len(packet.get('catalysts', []))} catalysts",
            )

            return {
                "status": "success",
                "cost_usd": packet.get("_meta", {}).get("cost_usd", 0.0),
                "output": packet,
            }

        except Exception as exc:
            logger.error("[WR-01] Research failed for %s: %s", ticker, exc, exc_info=True)
            self._log_activity(
                what_i_did=f"Attempted research for {ticker}",
                losses=str(exc),
            )
            return {
                "status": "failed",
                "cost_usd": 0.0,
                "output": {"error": str(exc)},
            }

    # ── Core research call ────────────────────────────────────────────────────

    def _research(self, ticker: str, run_id: str | None) -> dict[str, Any]:
        """
        OpenAI call to gather world context for `ticker`.
        Returns a structured research packet dict.
        """
        system_prompt = self._load_system_prompt()

        user_message = (
            f"Research {ticker} comprehensively. Gather and structure:
"
            f"1. Recent news (last 30 days) — material events only
"
            f"2. Latest earnings call highlights and analyst estimate revisions
"
            f"3. SEC filing summaries (most recent 10-K / 10-Q key points)
"
            f"4. Insider transactions (last 90 days)
"
            f"5. Short interest and notable institutional ownership changes
"
            f"6. Macro / sector context relevant to this company right now
"
            f"7. Upcoming catalysts (earnings date, product launches, regulatory decisions, "
            f"   FDA approvals, contract announcements)

"
            f"Return a single JSON object with these keys:
"
            f"  ticker, research_date, news_items (list), earnings_summary, "
            f"  sec_filing_summary, insider_transactions (list), "
            f"  institutional_changes, macro_context, catalysts (list), "
            f"  overall_sentiment (bullish/neutral/bearish), "
            f"  red_flags (list — empty if none), "
            f"  researcher_notes (free text summary)

"
            f"Be factual. Flag uncertainty explicitly. Do not fabricate data."
        )

        t0 = time.monotonic()
        request_started_at = datetime.now(timezone.utc)

        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_message},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        duration_ms = int((time.monotonic() - t0) * 1000)
        request_completed_at = datetime.now(timezone.utc)

        usage = response.usage
        cost  = self._calculate_cost(
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
        )

        logger.info(
            "[WR-01] %s | ticker=%s in=%d out=%d cost=$%.4f dur=%dms",
            self.model, ticker,
            usage.prompt_tokens, usage.completion_tokens,
            cost, duration_ms,
        )

        self._log_api_usage(
            run_id=run_id,
            ticker=ticker,
            input_tokens=usage.prompt_tokens,
            output_tokens=usage.completion_tokens,
            cost_usd=cost,
            request_started_at=request_started_at,
            request_completed_at=request_completed_at,
            latency_ms=duration_ms,
            request_id=response.id,
        )

        try:
            packet = json.loads(response.choices[0].message.content)
        except json.JSONDecodeError:
            packet = {"raw_response": response.choices[0].message.content}

        packet["_meta"] = {
            "cost_usd":    cost,
            "duration_ms": duration_ms,
            "model":       self.model,
            "stage":       "world_research",
        }
        return packet

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _load_system_prompt(self) -> str:
        """
        Load WR-01 system prompt from env var or PROMPT_DIR file.
        On Railway: set PROMPT_WORLD_RESEARCHER_SYSTEM env var.
        Locally: place world_researcher.md in PROMPT_DIR.
        """
        import os
        from pathlib import Path

        env_prompt = os.getenv("PROMPT_WORLD_RESEARCHER_SYSTEM", "").strip()
        if env_prompt:
            return env_prompt

        prompt_dir = settings.PROMPT_DIR
        if prompt_dir:
            prompt_path = Path(prompt_dir) / "world_researcher.md"
            if prompt_path.exists():
                return prompt_path.read_text(encoding="utf-8")

        # Minimal fallback — real prompt lives in private repo
        return (
            "You are a world-class financial research analyst. "
            "Your job is to gather comprehensive, factual, real-world context "
            "about publicly traded companies. Always return valid JSON. "
            "Never fabricate data — flag uncertainty explicitly."
        )

    @staticmethod
    def _calculate_cost(input_tokens: int, output_tokens: int) -> float:
        """
        Estimate OpenAI cost for one call.
        GPT-4.1: $2.00 input / $8.00 output per 1M tokens (as of 2026-04).
        Update PRICING dict in settings if rates change.
        """
        rates = settings.OPENAI_PRICING.get(
            settings.WORLD_RESEARCHER_MODEL,
            {"input": 2.00 / 1_000_000, "output": 8.00 / 1_000_000},
        )
        return round(
            input_tokens  * rates["input"] +
            output_tokens * rates["output"],
            6,
        )

    # ── DB writes ─────────────────────────────────────────────────────────────

    def _save_packet(
        self,
        ticker: str,
        run_id: str | None,
        packet: dict[str, Any],
    ) -> None:
        """
        Write research packet to world_research table.
        FA-01 reads from this table — this is the handoff mechanism.
        """
        try:
            conn = get_connection()
            conn.execute(
                """
                INSERT INTO world_research (
                    run_id, ticker, model,
                    research_packet, overall_sentiment, red_flags_count,
                    created_at, created_date
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                [
                    run_id,
                    ticker,
                    self.model,
                    json.dumps(packet, default=str),
                    packet.get("overall_sentiment"),
                    len(packet.get("red_flags", [])),
                    datetime.now(timezone.utc),
                    date.today(),
                ],
            )
            conn.commit()
            conn.close()
            logger.debug("[WR-01] Research packet saved for %s", ticker)
        except Exception as exc:
            logger.error("[WR-01] Failed to save research packet: %s", exc)

    def _log_api_usage(
        self,
        run_id: str | None,
        ticker: str,
        input_tokens: int,
        output_tokens: int,
        cost_usd: float,
        request_started_at: datetime,
        request_completed_at: datetime,
        latency_ms: int,
        request_id: str | None,
    ) -> None:
        """Write one row to api_usage — same schema as BaseAgent._log_api_usage."""
        try:
            conn = get_connection()
            conn.execute(
                """
                INSERT INTO api_usage (
                    run_id, ticker, triggered_by,
                    agent_name, agent_id, agent_role,
                    api_provider, api_endpoint, model, model_tier,
                    input_tokens, input_cached_tokens, input_uncached_tokens,
                    output_tokens, thinking_tokens, response_tokens, total_tokens,
                    input_cost_usd, output_cost_usd, thinking_cost_usd, total_cost_usd,
                    prompt_cache_status, cache_creation_tokens, cache_read_tokens,
                    request_started_at, request_completed_at, latency_ms,
                    request_id, is_error, environment,
                    created_date, created_at
                ) VALUES (
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?, ?,
                    ?, ?
                )
                """,
                [
                    run_id, ticker, "user_analysis",
                    self.AGENT_NAME, self.AGENT_ID, self.AGENT_ROLE,
                    "openai", "/v1/chat/completions", self.model, "standard",
                    input_tokens, 0, input_tokens,
                    output_tokens, 0, output_tokens, input_tokens + output_tokens,
                    round(input_tokens  * settings.OPENAI_PRICING.get(self.model, {"input": 2e-6})["input"],  6),
                    round(output_tokens * settings.OPENAI_PRICING.get(self.model, {"output": 8e-6})["output"], 6),
                    0.0, cost_usd,
                    "none", 0, 0,
                    request_started_at, request_completed_at, latency_ms,
                    request_id, False, settings.APP_ENV,
                    date.today(), datetime.now(timezone.utc),
                ],
            )
            conn.commit()
            conn.close()
        except Exception as exc:
            logger.error("[WR-01] Failed to write api_usage: %s", exc)

    def _log_activity(
        self,
        what_i_did: str | None = None,
        wins: str | None = None,
        losses: str | None = None,
    ) -> None:
        """UPSERT daily activity into agent_logs (mirrors BaseAgent.log_activity)."""
        today = date.today()
        now   = datetime.now(timezone.utc)
        try:
            conn = get_connection()
            row = conn.execute(
                """
                SELECT COUNT(DISTINCT run_id), COUNT(*),
                       COALESCE(SUM(total_tokens), 0),
                       COALESCE(SUM(total_cost_usd), 0.0),
                       CAST(AVG(latency_ms) AS INTEGER)
                FROM api_usage
                WHERE agent_name = ? AND created_date = ?
                """,
                [self.AGENT_NAME, today],
            ).fetchone()
            conn.execute(
                """
                INSERT INTO agent_logs (
                    log_date, agent_id, agent_name,
                    what_i_did, wins, losses,
                    analyses_completed, api_calls_made,
                    total_tokens_used, total_cost_usd,
                    errors_encountered, avg_latency_ms,
                    created_date, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT (log_date, agent_id) DO UPDATE SET
                    what_i_did         = excluded.what_i_did,
                    wins               = excluded.wins,
                    losses             = excluded.losses,
                    analyses_completed = excluded.analyses_completed,
                    api_calls_made     = excluded.api_calls_made,
                    total_tokens_used  = excluded.total_tokens_used,
                    total_cost_usd     = excluded.total_cost_usd,
                    avg_latency_ms     = excluded.avg_latency_ms,
                    updated_at         = excluded.updated_at
                """,
                [
                    today, self.AGENT_ID, self.AGENT_NAME,
                    what_i_did, wins, losses,
                    row[0] or 0, row[1] or 0,
                    row[2] or 0, row[3] or 0.0,
                    0, row[4],
                    today, now, now,
                ],
            )
            conn.commit()
            conn.close()
        except Exception as exc:
            logger.error("[WR-01] Failed to write agent_logs: %s", exc)
