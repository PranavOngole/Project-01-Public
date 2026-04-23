"""
config/settings.py
Load all environment variables from .env into typed constants.

Every API key and secret MUST come from the environment — nothing hardcoded.
Copy .env.example → .env and fill in real values before running.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from the project root (one level above this file)
load_dotenv(Path(__file__).parent.parent / ".env")


# ── AI Provider — Anthropic ───────────────────────────────────────────────────

ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")


# ── AI Provider — OpenAI ──────────────────────────────────────────────────────

OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")

# OpenAI token pricing (USD per token). Update when rates change.
OPENAI_PRICING: dict[str, dict[str, float]] = {
    "gpt-4.1": {
        "input":  2.00 / 1_000_000,
        "output": 8.00 / 1_000_000,
    },
    "gpt-4.1-mini": {
        "input":  0.40 / 1_000_000,
        "output": 1.60 / 1_000_000,
    },
    "o3": {
        "input":  10.00 / 1_000_000,
        "output": 40.00 / 1_000_000,
    },
    "o4-mini": {
        "input":  1.10 / 1_000_000,
        "output": 4.40 / 1_000_000,
    },
}


# ── Market Data — Alpaca ──────────────────────────────────────────────────────

ALPACA_API_KEY: str    = os.getenv("ALPACA_API_KEY", "")
ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
# Use paper endpoint for dev; switch to live for production
ALPACA_BASE_URL: str   = os.getenv("ALPACA_BASE_URL", "https://paper-api.alpaca.markets")
ALPACA_DATA_URL: str   = os.getenv("ALPACA_DATA_URL", "https://data.alpaca.markets")


# ── Notifications — WhatsApp (Twilio) ─────────────────────────────────────────

TWILIO_ACCOUNT_SID: str  = os.getenv("TWILIO_ACCOUNT_SID", "")
TWILIO_AUTH_TOKEN: str   = os.getenv("TWILIO_AUTH_TOKEN", "")
TWILIO_WHATSAPP_FROM: str = os.getenv("TWILIO_WHATSAPP_FROM", "")   # e.g. whatsapp:+14155238886
TWILIO_WHATSAPP_TO: str  = os.getenv("TWILIO_WHATSAPP_TO", "")     # e.g. whatsapp:+1XXXXXXXXXX
WHATSAPP_NOTIFICATIONS_ENABLED: bool = (
    os.getenv("WHATSAPP_NOTIFICATIONS_ENABLED", "false").lower() == "true"
)


# ── Model Assignments ─────────────────────────────────────────────────────────
# Locked decisions — update BIG_PICTURE.md and decision log before changing.

# Claude models
MANAGER_MODEL: str              = os.getenv("MANAGER_MODEL",              "claude-opus-4-7")
FUNDAMENTAL_ANALYST_MODEL: str  = os.getenv("FUNDAMENTAL_ANALYST_MODEL",  "claude-opus-4-7")
BUSINESS_ANALYST_MODEL: str     = os.getenv("BUSINESS_ANALYST_MODEL",     "claude-sonnet-4-6")
DATA_ENGINEER_MODEL: str        = os.getenv("DATA_ENGINEER_MODEL",        "claude-sonnet-4-6")
TECHNICAL_ANALYST_MODEL: str    = os.getenv("TECHNICAL_ANALYST_MODEL",    "claude-sonnet-4-6")
QA_TESTER_MODEL: str            = os.getenv("QA_TESTER_MODEL",            "claude-haiku-4-5-20251001")
PROJECT_COORDINATOR_MODEL: str  = os.getenv("PROJECT_COORDINATOR_MODEL",  "claude-haiku-4-5-20251001")
AI_ANALYST_MODEL: str           = os.getenv("AI_ANALYST_MODEL",           "claude-sonnet-4-6")

# OpenAI models
WORLD_RESEARCHER_MODEL: str     = os.getenv("WORLD_RESEARCHER_MODEL",     "gpt-4.1")


# ── Database ──────────────────────────────────────────────────────────────────

DUCKDB_PATH: str = os.getenv("DUCKDB_PATH", "data/db/project01.duckdb")


# ── Budget Controls ───────────────────────────────────────────────────────────

MAX_COST_PER_REPORT_USD: float      = float(os.getenv("MAX_COST_PER_REPORT_USD",      "0.75"))
DAILY_BUDGET_LIMIT_USD: float       = float(os.getenv("DAILY_BUDGET_LIMIT_USD",       "10.00"))
MAX_TOKENS_PER_AGENT_CALL: int      = int(os.getenv("MAX_TOKENS_PER_AGENT_CALL",      "4096"))
MAX_TOKENS_PER_PIPELINE_RUN: int    = int(os.getenv("MAX_TOKENS_PER_PIPELINE_RUN",    "100000"))


# ── Prompt Caching ────────────────────────────────────────────────────────────

ENABLE_PROMPT_CACHING: bool    = os.getenv("ENABLE_PROMPT_CACHING", "true").lower() == "true"
PROMPT_CACHE_MIN_CHARS: int    = int(os.getenv("PROMPT_CACHE_MIN_CHARS", "1024"))


# ── Prompts ───────────────────────────────────────────────────────────────────

PROMPT_DIR: str = os.getenv("PROMPT_DIR", "")


# ── Data Refresh ──────────────────────────────────────────────────────────────

DATA_REFRESH_CRON: str          = os.getenv("DATA_REFRESH_CRON",          "30 11 * * 1-5")
HISTORY_DAYS: int               = int(os.getenv("HISTORY_DAYS",           "730"))
REPORT_CACHE_TTL_MINUTES: int   = int(os.getenv("REPORT_CACHE_TTL_MINUTES", "60"))
FORCE_DATA_REFRESH: bool        = os.getenv("FORCE_DATA_REFRESH", "false").lower() == "true"


# ── App Settings ──────────────────────────────────────────────────────────────

PORT: int      = int(os.getenv("PORT",      "8501"))
LOG_LEVEL: str = os.getenv("LOG_LEVEL",     "INFO")
APP_ENV: str   = os.getenv("APP_ENV",       "development")
