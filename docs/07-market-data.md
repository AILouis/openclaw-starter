# Market Data Infrastructure

## Overview

The `market-data` project is a shared library and CLI that all agents use as the single source of truth for price data. It was built by Jim and lives at `/mnt/d/eve-projects/market-data/`.

**Golden rule:** All agents use `market_data` for prices. Web search is for NEWS only. Prices always come from the script.

## Usage

### Quick Snapshot (Most Common)

```bash
cd /mnt/d/eve-projects/market-data && python3 -m market_data --snapshot --format telegram
```

This outputs current prices for all tracked instruments in a compact format suitable for Discord/Telegram.

### Available Modes

| Mode | Flag | Description |
|------|------|-------------|
| Snapshot | `--snapshot` | Current prices for all instruments |
| History | `--history` | Historical price data |
| Telegram format | `--format telegram` | Compact output for messaging |

## Data Sources (Fallback Chain)

The script tries sources in order:

1. **yfinance** — Primary source (Yahoo Finance)
2. **FRED** — Federal Reserve Economic Data (for rates, economic indicators)
3. **Static** — Hardcoded fallback values
4. **N/A** — If all sources fail

## Storage

- SQLite database for caching and historical data
- Located within the `market-data/` project directory

## Instruments Tracked

Jesse's scans include these key levels:
- Brent, WTI (oil)
- 10Y UST, 2Y UST (US Treasuries)
- Gold
- DXY (dollar index)
- USDCNH (offshore yuan)
- USDJPY
- EURUSD
- SPX (S&P 500)
- BTC (Bitcoin)
- 10Y JGB (Japan government bond)
- VIX

## Test Status

60/60 tests passing as of the last build.

## What Happens When the Script Fails

If `market_data` fails or times out during a Jesse scan:

1. Jesse does NOT fall back to web search for prices
2. Jesse notes the failure: "Market data script unavailable -- price levels omitted this scan."
3. Jesse skips the entire price/levels section
4. Jesse flags the issue to Eve for investigation

**Stale or unverified prices are more dangerous than no prices.** This is a non-negotiable rule.

## Related Project: Market Regime Detection

**Location:** `/mnt/d/eve-projects/Market_Regime_Detection/`

This is Louis's main regime detection framework, built and maintained by Jim:
- Python-based HMM model (replaced earlier GMM approach)
- Walk-forward validation
- Multi-layer regime classification (L1: macro, L2: volatility, L3: risk)
- Ongoing research project

## For Developers

The market-data project structure:
```
/mnt/d/eve-projects/market-data/
├── market_data/          # Python package
│   ├── __main__.py       # CLI entry point
│   └── ...               # Library modules
├── tests/                # Test suite (60 tests)
├── README.md
└── CLAUDE.md             # Development notes
```
