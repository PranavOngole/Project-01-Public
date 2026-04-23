# Project-01 | AI-Powered Stock Research Platform

> **Pranav Ongole's Vision** — Build the research desk I always wanted: one that never sleeps,
> never misses a filing, and delivers institutional-grade conviction scores to any investor
> in under 60 seconds.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![Powered by Claude](https://img.shields.io/badge/AI-Claude%20Opus%204.7-orange)](https://anthropic.com)
[![Powered by OpenAI](https://img.shields.io/badge/AI-GPT--4.1-412991)](https://openai.com)
[![Part of POV Series](https://img.shields.io/badge/Series-Pranav%20Ongole's%20Vision%20(POV)-blueviolet)](https://github.com/PranavOngole/Project-00)

---

## What This Platform Does

Project-01 is a **single-stock, deep-analysis engine**. Enter a ticker; receive a comprehensive
research report in seconds — the kind that would take a junior analyst half a day to assemble.

| Capability | Description |
|---|---|
| **Value Conviction Score** | Proprietary 0–100 composite score weighing fundamentals, technicals, sentiment, and competitive position |
| **Purchase Price Recommendation** | Agent-derived fair-value range with entry, target, and stop-loss levels |
| **World Research Context** | Real-time news, SEC filings, analyst estimates, insider moves, and upcoming catalysts gathered before the financial verdict |
| **Fundamental Deep Dive** | Revenue trends, margins, balance sheet health, FCF, earnings quality, and ratio benchmarking |
| **WhatsApp Notifications** | Push alerts when analysis completes, signals change, or budget thresholds are hit |
| **QA-Validated Output** | Every report passes a dedicated QA agent before it reaches the UI |

---

## How It Works

```
User enters ticker
        │
        ▼
┌───────────────────────────────────────┐
│  World Researcher (WR-01)             │
│  OpenAI GPT-4.1                       │
│                                       │
│  Gathers everything real-world:       │
│  • News (last 30 days)                │
│  • Earnings call highlights           │
│  • SEC filing summaries               │
│  • Insider transactions               │
│  • Macro + sector context             │
│  • Upcoming catalysts                 │
│                                       │
│  → Deposits research packet to DB     │
└──────────────────┬────────────────────┘
                   │
                   ▼
┌───────────────────────────────────────┐
│  Fundamental Analyst (FA-01)          │
│  Claude Opus 4.7                      │
│                                       │
│  Step 1: Independent financial        │
│    analysis — financials only,        │
│    no world context yet               │
│                                       │
│  Step 2: Reads WR-01 research packet  │
│    Adjusts conviction only if world   │
│    context materially changes thesis  │
│                                       │
│  → Issues final report:               │
│    Signal · VCS Score · Buy Price     │
└──────────────────┬────────────────────┘
                   │
                   ▼
           Report displayed
           WhatsApp notification sent
```

**Why this order?** FA-01 forms its financial view first (preventing anchoring bias from headlines),
then stress-tests it against real-world context. If fundamentals say BUY but World Researcher found
an SEC investigation, FA-01 revises down.

---

## Current Build Status

```
Phase 1: Planning          ✅ COMPLETE
Phase 2: Architecture      ✅ COMPLETE
Phase 3: Infrastructure    🔨 IN PROGRESS
Phase 4: Agents            🔨 IN PROGRESS  ← Baby Steps: WR-01 + FA-01 first
Phase 5: Integration       ⬜ NOT STARTED
Phase 6: Launch            ⬜ NOT STARTED
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| AI — Conviction Engine | [Claude Opus 4.7](https://anthropic.com) | Fundamental Analyst (FA-01) |
| AI — World Research | [OpenAI GPT-4.1](https://openai.com) | World Researcher (WR-01) |
| Market Data | [Alpaca API](https://alpaca.markets) | Real-time + historical price data |
| Notifications | [Twilio WhatsApp](https://twilio.com) | Push alerts on analysis events |
| Frontend | [Streamlit](https://streamlit.io) | Interactive web UI |
| Charts | [Plotly](https://plotly.com/python/) | Interactive price charts |
| Database | [DuckDB](https://duckdb.org) | Embedded analytical DB — caching + logs |
| Deployment | [Railway](https://railway.app) | Zero-config cloud hosting |
| Scheduler | [n8n](https://n8n.io) | Automated data refresh + alert workflows |

---

## Agent Roster

| ID | Agent | Brain | Role | Status |
|---|---|---|---|---|
| WR-01 | World Researcher | GPT-4.1 | Real-world context gathering | ✅ Built |
| FA-01 | Fundamental Analyst | Claude Opus 4.7 | Conviction engine — VCS + purchase price | ✅ Built |
| MGR-01 | Manager | Claude Opus 4.7 | Orchestration, conflict resolution | 🔜 Next |
| TA-01 | Technical Analyst | TBD | Chart reading, indicators, entry timing | Planned |
| BA-01 | Business Analyst | Claude Sonnet | Competitive positioning, moat analysis | Planned |
| DE-01 | Data Engineer | Python + Alpaca | Raw data pipeline | Planned |
| QA-01 | QA Tester | Python | Data validation, hallucination detection | Planned |
| PM-01 | Project Manager | Claude Haiku | Report assembly | Planned |
| AIA-01 | AI Analyst | Python | Cost tracking, budget alerts | Planned |

> Agent system prompts are loaded from environment variables at runtime and are **not stored in this repository**.

---

## Project Structure

```
Project-01/
│
├── app/                          # Streamlit application
│   ├── main.py                   # Entry point, sidebar, session state
│   └── pages/                    # Multi-page app sections
│
├── agents/                       # Agent definitions (prompts via env)
│   ├── base_agent.py             # Shared Claude API wrapper, token tracking, retry
│   ├── world_researcher.py       # WR-01 — OpenAI, real-world context
│   ├── fundamental_analyst.py    # FA-01 — Claude Opus 4.7, conviction engine
│   ├── manager.py                # MGR-01 — orchestrator (scaffold)
│   └── data_engineer.py          # DE-01 — data pipeline (scaffold)
│
├── data/                         # Data layer
│   ├── pipeline.py               # Fetch → validate → cache orchestration
│   ├── schema.py                 # DuckDB table definitions (incl. world_research)
│   └── cache.py                  # Cache read/write helpers
│
├── config/
│   ├── settings.py               # All env vars: Anthropic, OpenAI, Alpaca, Twilio
│   ├── ticker_universe.py        # NYSE/NASDAQ universe filters
│   └── prompts.py                # Prompt loader (keys map to private repo files)
│
├── .env.example                  # Required environment variables (template)
└── requirements.txt              # anthropic, openai, alpaca-py, twilio, duckdb, ...
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in:

```
# AI
ANTHROPIC_API_KEY=
OPENAI_API_KEY=

# Market Data
ALPACA_API_KEY=
ALPACA_SECRET_KEY=

# Notifications
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+1XXXXXXXXXX
WHATSAPP_NOTIFICATIONS_ENABLED=false

# Prompts (point to private repo locally)
PROMPT_DIR=/path/to/Project-01-Private/prompts
```

---

## Stock Universe

Analysis is scoped to **NYSE and NASDAQ-listed equities** meeting all of the following criteria:

- Market capitalisation **>= $500M** (mid-cap and above)
- Minimum **2 years** of continuous price history
- Active trading status (no OTC, pink sheets, or shell companies)

ADRs, ETFs, SPACs, and preferred shares are excluded from the default universe.

---

## Part of Pranav Ongole's Vision (POV) Series

This project is **Project-01** in a year-long, public build series.

| # | Project | Status |
|---|---|---|
| 00 | [POV Series — Kickoff & Manifesto](https://github.com/PranavOngole/Project-00) | Complete |
| 01 | AI-Powered Stock Research Platform | **In Progress** |
| 02–12 | Coming throughout 2026 | Planned |

---

## License

Distributed under the [MIT License](LICENSE). You are free to fork, adapt, and build on this work
with attribution.

---

## SEC Disclaimer

> **This platform is for informational and educational purposes only.**
> Nothing produced by Project-01 — including the Value Conviction Score, purchase price
> recommendations, or any analysis output — constitutes financial advice, investment advice,
> or a recommendation to buy or sell any security. Always conduct your own due diligence and
> consult a qualified financial professional before making investment decisions.
> Past performance of any stock referenced is not indicative of future results.
