"""Data fetching from yfinance and FRED with caching."""

import os
import json
import time
import logging
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from fredapi import Fred

from .config import get_fred_api_key

logger = logging.getLogger("pcsi.data")

CACHE_EXPIRY_HOURS = 6


def _cache_path(skill_dir, key):
    safe = key.replace("^", "_").replace("/", "_")
    return os.path.join(skill_dir, "data", "cache", f"{safe}.json")


def _read_cache(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as f:
            data = json.load(f)
        cached_at = data.get("cached_at", 0)
        if time.time() - cached_at > CACHE_EXPIRY_HOURS * 3600:
            return None
        return data
    except Exception:
        return None


def _write_cache(path, series_data, last_updated):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    payload = {
        "cached_at": time.time(),
        "last_updated": last_updated,
        "data": series_data,
    }
    with open(path, "w") as f:
        json.dump(payload, f)


def fetch_yfinance(ticker, lookback_days, skill_dir, retries=2):
    """Fetch price history from yfinance. Returns (Series, last_updated_str)."""
    cp = _cache_path(skill_dir, f"yf_{ticker}")
    
    for attempt in range(retries + 1):
        try:
            end = datetime.now()
            start = end - timedelta(days=int(lookback_days * 1.6))  # extra buffer
            t = yf.Ticker(ticker)
            hist = t.history(start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"))
            if hist.empty:
                raise ValueError(f"No data for {ticker}")
            
            close = hist["Close"].dropna()
            last_updated = str(close.index[-1].date())
            
            # Cache it
            cache_data = {str(k.date()): float(v) for k, v in close.items()}
            _write_cache(cp, cache_data, last_updated)
            
            return close, last_updated
        except Exception as e:
            logger.warning(f"yfinance {ticker} attempt {attempt+1} failed: {e}")
            if attempt == retries:
                # Try cache
                cached = _read_cache(cp)
                if cached:
                    logger.info(f"Using cached data for {ticker}")
                    s = pd.Series(cached["data"], dtype=float)
                    s.index = pd.to_datetime(s.index)
                    return s.sort_index(), cached["last_updated"]
                return None, None
            time.sleep(1)


def fetch_fred(series_id, lookback_days, skill_dir, retries=2):
    """Fetch series from FRED. Returns (Series, last_updated_str)."""
    api_key = get_fred_api_key()
    if not api_key:
        logger.error("No FRED API key available")
        return None, None
    
    cp = _cache_path(skill_dir, f"fred_{series_id}")
    
    for attempt in range(retries + 1):
        try:
            fred = Fred(api_key=api_key)
            end = datetime.now()
            start = end - timedelta(days=int(lookback_days * 1.6))
            data = fred.get_series(series_id, observation_start=start, observation_end=end)
            data = data.dropna()
            
            if data.empty:
                raise ValueError(f"No FRED data for {series_id}")
            
            last_updated = str(data.index[-1].date())
            cache_data = {str(k.date()): float(v) for k, v in data.items()}
            _write_cache(cp, cache_data, last_updated)
            
            return data, last_updated
        except Exception as e:
            logger.warning(f"FRED {series_id} attempt {attempt+1} failed: {e}")
            if attempt == retries:
                cached = _read_cache(cp)
                if cached:
                    logger.info(f"Using cached data for {series_id}")
                    s = pd.Series(cached["data"], dtype=float)
                    s.index = pd.to_datetime(s.index)
                    return s.sort_index(), cached["last_updated"]
                return None, None
            time.sleep(1)


def fetch_signal_data(signal_cfg, lookback_days, skill_dir):
    """Fetch data for a single signal config entry.
    
    Returns: (pd.Series, last_updated_str) or (None, None) on failure.
    """
    source = signal_cfg["source"]
    
    if source == "yfinance":
        return fetch_yfinance(signal_cfg["ticker"], lookback_days, skill_dir)
    
    elif source == "fred":
        return fetch_fred(signal_cfg["series"], lookback_days, skill_dir)
    
    elif source == "fred_computed":
        # Fetch two series and compute
        s_a, lu_a = fetch_fred(signal_cfg["series_a"], lookback_days, skill_dir)
        s_b, lu_b = fetch_fred(signal_cfg["series_b"], lookback_days, skill_dir)
        
        if s_a is None or s_b is None:
            return None, None
        
        # Align on common dates
        common = s_a.index.intersection(s_b.index)
        if len(common) == 0:
            return None, None
        
        op = signal_cfg.get("operation", "subtract")
        if op == "subtract":
            result = s_a[common] - s_b[common]
        else:
            result = s_a[common]
        
        last_updated = max(lu_a or "", lu_b or "")
        return result.dropna(), last_updated
    
    else:
        logger.error(f"Unknown source: {source}")
        return None, None
