#!/usr/bin/env python3
"""PCSI — Private Credit Sentiment Index
Main entry point: fetch data, compute index, generate dashboard.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime

# Ensure lib is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lib.config import load_config
from lib.data_pipeline import fetch_signal_data
from lib.signals import percentile_score, apply_polarity
from lib.index import compute_pillar_score, compute_pcsi, get_label, get_band_color
from lib.storage import init_db, save_pcsi, get_history, get_previous_pcsi
from lib.dashboard import generate_dashboard

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("pcsi")


def _pid_guard(skill_dir):
    """Simple PID file guard to prevent concurrent runs."""
    pid_file = os.path.join(skill_dir, "data", ".pcsi.pid")
    if os.path.exists(pid_file):
        try:
            with open(pid_file) as f:
                old_pid = int(f.read().strip())
            # Check if process is still running
            os.kill(old_pid, 0)
            logger.error(f"Another PCSI instance is running (PID {old_pid})")
            sys.exit(1)
        except (ProcessLookupError, ValueError):
            pass  # stale pid file
    
    with open(pid_file, "w") as f:
        f.write(str(os.getpid()))
    
    return pid_file


def main():
    parser = argparse.ArgumentParser(description="PCSI — Private Credit Sentiment Index")
    parser.add_argument("--config", default=None, help="Path to methodology.yaml")
    parser.add_argument("--output-dir", default=None, help="Output directory for dashboard")
    parser.add_argument("--dry-run", action="store_true", help="Validate data fetching only")
    args = parser.parse_args()

    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # PID guard
    pid_file = _pid_guard(skill_dir)
    
    try:
        _run(args, skill_dir)
    finally:
        if os.path.exists(pid_file):
            os.remove(pid_file)


def _run(args, skill_dir):
    # Load config
    config_path = args.config
    if config_path is None:
        config_path = os.path.join(skill_dir, "config", "methodology.yaml")
    
    cfg = load_config(config_path)
    lookback = cfg["lookback_days"]
    staleness_cfg = cfg["staleness"]
    bands = cfg["bands"]
    
    output_dir = args.output_dir
    if output_dir is None:
        output_dir = os.path.join(skill_dir, "data", "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Init storage
    init_db(skill_dir)
    
    # Fetch and score all signals
    all_signal_details = []
    pillar_scores = {}
    pillar_weights = {}
    total_signals = 0
    available_signals = 0
    
    for pillar_name, pillar_cfg in cfg["pillars"].items():
        pillar_weights[pillar_name] = pillar_cfg["weight"]
        signal_results = []
        
        for sig_cfg in pillar_cfg["signals"]:
            total_signals += 1
            name = sig_cfg["name"]
            logger.info(f"Fetching: {name}")
            
            series, last_updated = fetch_signal_data(sig_cfg, lookback, skill_dir)
            
            if series is not None and len(series) > 0:
                current_value = float(series.iloc[-1])
                raw_pctile = percentile_score(series, lookback)
                score = apply_polarity(raw_pctile, sig_cfg["polarity"])
                available_signals += 1
            else:
                current_value = None
                score = None
                logger.warning(f"No data available for {name}")
            
            result = {
                "name": name,
                "score": score,
                "weight": sig_cfg["weight"],
                "last_updated": last_updated,
                "source": sig_cfg["source"],
                "current_value": current_value,
                "polarity": sig_cfg["polarity"],
            }
            signal_results.append(result)
            all_signal_details.append(result)
        
        # Compute pillar score
        p_score, signal_results = compute_pillar_score(signal_results, staleness_cfg)
        pillar_scores[pillar_name] = p_score
        logger.info(f"Pillar {pillar_name}: {p_score}")
    
    # Check availability threshold
    if available_signals / max(total_signals, 1) < 0.5:
        error_result = {
            "ok": False,
            "error": f"Insufficient data: only {available_signals}/{total_signals} signals available",
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        print(json.dumps(error_result))
        sys.exit(1)
    
    # Compute composite
    pcsi = compute_pcsi(pillar_scores, pillar_weights)
    label = get_label(pcsi, bands)
    
    if pcsi is None:
        error_result = {
            "ok": False,
            "error": "Could not compute PCSI — insufficient pillar data",
            "date": datetime.now().strftime("%Y-%m-%d"),
        }
        print(json.dumps(error_result))
        sys.exit(1)
    
    # Delta from previous
    prev = get_previous_pcsi(skill_dir)
    delta_1d = round(pcsi - prev, 2) if prev is not None else None
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    if args.dry_run:
        result = {
            "ok": True,
            "dry_run": True,
            "pcsi": pcsi,
            "label": label,
            "delta_1d": delta_1d,
            "pillar_scores": pillar_scores,
            "signals_available": available_signals,
            "signals_total": total_signals,
            "date": date_str,
        }
        print(json.dumps(result, indent=2))
        return
    
    # Save to history
    save_pcsi(
        skill_dir, date_str, pcsi, label,
        pillar_scores,
        [{"name": s["name"], "score": s["score"], "current_value": s["current_value"]}
         for s in all_signal_details],
    )
    
    # Get history for chart
    history = get_history(skill_dir, days=30)
    
    # Generate dashboard
    dashboard_path = os.path.join(output_dir, "pcsi_dashboard.html")
    generate_dashboard(
        pcsi, label, delta_1d,
        pillar_scores, all_signal_details,
        history, bands, dashboard_path,
    )
    
    result = {
        "ok": True,
        "pcsi": pcsi,
        "label": label,
        "delta_1d": delta_1d,
        "dashboard": dashboard_path,
        "date": date_str,
    }
    print(json.dumps(result))
    logger.info(f"PCSI = {pcsi} ({label}) | Dashboard: {dashboard_path}")


if __name__ == "__main__":
    main()
