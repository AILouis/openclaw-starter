"""Load and validate methodology.yaml configuration."""

import os
import yaml

def load_config(config_path=None):
    """Load methodology config from YAML file."""
    if config_path is None:
        skill_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        config_path = os.path.join(skill_dir, "config", "methodology.yaml")
    
    with open(config_path, "r") as f:
        cfg = yaml.safe_load(f)
    
    # Validate pillar weights sum to ~1.0
    total = sum(p["weight"] for p in cfg["pillars"].values())
    if abs(total - 1.0) > 0.01:
        raise ValueError(f"Pillar weights sum to {total}, expected ~1.0")
    
    # Validate signal weights within each pillar sum to ~1.0
    for pname, pillar in cfg["pillars"].items():
        sig_total = sum(s["weight"] for s in pillar["signals"])
        if abs(sig_total - 1.0) > 0.01:
            raise ValueError(f"Signal weights in {pname} sum to {sig_total}, expected ~1.0")
    
    return cfg


def get_fred_api_key():
    """Get FRED API key from env or file."""
    key = os.environ.get("FRED_API_KEY")
    if key:
        return key
    
    skill_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    key_file = os.path.join(skill_dir, "data", "fred_key.txt")
    if os.path.exists(key_file):
        with open(key_file, "r") as f:
            return f.read().strip()
    
    return None
