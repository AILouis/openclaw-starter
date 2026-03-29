"""Pillar aggregation and composite PCSI calculation."""

import logging
from datetime import datetime, timedelta

logger = logging.getLogger("pcsi.index")


def check_staleness(last_updated_str, source, staleness_cfg):
    """Check if a signal's data is stale. Returns True if stale."""
    if not last_updated_str:
        return True
    
    try:
        last_dt = datetime.strptime(last_updated_str, "%Y-%m-%d")
    except ValueError:
        return True
    
    now = datetime.now()
    days_old = (now - last_dt).days
    
    if source in ("fred", "fred_computed"):
        return days_old > staleness_cfg.get("fred_max_days", 45)
    else:
        return days_old > staleness_cfg.get("daily_max_days", 7)


def compute_pillar_score(signal_results, staleness_cfg):
    """Compute weighted average score for a pillar.
    
    signal_results: list of dicts with keys: name, score, weight, last_updated, source
    
    Returns: (pillar_score, adjusted_signal_results)
    """
    # Separate available vs unavailable
    available = []
    unavailable = []
    
    for sr in signal_results:
        if sr["score"] is not None:
            stale = check_staleness(sr["last_updated"], sr["source"], staleness_cfg)
            sr["stale"] = stale
            effective_weight = sr["weight"] * 0.5 if stale else sr["weight"]
            sr["effective_weight"] = effective_weight
            available.append(sr)
        else:
            sr["stale"] = True
            sr["effective_weight"] = 0
            unavailable.append(sr)
    
    if not available:
        return None, signal_results
    
    # Normalize weights
    total_weight = sum(s["effective_weight"] for s in available)
    if total_weight == 0:
        return None, signal_results
    
    pillar_score = sum(
        s["score"] * (s["effective_weight"] / total_weight)
        for s in available
    )
    
    return round(pillar_score, 2), signal_results


def compute_pcsi(pillar_scores, pillar_weights):
    """Compute composite PCSI from pillar scores.
    
    pillar_scores: dict of pillar_name -> score (or None)
    pillar_weights: dict of pillar_name -> weight
    
    Returns: float 0-100 or None
    """
    available = {k: v for k, v in pillar_scores.items() if v is not None}
    
    if len(available) == 0:
        return None
    
    # Check >50% availability by weight
    available_weight = sum(pillar_weights[k] for k in available)
    if available_weight < 0.5:
        return None
    
    # Normalize and compute
    total = sum(pillar_weights[k] for k in available)
    pcsi = sum(
        score * (pillar_weights[k] / total)
        for k, score in available.items()
    )
    
    return round(pcsi, 2)


def get_label(pcsi, bands):
    """Get interpretation label for a PCSI value."""
    if pcsi is None:
        return "N/A"
    for band in bands:
        if band["min"] <= pcsi <= band["max"]:
            return band["label"]
    return "N/A"


def get_band_color(pcsi, bands):
    """Get color for a PCSI value."""
    if pcsi is None:
        return "#999"
    for band in bands:
        if band["min"] <= pcsi <= band["max"]:
            return band["color"]
    return "#999"
