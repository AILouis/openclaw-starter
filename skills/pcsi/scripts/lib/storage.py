"""SQLite storage for historical PCSI values."""

import os
import sqlite3
import json
from datetime import datetime


def _db_path(skill_dir):
    return os.path.join(skill_dir, "data", "history.db")


def init_db(skill_dir):
    """Create tables if they don't exist."""
    db = _db_path(skill_dir)
    os.makedirs(os.path.dirname(db), exist_ok=True)
    conn = sqlite3.connect(db)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS pcsi_history (
            date TEXT PRIMARY KEY,
            pcsi REAL,
            label TEXT,
            pillar_scores TEXT,
            signal_details TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    conn.close()


def save_pcsi(skill_dir, date_str, pcsi, label, pillar_scores, signal_details):
    """Save or update a PCSI record."""
    db = _db_path(skill_dir)
    conn = sqlite3.connect(db)
    conn.execute("""
        INSERT OR REPLACE INTO pcsi_history (date, pcsi, label, pillar_scores, signal_details, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        date_str,
        pcsi,
        label,
        json.dumps(pillar_scores),
        json.dumps(signal_details),
        datetime.now().isoformat(),
    ))
    conn.commit()
    conn.close()


def get_history(skill_dir, days=30):
    """Get last N days of PCSI history."""
    db = _db_path(skill_dir)
    if not os.path.exists(db):
        return []
    conn = sqlite3.connect(db)
    rows = conn.execute(
        "SELECT date, pcsi, label FROM pcsi_history ORDER BY date DESC LIMIT ?",
        (days,)
    ).fetchall()
    conn.close()
    return [{"date": r[0], "pcsi": r[1], "label": r[2]} for r in reversed(rows)]


def get_previous_pcsi(skill_dir):
    """Get yesterday's PCSI value for delta calculation."""
    db = _db_path(skill_dir)
    if not os.path.exists(db):
        return None
    conn = sqlite3.connect(db)
    rows = conn.execute(
        "SELECT pcsi FROM pcsi_history ORDER BY date DESC LIMIT 2"
    ).fetchall()
    conn.close()
    if len(rows) >= 2:
        return rows[1][0]
    return None
