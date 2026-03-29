---
name: eqt-report
description: Generate multi-agent equity research PDF reports via OpenRouter. Wraps github.com/AILouis/eqt-report-generator.
---

# eqt-report

Generate investment research reports for any publicly traded stock. Five specialized AI agents (technical, macro, flow, narrative, fundamental) run in parallel via OpenRouter, a CIO agent synthesizes their output, and the result is a formatted PDF.

## Human Setup (one-time)

### Prerequisites

- Linux or macOS (uses Unix-specific APIs)
- Python 3.10+ installed and available as `python3`
- Git installed
- Internet access (clones repo, calls OpenRouter API)
- An OpenRouter API key (https://openrouter.ai/keys)

### Installation

```bash
export OPENROUTER_API_KEY="sk-or-..."
cd ~/.openclaw/workspace/skills/eqt-report
bash scripts/setup.sh
```

Setup is idempotent — safe to re-run. It clones the upstream repo, creates a Python venv, installs dependencies, and writes the API key to `data/eqt-report-generator/key.txt`.

To use a different API key later, either:
- Edit `data/eqt-report-generator/key.txt`, or
- Set the `OPENROUTER_API_KEY` environment variable

## Agent Usage

### When to use

User asks for an equity research report, stock analysis PDF, or investment report for a ticker.

### How to run

```bash
SKILL_DIR="$HOME/.openclaw/workspace/skills/eqt-report"
"$SKILL_DIR/data/venv/bin/python" "$SKILL_DIR/scripts/run_report.py" --ticker NVDA
```

Optional flags:
- `--model <openrouter-model-id>` (default: `anthropic/claude-3.5-haiku:online`)
- `--dry-run` validates inputs without generating (useful for checking ticker resolution)

Available models:
- `anthropic/claude-3.5-haiku:online` (default, fast + cheap)
- `google/gemini-2.5-flash:online`
- `openai/gpt-4o-mini:online`
- `deepseek/deepseek-chat:online`

### Output

JSON on stdout:
- Success: `{"ok": true, "ticker": "NVDA", "company": "NVIDIA Corp", "pdf": "/absolute/path/to/report.pdf", "seconds": 142}`
- Failure: `{"ok": false, "error": "description"}`

PDF reports are saved under `data/reports/<YYYYMMDD>/<TICKER>/`.

### Timing

A full report takes 2–4 minutes depending on model and network. Each run costs a few cents in OpenRouter credits.

### Concurrency

Only one report runs at a time (PID file guard). If a run is already in progress, the script exits with an error JSON.

### Troubleshooting

- **Missing venv**: Run `bash scripts/setup.sh` again
- **API key errors**: Check `data/eqt-report-generator/key.txt` or set `OPENROUTER_API_KEY`
- **Import errors**: Re-run setup.sh to reinstall deps
- **Stale PID lock**: Delete `data/run_report.pid` if a previous run crashed
