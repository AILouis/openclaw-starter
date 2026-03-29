#!/usr/bin/env python3
"""
Thin wrapper around eqt-report-generator's orchestrator.generate_report().
JSON stdout, PID guard, subprocess timeout, model validation.
"""

import argparse
import json
import os
import sys
import time
import fcntl
from pathlib import Path
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeout

# ── Paths (relative to skill dir) ────────────────────────────────
SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
DATA_DIR = SKILL_DIR / "data"
REPO_DIR = DATA_DIR / "eqt-report-generator"
REPORTS_DIR = DATA_DIR / "reports"
PID_FILE = DATA_DIR / "run_report.pid"
KEY_FILE = REPO_DIR / "key.txt"

DEFAULT_MODEL = "anthropic/claude-3.5-haiku:online"
TIMEOUT_SECONDS = 300  # 5 minutes


def emit(obj: dict):
    """Print JSON to stdout and exit."""
    print(json.dumps(obj), flush=True)
    sys.exit(0 if obj.get("ok") else 1)


def resolve_api_key() -> str:
    """Resolve API key: env var → key.txt. No hardcoded fallback."""
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if key:
        return key
    try:
        key = KEY_FILE.read_text().strip()
        if key:
            return key
    except FileNotFoundError:
        pass
    return ""


class PidGuard:
    """Prevent concurrent runs via PID file with flock."""

    def __init__(self, pid_path: Path):
        self.pid_path = pid_path
        self.fd = None

    def acquire(self):
        self.pid_path.parent.mkdir(parents=True, exist_ok=True)
        self.fd = open(self.pid_path, "w")
        try:
            fcntl.flock(self.fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (IOError, OSError):
            self.fd.close()
            self.fd = None
            return False
        self.fd.write(str(os.getpid()))
        self.fd.flush()
        return True

    def release(self):
        if self.fd:
            try:
                fcntl.flock(self.fd, fcntl.LOCK_UN)
                self.fd.close()
            except Exception:
                pass
            try:
                self.pid_path.unlink()
            except FileNotFoundError:
                pass
            self.fd = None


def main():
    parser = argparse.ArgumentParser(description="Generate equity research report")
    parser.add_argument("--ticker", "-t", required=True, help="Stock ticker (e.g. NVDA, 0700 HK, SHEL LN)")
    parser.add_argument("--model", "-m", default=DEFAULT_MODEL, help=f"OpenRouter model (default: {DEFAULT_MODEL})")
    parser.add_argument("--dry-run", action="store_true", help="Validate inputs only, don't generate")
    args = parser.parse_args()

    ticker = args.ticker.strip()
    if not ticker:
        emit({"ok": False, "error": "Ticker is required"})

    model = args.model

    # Verify setup
    if not REPO_DIR.is_dir():
        emit({"ok": False, "error": f"Repo not found at {REPO_DIR}. Run setup.sh first."})
    if not (DATA_DIR / "venv" / "bin" / "python").is_file():
        emit({"ok": False, "error": "Venv not found. Run setup.sh first."})

    api_key = resolve_api_key()
    if not api_key:
        emit({"ok": False, "error": "No API key found. Set OPENROUTER_API_KEY env var or write key to data/eqt-report-generator/key.txt"})

    # Add repo to sys.path for imports
    repo_str = str(REPO_DIR)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)

    # Set API key in environment so the repo's config can pick it up
    os.environ["OPENROUTER_API_KEY"] = api_key

    # Import after sys.path modification
    try:
        from orchestrator import generate_report
        from ticker_resolver import resolve_ticker
    except ImportError as e:
        emit({"ok": False, "error": f"Import failed (deps installed?): {e}"})

    # Resolve ticker — fail explicitly if not found
    try:
        resolved_ticker, company_name = resolve_ticker(ticker)
    except Exception as e:
        emit({"ok": False, "error": f"Ticker resolution failed for '{ticker}': {e}"})

    if not company_name:
        # Warn but continue — some valid tickers don't resolve to a name
        print(json.dumps({"warning": f"Could not resolve company name for '{resolved_ticker}'. Proceeding anyway."}),
              file=sys.stderr, flush=True)

    if args.dry_run:
        emit({"ok": True, "dry_run": True, "ticker": resolved_ticker,
              "company": company_name or None, "model": model})

    # Prepare output directory
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    report_dir = REPORTS_DIR / date_str / resolved_ticker
    report_dir.mkdir(parents=True, exist_ok=True)
    time_str = now.strftime("%H%M")
    output_path = str(report_dir / f"{resolved_ticker}_Report_{date_str}_{time_str}.pdf")

    # Acquire PID lock (manual, not context manager — safer with threads)
    guard = PidGuard(PID_FILE)
    if not guard.acquire():
        emit({"ok": False, "error": "Another report is already running (PID lock held)"})

    # Run with thread-based timeout (safe with ThreadPoolExecutor inside generate_report)
    start = time.time()
    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                generate_report,
                ticker=resolved_ticker,
                api_key=api_key,
                output_path=output_path,
                model=model,
            )
            try:
                result_path = future.result(timeout=TIMEOUT_SECONDS)
            except FuturesTimeout:
                guard.release()
                emit({"ok": False, "error": f"Report generation timed out after {TIMEOUT_SECONDS}s"})
    except Exception as e:
        guard.release()
        emit({"ok": False, "error": str(e)})

    guard.release()
    elapsed = round(time.time() - start, 1)

    emit({
        "ok": True,
        "ticker": resolved_ticker,
        "company": company_name or None,
        "pdf": result_path,
        "seconds": elapsed,
    })


if __name__ == "__main__":
    main()
