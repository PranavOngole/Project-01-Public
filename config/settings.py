"""
config/settings.py

Loads environment variables. All keys and model assignments are configured
via environment variables — nothing is hardcoded here.

Copy .env.example to .env and fill in values before running.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

# AI provider keys
ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY:    str = os.getenv("OPENAI_API_KEY",    "")

# Market data
ALPACA_API_KEY:    str = os.getenv("ALPACA_API_KEY",    "")
ALPACA_SECRET_KEY: str = os.getenv("ALPACA_SECRET_KEY", "")
ALPACA_BASE_URL:   str = os.getenv("ALPACA_BASE_URL",   "https://paper-api.alpaca.markets")
ALPACA_DATA_URL:   str = os.getenv("ALPACA_DATA_URL",   "https://data.alpaca.markets")

# Notifications
TWILIO_ACCOUNT_SID:   str = os.getenv("TWILIO_ACCOUNT_SID",   "")
TWILIO_AUTH_TOKEN:    str = os.getenv("TWILIO_AUTH_TOKEN",     "")
TWILIO_WHATSAPP_FROM: str = os.getenv("TWILIO_WHATSAPP_FROM",  "")
TWILIO_WHATSAPP_TO:   str = os.getenv("TWILIO_WHATSAPP_TO",    "")

# Model assignments (set via environment — not defaulted here)
FUNDAMENTAL_ANALYST_MODEL: str = os.getenv("FUNDAMENTAL_ANALYST_MODEL", "")
WORLD_RESEARCHER_MODEL:    str = os.getenv("WORLD_RESEARCHER_MODEL",    "")
MANAGER_MODEL:             str = os.getenv("MANAGER_MODEL",             "")

# Budget controls
MAX_COST_PER_REPORT_USD:   float = float(os.getenv("MAX_COST_PER_REPORT_USD",  "0.75"))
DAILY_BUDGET_LIMIT_USD:    float = float(os.getenv("DAILY_BUDGET_LIMIT_USD",   "10.00"))

# Prompts
PROMPT_DIR: str = os.getenv("PROMPT_DIR", "")

# App
APP_ENV:   str = os.getenv("APP_ENV",   "development")
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
PORT:      int = int(os.getenv("PORT",  "8501"))
