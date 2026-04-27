"""
data/schema.py
Phase 4 — PostgreSQL schema (Railway managed Postgres).

Not active in Phase 3. Wire in psycopg2 / SQLAlchemy when Phase 4 ships.

Tables planned:
  analysis_runs        — Master record per analysis session
  analysis_results     — Each agent's output per run
  analysis_cache       — Same-day deduplication (ticker + date)
  stock_prices         — Daily OHLCV
  stock_fundamentals   — Company profile + financials snapshot
  api_usage            — Token-level cost tracking
  agent_logs           — Daily agent report
  communication_log    — Inter-agent messages
  escalation_alerts    — Failure escalation records
  agent_registry       — Agent config source of truth
  learning_log         — Continuous learning entries
  weekly_universe      — Curated 20 stocks/week
  stock_requests       — User-submitted ticker requests
  signal_history       — Signal change audit trail

Views:
  v_cost_daily_summary
  v_cost_by_agent
  v_budget_tracker

See docs/ for full DDL when Phase 4 begins.
"""
