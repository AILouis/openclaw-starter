---
name: pcsi
version: 1.0.0
description: "Private Credit Sentiment Index — composite 0-100 index from 10 credit, flow, and macro signals"
triggers:
  - pcsi
  - private credit
  - credit sentiment
  - credit index
---

# PCSI — Private Credit Sentiment Index

Composite sentiment index (0–100) built from 10 signals across three pillars:
Credit Spreads (35%), Credit Flows (30%), Macro Environment (35%).

## Human Setup

1. **Prerequisites**: Linux or macOS, Python 3.10+, git
2. **FRED API Key**: Set `FRED_API_KEY` environment variable, or place your key in `data/fred_key.txt`
3. **Run setup**: `bash scripts/setup.sh` — creates venv and installs dependencies
4. **Run index**: `data/venv/bin/python scripts/run_pcsi.py`
5. **View dashboard**: Open `data/output/pcsi_dashboard.html` in a browser

### Configuration

Edit `config/methodology.yaml` to adjust pillar weights, signal weights, lookback windows, and staleness thresholds.

## Agent Usage

```bash
SKILL_DIR="$HOME/.openclaw/workspace/skills/pcsi"

# First-time setup (idempotent)
bash "$SKILL_DIR/scripts/setup.sh"

# Run the index
"$SKILL_DIR/data/venv/bin/python" "$SKILL_DIR/scripts/run_pcsi.py"

# Dry run (validate data fetching, no dashboard)
"$SKILL_DIR/data/venv/bin/python" "$SKILL_DIR/scripts/run_pcsi.py" --dry-run
```

### Output

JSON to stdout on completion:
```json
{"ok": true, "pcsi": 62.4, "label": "Bullish", "delta_1d": 3.1, "dashboard": "/path/to/dashboard.html", "date": "2026-03-28"}
```

### Interpretation Bands

| Range   | Label         |
|---------|---------------|
| 80–100  | Very Bullish  |
| 60–80   | Bullish       |
| 40–60   | Neutral       |
| 20–40   | Bearish       |
| 0–20    | Very Bearish  |

### Dependencies

yfinance, fredapi, matplotlib, pandas, numpy, scipy
