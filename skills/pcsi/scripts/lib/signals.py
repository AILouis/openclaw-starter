"""Signal normalization using percentile rank."""

import numpy as np
from scipy import stats


def percentile_score(series, lookback_days=504):
    """Compute percentile rank of the latest value over the lookback window.
    
    Returns: float 0-100, or None if insufficient data.
    """
    if series is None or len(series) == 0:
        return None
    
    # Use the last `lookback_days` observations
    window = series.iloc[-lookback_days:]
    if len(window) < 20:  # minimum viable window
        return None
    
    latest = window.iloc[-1]
    # Percentile rank: what % of the window is <= latest value
    rank = stats.percentileofscore(window.values, latest, kind="rank")
    return round(rank, 2)


def apply_polarity(score, polarity):
    """Apply polarity to a percentile score.
    
    polarity +1: higher raw value = more bullish → keep score
    polarity -1: higher raw value = more bearish → flip score
    """
    if score is None:
        return None
    if polarity == -1:
        return round(100.0 - score, 2)
    return score
