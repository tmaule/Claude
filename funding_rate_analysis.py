"""
Inverse Perpetual Funding Rate Analysis
========================================
Analyzes funding rate data for inverse (coin-margined) perpetual contracts
on Binance, OKX, and Bybit for BTC, ETH, XRP, and DOGE.

Data sources:
  - Binance:  Historical data from Binance Vision S3 archive (Nov 2025 - Jan 2026)
  - OKX:     Current snapshot from CoinGecko derivatives API
  - Bybit:   Current snapshot from CoinGecko derivatives API

Note: OKX and Bybit direct APIs were inaccessible from this environment.
Historical data for those exchanges is therefore unavailable. Only Binance
has full 90-day history; OKX and Bybit show current annualized rates only.

Produces:
  1. Annualized funding rate table (7d, 30d, 60d, 90d horizons)
  2. Rolling 24h funding rate chart over 90 days (Binance only)
"""

import glob
import json
import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
import matplotlib.colors as mcolors
from datetime import datetime, timedelta, timezone

# ── Configuration ──────────────────────────────────────────────────────────

COINS = ["BTC", "ETH", "XRP", "DOGE"]
EXCHANGES = ["Binance", "OKX", "Bybit"]

SYMBOLS = {
    "Binance": {"BTC": "BTCUSD_PERP", "ETH": "ETHUSD_PERP", "XRP": "XRPUSD_PERP", "DOGE": "DOGEUSD_PERP"},
    "OKX":     {"BTC": "BTC-USD-SWAP", "ETH": "ETH-USD-SWAP", "XRP": "XRP-USD-SWAP", "DOGE": "DOGE-USD-SWAP"},
    "Bybit":   {"BTC": "BTCUSD",       "ETH": "ETHUSD",       "XRP": "XRPUSD",       "DOGE": "DOGEUSD"},
}

DATA_DIR = "/home/user/Claude/funding_data/binance"
LOOKBACK_DAYS = 90
PERIODS_PER_DAY = 3   # 8h funding intervals
NOW = datetime.now(timezone.utc)


# ── Data Loading ───────────────────────────────────────────────────────────

def load_binance_csv(coin: str) -> pd.DataFrame:
    """Load Binance historical funding from downloaded S3 CSV files."""
    symbol = SYMBOLS["Binance"][coin]
    pattern = f"{DATA_DIR}/{symbol}-fundingRate-*.csv"
    files = sorted(glob.glob(pattern))
    if not files:
        return pd.DataFrame(columns=["timestamp", "rate"])

    frames = []
    for f in files:
        df = pd.read_csv(f)
        df["timestamp"] = pd.to_datetime(df["calc_time"], unit="ms", utc=True)
        df["rate"] = df["last_funding_rate"].astype(float)
        frames.append(df[["timestamp", "rate"]])

    combined = pd.concat(frames, ignore_index=True).sort_values("timestamp").reset_index(drop=True)
    # Filter to lookback window
    cutoff = NOW - timedelta(days=LOOKBACK_DAYS)
    return combined[combined["timestamp"] >= cutoff].reset_index(drop=True)


def fetch_coingecko_current_rates() -> dict:
    """Fetch current funding rate snapshots from CoinGecko derivatives API."""
    print("  Fetching current snapshots from CoinGecko ...", flush=True)
    url = "https://api.coingecko.com/api/v3/derivatives?include_tickers=unexpired"
    resp = requests.get(url, timeout=60, headers={"Accept": "application/json"})
    resp.raise_for_status()
    data = resp.json()

    # Map CoinGecko exchange names to our names
    exchange_map = {
        "Binance (Futures)": "Binance",
        "OKX (Futures)": "OKX",
        "Bybit (Futures)": "Bybit",
    }

    results = {}
    for t in data:
        market = exchange_map.get(t.get("market", ""), "")
        if not market:
            continue
        symbol = t.get("symbol", "")
        index_id = t.get("index_id", "").upper()
        funding = t.get("funding_rate")
        contract_type = t.get("contract_type", "")

        if index_id not in COINS:
            continue

        # Only perpetuals, not quarterly futures
        if contract_type != "perpetual":
            continue

        # Identify inverse perps: USD-denominated, not USDT/USDC
        sym_upper = symbol.upper()
        is_inverse = ("USD" in sym_upper and "USDT" not in sym_upper and "USDC" not in sym_upper)
        if not is_inverse:
            continue

        key = (market, index_id)
        if funding is not None:
            results[key] = {
                "symbol": symbol,
                "funding_rate_pct": float(funding),  # CoinGecko returns as percentage
                "rate": float(funding) / 100,          # Convert to decimal
            }

    return results


def load_all_data() -> dict:
    """Load all funding data. Returns nested dict[exchange][coin] -> DataFrame."""
    data = {}

    # Binance: full history from S3 archive
    data["Binance"] = {}
    for coin in COINS:
        df = load_binance_csv(coin)
        print(f"  Binance {coin}: {len(df)} records "
              f"({df['timestamp'].min().strftime('%Y-%m-%d') if len(df) else 'N/A'} to "
              f"{df['timestamp'].max().strftime('%Y-%m-%d') if len(df) else 'N/A'})")
        data["Binance"][coin] = df

    # OKX and Bybit: empty history (APIs blocked), will use current snapshots for table
    for exchange in ["OKX", "Bybit"]:
        data[exchange] = {}
        for coin in COINS:
            data[exchange][coin] = pd.DataFrame(columns=["timestamp", "rate"])

    return data


# ── Analysis ───────────────────────────────────────────────────────────────

def annualized_rate(df: pd.DataFrame, days: int) -> float | None:
    """Compute annualized funding rate over the most recent `days`."""
    if df.empty:
        return None
    cutoff = NOW - timedelta(days=days)
    subset = df[df["timestamp"] >= cutoff]
    if len(subset) < 3:
        return None
    avg_per_period = subset["rate"].mean()
    return avg_per_period * PERIODS_PER_DAY * 365 * 100  # as percentage


def build_summary_table(data: dict, current_rates: dict) -> pd.DataFrame:
    """Build summary DataFrame with annualized funding across horizons."""
    horizons = [7, 30, 60, 90]
    rows = []

    for exchange in EXCHANGES:
        for coin in COINS:
            df = data[exchange][coin]
            row = {
                "Exchange": exchange,
                "Contract": SYMBOLS[exchange][coin],
                "Coin": coin,
            }

            if not df.empty:
                # Full history available (Binance)
                row["_snapshot"] = False
                for h in horizons:
                    row[f"{h}d Ann. %"] = annualized_rate(df, h)
            else:
                # Only current snapshot available (OKX, Bybit)
                key = (exchange, coin)
                snap = current_rates.get(key)
                if snap:
                    # Annualize the current rate: rate_per_period * 3 * 365 * 100
                    ann = snap["rate"] * PERIODS_PER_DAY * 365 * 100
                    for h in horizons:
                        row[f"{h}d Ann. %"] = ann  # same value across all horizons (snapshot)
                    row["_snapshot"] = True
                else:
                    row["_snapshot"] = False
                    for h in horizons:
                        row[f"{h}d Ann. %"] = None

            rows.append(row)

    return pd.DataFrame(rows)


def rolling_24h_funding(df: pd.DataFrame) -> pd.DataFrame:
    """Compute rolling 24h annualized funding (sum of 3 consecutive periods * 365)."""
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "rolling_24h_ann"])
    df = df.copy().set_index("timestamp").sort_index()
    df["rolling_24h_ann"] = df["rate"].rolling(window=3, min_periods=3).sum() * 365 * 100
    return df[["rolling_24h_ann"]].dropna().reset_index()


# ── Visualization ──────────────────────────────────────────────────────────

def render_table(summary: pd.DataFrame, output_path: str):
    """Render a formatted table image with conditional coloring."""
    horizons = ["7d Ann. %", "30d Ann. %", "60d Ann. %", "90d Ann. %"]

    # Collect all valid values for color scaling
    all_vals = []
    for h in horizons:
        all_vals.extend(summary[h].dropna().tolist())
    if not all_vals:
        print("No data to render table.")
        return

    vmin = min(all_vals)
    vmax = max(all_vals)
    abs_max = max(abs(vmin), abs(vmax), 0.01)

    fig, ax = plt.subplots(figsize=(16, 7.5))
    ax.axis("off")

    col_labels = ["Exchange", "Contract"] + horizons
    cell_text = []
    cell_colors = []
    is_snapshot_row = []

    for _, row in summary.iterrows():
        text_row = [row["Exchange"], row["Contract"]]
        color_row = ["#f5f5f5", "#f5f5f5"]
        is_snap = row.get("_snapshot", False)
        is_snapshot_row.append(is_snap)

        for h in horizons:
            val = row[h]
            if pd.isna(val):
                text_row.append("N/A")
                color_row.append("#e0e0e0")
            else:
                label = f"{val:+.2f}%"
                if is_snap:
                    label += "*"
                text_row.append(label)

                # Diverging color scale: green for positive, red for negative
                norm_val = val / abs_max  # [-1, 1]
                if val > 0:
                    # Green scale - more positive = more intense green
                    intensity = min(abs(norm_val), 1.0)
                    r = int(255 - intensity * 120)
                    g = int(255 - intensity * 40)
                    b = int(255 - intensity * 120)
                    color_row.append(f"#{r:02x}{g:02x}{b:02x}")
                elif val < 0:
                    # Red scale - more negative = more intense red
                    intensity = min(abs(norm_val), 1.0)
                    r = int(255 - intensity * 20)
                    g = int(255 - intensity * 110)
                    b = int(255 - intensity * 110)
                    color_row.append(f"#{r:02x}{g:02x}{b:02x}")
                else:
                    color_row.append("#ffffff")

        cell_text.append(text_row)
        cell_colors.append(color_row)

    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        cellColours=cell_colors,
        colColours=["#2F5496"] * len(col_labels),
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.7)

    # Style header
    for j in range(len(col_labels)):
        cell = table[0, j]
        cell.set_text_props(color="white", fontweight="bold", fontsize=10.5)
        cell.set_height(0.07)

    # Bold the most positive value in each horizon column
    for col_idx, h in enumerate(horizons):
        vals = summary[h].tolist()
        valid = [(i, v) for i, v in enumerate(vals) if pd.notna(v)]
        if valid:
            max_idx = max(valid, key=lambda x: x[1])[0]
            cell = table[max_idx + 1, col_idx + 2]
            cell.set_text_props(fontweight="bold", fontsize=11.5)
            cell.set_edgecolor("#2F5496")
            cell.set_linewidth(2)

    # Add alternating row shading for readability (exchange groups)
    for i in range(len(summary)):
        exchange = summary.iloc[i]["Exchange"]
        if exchange == "OKX":
            for j in range(len(col_labels)):
                c = cell_colors[i][j]
                # Slightly darken OKX rows for grouping
                table[i + 1, j].set_edgecolor("#cccccc")

    # Title and footnotes
    ax.set_title(
        "Inverse Perpetual Funding Rates — Annualized\n"
        "Binance | OKX | Bybit",
        fontsize=14, fontweight="bold", pad=25, loc="center"
    )

    fig.text(0.5, 0.02,
             f"Data as of {NOW.strftime('%Y-%m-%d %H:%M UTC')} | "
             f"Binance: historical data (Nov 2025 – Jan 2026) | "
             f"OKX & Bybit: current snapshot only (*)\n"
             f"Positive = longs pay shorts | Annualized = avg per-period rate x 3 x 365",
             ha="center", fontsize=8.5, color="#666666", style="italic")

    plt.savefig(output_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Table saved to {output_path}")


def render_chart(data: dict, output_path: str):
    """Plot rolling 24h annualized funding for Binance inverse perps over 90 days."""
    coin_colors = {"BTC": "#F7931A", "ETH": "#627EEA", "XRP": "#00AAE4", "DOGE": "#C2A633"}

    fig, axes = plt.subplots(2, 2, figsize=(18, 10), sharex=True)
    axes_flat = axes.flatten()

    for idx, coin in enumerate(COINS):
        ax = axes_flat[idx]
        df = data["Binance"][coin]
        rdf = rolling_24h_funding(df)

        if not rdf.empty:
            color = coin_colors[coin]
            ax.fill_between(
                rdf["timestamp"],
                rdf["rolling_24h_ann"],
                0,
                where=rdf["rolling_24h_ann"] >= 0,
                alpha=0.3, color="#2ecc71", interpolate=True
            )
            ax.fill_between(
                rdf["timestamp"],
                rdf["rolling_24h_ann"],
                0,
                where=rdf["rolling_24h_ann"] < 0,
                alpha=0.3, color="#e74c3c", interpolate=True
            )
            ax.plot(rdf["timestamp"], rdf["rolling_24h_ann"],
                    color=color, linewidth=1.3, alpha=0.9)
            ax.axhline(y=0, color="gray", linewidth=0.7, linestyle="-")

            # Stats annotation
            mean_val = rdf["rolling_24h_ann"].mean()
            max_val = rdf["rolling_24h_ann"].max()
            min_val = rdf["rolling_24h_ann"].min()
            ax.text(0.02, 0.95,
                    f"Mean: {mean_val:+.1f}%  Max: {max_val:+.1f}%  Min: {min_val:+.1f}%",
                    transform=ax.transAxes, fontsize=8, verticalalignment="top",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
        else:
            ax.text(0.5, 0.5, "No data", transform=ax.transAxes,
                    ha="center", va="center", fontsize=14, color="gray")

        ax.set_title(f"Binance {SYMBOLS['Binance'][coin]}", fontsize=12, fontweight="bold")
        ax.set_ylabel("Annualized %", fontsize=9)
        ax.grid(True, alpha=0.25)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))

    # Format x-axis
    for ax in axes_flat:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, fontsize=8)

    fig.suptitle(
        "Rolling 24-Hour Funding Rates — Binance Inverse Perpetuals\n"
        f"Nov 2025 – Jan 2026",
        fontsize=14, fontweight="bold", y=1.02
    )

    fig.text(0.5, -0.01,
             "Rolling 24h = sum of 3 consecutive 8h funding periods, annualized (x365) | "
             "Green fill = positive (longs pay), Red fill = negative (shorts pay)",
             ha="center", fontsize=8.5, color="#666666", style="italic")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Chart saved to {output_path}")


def render_combined_chart(data: dict, output_path: str):
    """Overlay chart: all 4 coins on one panel for easy comparison."""
    coin_colors = {"BTC": "#F7931A", "ETH": "#627EEA", "XRP": "#00AAE4", "DOGE": "#C2A633"}

    fig, ax = plt.subplots(figsize=(18, 7))

    for coin in COINS:
        df = data["Binance"][coin]
        rdf = rolling_24h_funding(df)
        if not rdf.empty:
            ax.plot(rdf["timestamp"], rdf["rolling_24h_ann"],
                    label=f"{coin} ({SYMBOLS['Binance'][coin]})",
                    color=coin_colors[coin],
                    linewidth=1.4 if coin in ("BTC", "ETH") else 1.0,
                    alpha=0.85)

    ax.axhline(y=0, color="gray", linewidth=0.7, linestyle="-")
    ax.set_ylabel("Annualized %", fontsize=11)
    ax.set_title("Binance Inverse Perps — Rolling 24h Funding (Annualized)", fontsize=14, fontweight="bold")
    ax.legend(loc="best", fontsize=10, framealpha=0.9)
    ax.grid(True, alpha=0.25)
    ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.xticks(rotation=30, fontsize=9)

    fig.text(0.5, -0.02,
             f"Data: Binance Vision S3 archive | Period: Nov 2025 – Jan 2026 | "
             f"Positive = longs pay shorts",
             ha="center", fontsize=8.5, color="#666666", style="italic")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Combined chart saved to {output_path}")


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    print("=" * 65)
    print(" Inverse Perpetual Funding Rate Analysis")
    print(" Exchanges: Binance, OKX, Bybit")
    print(f" Coins: {', '.join(COINS)} | Lookback: {LOOKBACK_DAYS} days")
    print("=" * 65)
    print()

    # Step 1: Load Binance historical data
    print("[1/5] Loading Binance historical data from S3 archive ...")
    data = load_all_data()
    print()

    # Step 2: Fetch current snapshots from CoinGecko
    print("[2/5] Fetching current funding snapshots from CoinGecko ...")
    current_rates = fetch_coingecko_current_rates()
    for (ex, coin), info in sorted(current_rates.items()):
        ann = info["rate"] * PERIODS_PER_DAY * 365 * 100
        print(f"  {ex:8s} {coin:5s} {info['symbol']:15s} current rate: {info['funding_rate_pct']:+.6f}%  "
              f"(ann: {ann:+.2f}%)")
    print()

    # Step 3: Build summary table
    print("[3/5] Building summary table ...")
    summary = build_summary_table(data, current_rates)

    # Print text table
    display_cols = ["Exchange", "Contract", "7d Ann. %", "30d Ann. %", "60d Ann. %", "90d Ann. %"]
    print()
    print(summary[display_cols].to_string(index=False, float_format=lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A"))
    print()

    # Save CSV
    summary[display_cols].to_csv("/home/user/Claude/funding_summary.csv", index=False)
    print("  CSV saved to funding_summary.csv")
    print()

    # Step 4: Render table image
    print("[4/5] Rendering formatted table ...")
    render_table(summary, "/home/user/Claude/funding_table.png")
    print()

    # Step 5: Render charts
    print("[5/5] Rendering rolling 24h funding charts ...")
    render_chart(data, "/home/user/Claude/funding_chart_rolling24h.png")
    render_combined_chart(data, "/home/user/Claude/funding_chart_combined.png")
    print()

    print("=" * 65)
    print(" Analysis complete!")
    print(" Output files:")
    print("   - funding_summary.csv")
    print("   - funding_table.png")
    print("   - funding_chart_rolling24h.png")
    print("   - funding_chart_combined.png")
    print()
    print(" NOTES:")
    print("   - Binance data: Full history from S3 archive (Nov 2025 – Jan 2026)")
    print("   - OKX & Bybit: Current snapshot only (APIs blocked in this env)")
    print("   - OKX/Bybit values marked with * are point-in-time, not averaged")
    print("=" * 65)


if __name__ == "__main__":
    main()
