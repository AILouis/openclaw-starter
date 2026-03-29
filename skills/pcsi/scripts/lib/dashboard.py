"""HTML dashboard generation with embedded matplotlib charts."""

import io
import base64
from datetime import datetime

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np


def _fig_to_base64(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=120, bbox_inches="tight", facecolor="#1a1a2e")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")


def _make_trend_chart(history, bands):
    """30-day trend line chart with colored band zones."""
    fig, ax = plt.subplots(figsize=(10, 4))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    
    if history:
        dates = [h["date"] for h in history]
        values = [h["pcsi"] for h in history]
        
        # Draw band zones
        for band in bands:
            color = band["color"]
            ax.axhspan(band["min"], band["max"], alpha=0.15, color=color)
        
        ax.plot(dates, values, color="#00d4ff", linewidth=2.5, marker="o", markersize=4)
        ax.fill_between(range(len(dates)), values, alpha=0.1, color="#00d4ff")
        
        # Style
        ax.set_ylim(0, 100)
        ax.set_ylabel("PCSI", color="#e0e0e0", fontsize=11)
        ax.tick_params(colors="#e0e0e0", labelsize=9)
        
        # Thin x labels
        if len(dates) > 10:
            step = max(len(dates) // 6, 1)
            ax.set_xticks(range(0, len(dates), step))
            ax.set_xticklabels([dates[i] for i in range(0, len(dates), step)], rotation=30)
        else:
            ax.set_xticks(range(len(dates)))
            ax.set_xticklabels(dates, rotation=30)
        
        for spine in ax.spines.values():
            spine.set_color("#333")
    else:
        ax.text(0.5, 0.5, "No historical data yet", ha="center", va="center",
                color="#e0e0e0", fontsize=14, transform=ax.transAxes)
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 100)
    
    ax.set_title("30-Day PCSI Trend", color="#e0e0e0", fontsize=13, pad=10)
    ax.grid(True, alpha=0.2, color="#555")
    
    return _fig_to_base64(fig)


def _make_pillar_bars(pillar_data, bands):
    """Horizontal bar chart for pillar scores."""
    fig, ax = plt.subplots(figsize=(8, 2.5))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#1a1a2e")
    
    names = list(pillar_data.keys())
    scores = [pillar_data[n] if pillar_data[n] is not None else 0 for n in names]
    display_names = [n.replace("_", " ").title() for n in names]
    
    colors = []
    for s in scores:
        c = "#999"
        for band in bands:
            if band["min"] <= s <= band["max"]:
                c = band["color"]
                break
        colors.append(c)
    
    y_pos = range(len(names))
    ax.barh(y_pos, scores, color=colors, height=0.6, edgecolor="#444")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(display_names, color="#e0e0e0", fontsize=11)
    ax.set_xlim(0, 100)
    ax.set_xlabel("Score", color="#e0e0e0", fontsize=10)
    ax.tick_params(colors="#e0e0e0")
    
    for i, s in enumerate(scores):
        ax.text(s + 1, i, f"{s:.1f}", va="center", color="#e0e0e0", fontsize=10)
    
    for spine in ax.spines.values():
        spine.set_color("#333")
    ax.grid(True, axis="x", alpha=0.2, color="#555")
    
    return _fig_to_base64(fig)


def _direction_arrow(delta):
    if delta is None:
        return "—"
    if delta > 1:
        return "↑"
    elif delta < -1:
        return "↓"
    return "→"


def _signal_arrow(score):
    if score is None:
        return "—"
    if score >= 60:
        return "↑"
    elif score <= 40:
        return "↓"
    return "→"


def _freshness_badge(stale):
    if stale:
        return '<span style="color:#e74c3c;font-weight:bold;">STALE</span>'
    return '<span style="color:#2ecc71;">Fresh</span>'


def generate_dashboard(pcsi_value, label, delta_1d, pillar_scores, signal_details, history, bands, output_path):
    """Generate self-contained HTML dashboard."""
    
    trend_b64 = _make_trend_chart(history, bands)
    pillar_b64 = _make_pillar_bars(pillar_scores, bands)
    
    # Color for main PCSI
    main_color = "#999"
    for band in bands:
        if pcsi_value is not None and band["min"] <= pcsi_value <= band["max"]:
            main_color = band["color"]
            break
    
    arrow = _direction_arrow(delta_1d)
    delta_str = f"{delta_1d:+.1f}" if delta_1d is not None else "N/A"
    pcsi_str = f"{pcsi_value:.1f}" if pcsi_value is not None else "N/A"
    
    # Signal table rows
    signal_rows = ""
    for sig in signal_details:
        score_str = f"{sig['score']:.1f}" if sig.get("score") is not None else "N/A"
        val_str = f"{sig['current_value']:.4f}" if sig.get("current_value") is not None else "N/A"
        sig_arrow = _signal_arrow(sig.get("score"))
        fresh = _freshness_badge(sig.get("stale", True))
        signal_rows += f"""
        <tr>
            <td>{sig['name']}</td>
            <td>{val_str}</td>
            <td style="font-weight:bold;">{score_str}</td>
            <td>{sig_arrow}</td>
            <td>{sig.get('last_updated', 'N/A')}</td>
            <td>{fresh}</td>
        </tr>"""
    
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PCSI Dashboard — {date_str}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ 
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #0d0d1a; color: #e0e0e0; padding: 20px; max-width: 1100px; margin: 0 auto;
  }}
  .header {{ text-align: center; padding: 30px 0 20px; }}
  .header h1 {{ font-size: 1.8em; color: #00d4ff; margin-bottom: 5px; }}
  .header .date {{ color: #888; font-size: 0.95em; }}
  .pcsi-main {{
    text-align: center; padding: 20px; margin: 20px 0;
    background: #1a1a2e; border-radius: 12px; border: 1px solid #333;
  }}
  .pcsi-value {{ font-size: 4em; font-weight: 800; color: {main_color}; }}
  .pcsi-label {{ font-size: 1.3em; color: {main_color}; margin-top: 5px; }}
  .pcsi-delta {{ font-size: 1.1em; color: #aaa; margin-top: 5px; }}
  .section {{ 
    background: #1a1a2e; border-radius: 12px; border: 1px solid #333;
    padding: 20px; margin: 15px 0;
  }}
  .section h2 {{ color: #00d4ff; font-size: 1.2em; margin-bottom: 15px; }}
  .chart-img {{ width: 100%; border-radius: 8px; }}
  table {{ width: 100%; border-collapse: collapse; }}
  th {{ text-align: left; padding: 10px 8px; border-bottom: 2px solid #333; color: #00d4ff; font-size: 0.9em; }}
  td {{ padding: 8px; border-bottom: 1px solid #222; font-size: 0.9em; }}
  tr:hover {{ background: #222233; }}
  .footer {{ text-align: center; padding: 20px; color: #555; font-size: 0.8em; margin-top: 20px; }}
</style>
</head>
<body>

<div class="header">
  <h1>Private Credit Sentiment Index</h1>
  <div class="date">{date_str}</div>
</div>

<div class="pcsi-main">
  <div class="pcsi-value">{pcsi_str}</div>
  <div class="pcsi-label">{label}</div>
  <div class="pcsi-delta">{arrow} {delta_str} from previous</div>
</div>

<div class="section">
  <h2>Pillar Breakdown</h2>
  <img class="chart-img" src="data:image/png;base64,{pillar_b64}" alt="Pillar Scores">
</div>

<div class="section">
  <h2>30-Day Trend</h2>
  <img class="chart-img" src="data:image/png;base64,{trend_b64}" alt="30-Day Trend">
</div>

<div class="section">
  <h2>Signal Details</h2>
  <table>
    <thead>
      <tr>
        <th>Signal</th>
        <th>Current Value</th>
        <th>Score (0-100)</th>
        <th>Direction</th>
        <th>Last Updated</th>
        <th>Freshness</th>
      </tr>
    </thead>
    <tbody>
      {signal_rows}
    </tbody>
  </table>
</div>

<div class="footer">
  <p><strong>Methodology:</strong> 10 signals across 3 pillars — Credit Spreads (35%), Credit Flows (30%), Macro Environment (35%).
  Percentile rank normalization over 504-day rolling window. Stale signals receive halved weight.</p>
  <p>Sources: FRED (ICE BofA indices, yield curve, fed funds), Yahoo Finance (ETF prices, VIX).</p>
  <p>Generated by PCSI v1.0 — {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
</div>

</body>
</html>"""
    
    with open(output_path, "w") as f:
        f.write(html)
    
    return output_path
