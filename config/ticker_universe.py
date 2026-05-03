"""
config/ticker_universe.py

Defines the universe of tickers the system is permitted to analyse.
Scoped to NYSE and NASDAQ-listed equities with market cap >= $500M,
minimum 2 years of price history, and active trading status.

ADRs, ETFs, SPACs, and preferred shares are excluded by default.
"""

NYSE_NASDAQ_FILTERS = {
    "min_market_cap_usd":  500_000_000,
    "min_history_years":   2,
    "exchanges":           ["NYSE", "NASDAQ"],
    "exclude_types":       ["ETF", "ADR", "SPAC", "PREFERRED"],
}
