"""
Inverse Perpetual Funding Rate Analysis
========================================
Analyzes funding rate data for inverse (coin-margined) perpetual contracts
on Binance, OKX, and Bybit for BTC, ETH, XRP, and DOGE.

Data fetching strategy:
  1. Primary:  ccxt library (requires `pip install ccxt`)
  2. Fallback: Binance S3 archive + CoinGecko snapshots for OKX/Bybit

Produces:
  1. Annualized funding rate table (7d, 30d, 60d, 90d horizons)
  2. Rolling 24h funding rate charts over 90 days

Usage:
  pip install ccxt pandas matplotlib requests
  python funding_rate_analysis.py
"""

import glob
import time
import requests
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    import ccxt
    CCXT_AVAILABLE = True
except ImportError:
    CCXT_AVAILABLE = False

# ── Configuration ──────────────────────────────────────────────────────────

COINS = ["BTC", "ETH", "XRP", "DOGE"]
EXCHANGES = ["Binance", "OKX", "Bybit"]

# Inverse perp symbol mappings — exchange-native names (for display / S3 fallback)
SYMBOLS = {
    "Binance": {"BTC": "BTCUSD_PERP", "ETH": "ETHUSD_PERP", "XRP": "XRPUSD_PERP", "DOGE": "DOGEUSD_PERP"},
    "OKX":     {"BTC": "BTC-USD-SWAP", "ETH": "ETH-USD-SWAP", "XRP": "XRP-USD-SWAP", "DOGE": "DOGE-USD-SWAP"},
    "Bybit":   {"BTC": "BTCUSD",       "ETH": "ETHUSD",       "XRP": "XRPUSD",       "DOGE": "DOGEUSD"},
}

# ccxt unified symbol format for inverse perps: BASE/USD:BASE
CCXT_SYMBOLS = {
    "BTC":  "BTC/USD:BTC",
    "ETH":  "ETH/USD:ETH",
    "XRP":  "XRP/USD:XRP",
    "DOGE": "DOGE/USD:DOGE",
}

SCRIPT_DIR = Path(__file__).resolve().parent
DATA_DIR = SCRIPT_DIR / "funding_data" / "binance"
LOOKBACK_DAYS = 90
PERIODS_PER_DAY = 3   # 8h funding intervals
NOW = datetime.now(timezone.utc)


# ══════════════════════════════════════════════════════════════════════════
# PRIMARY: ccxt-based data fetching
# ══════════════════════════════════════════════════════════════════════════

def _create_exchange(name: str):
    """Instantiate a ccxt exchange object."""
    cls_map = {"Binance": ccxt.binance, "OKX": ccxt.okx, "Bybit": ccxt.bybit}
    exchange = cls_map[name]({"enableRateLimit": True})
    # Binance coin-margined futures require the 'delivery' (dapi) option
    if name == "Binance":
        exchange.options["defaultType"] = "delivery"
    return exchange


def fetch_funding_ccxt(exchange_name: str, coin: str) -> pd.DataFrame:
    """Fetch 90 days of funding rate history via ccxt."""
    exchange = _create_exchange(exchange_name)
    symbol = CCXT_SYMBOLS[coin]
    since_ms = int((NOW - timedelta(days=LOOKBACK_DAYS)).timestamp() * 1000)
    end_ms = int(NOW.timestamp() * 1000)

    all_rows = []
    cursor = since_ms

    while cursor < end_ms:
        try:
            batch = exchange.fetch_funding_rate_history(symbol, since=cursor, limit=200)
        except Exception as e:
            print(f"    ccxt error at cursor {cursor}: {e}")
            break

        if not batch:
            break

        all_rows.extend(batch)
        last_ts = batch[-1]["timestamp"]
        if last_ts <= cursor:
            break
        cursor = last_ts + 1
        time.sleep(exchange.rateLimit / 1000)

    if not all_rows:
        return pd.DataFrame(columns=["timestamp", "rate"])

    df = pd.DataFrame(all_rows)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["rate"] = df["fundingRate"].astype(float)
    cutoff = NOW - timedelta(days=LOOKBACK_DAYS)
    df = df[df["timestamp"] >= cutoff]
    return df[["timestamp", "rate"]].sort_values("timestamp").drop_duplicates("timestamp").reset_index(drop=True)


def fetch_all_ccxt() -> dict:
    """Attempt to fetch all 12 contracts via ccxt. Returns nested dict."""
    data = {}
    for exchange_name in EXCHANGES:
        data[exchange_name] = {}
        for coin in COINS:
            label = f"{exchange_name} {SYMBOLS[exchange_name][coin]}"
            print(f"  {label} ...", end=" ", flush=True)
            try:
                df = fetch_funding_ccxt(exchange_name, coin)
                print(f"{len(df)} records", flush=True)
            except Exception as e:
                print(f"FAILED ({e})", flush=True)
                df = pd.DataFrame(columns=["timestamp", "rate"])
            data[exchange_name][coin] = df
    return data


# ══════════════════════════════════════════════════════════════════════════
# FALLBACK: Binance S3 archive + CoinGecko snapshots
# ══════════════════════════════════════════════════════════════════════════

def load_binance_csv(coin: str) -> pd.DataFrame:
    """Load Binance historical funding from downloaded S3 CSV files."""
    symbol = SYMBOLS["Binance"][coin]
    pattern = str(DATA_DIR / f"{symbol}-fundingRate-*.csv")
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
    cutoff = NOW - timedelta(days=LOOKBACK_DAYS)
    return combined[combined["timestamp"] >= cutoff].reset_index(drop=True)


def fetch_coingecko_current_rates() -> dict:
    """Fetch current funding rate snapshots from CoinGecko derivatives API."""
    url = "https://api.coingecko.com/api/v3/derivatives?include_tickers=unexpired"
    resp = requests.get(url, timeout=60, headers={"Accept": "application/json"})
    resp.raise_for_status()
    data = resp.json()

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
        if contract_type != "perpetual":
            continue

        sym_upper = symbol.upper()
        is_inverse = ("USD" in sym_upper and "USDT" not in sym_upper and "USDC" not in sym_upper)
        if not is_inverse:
            continue

        key = (market, index_id)
        if funding is not None:
            results[key] = {
                "symbol": symbol,
                "funding_rate_pct": float(funding),
                "rate": float(funding) / 100,
            }

    return results


def fetch_all_fallback() -> tuple[dict, dict]:
    """Fallback path: Binance S3 history + CoinGecko snapshots for OKX/Bybit."""
    data = {}

    # Binance from S3 CSVs
    data["Binance"] = {}
    for coin in COINS:
        df = load_binance_csv(coin)
        rng = (f"{df['timestamp'].min():%Y-%m-%d} to {df['timestamp'].max():%Y-%m-%d}"
               if len(df) else "N/A")
        print(f"  Binance {SYMBOLS['Binance'][coin]:15s} {len(df):4d} records  ({rng})")
        data["Binance"][coin] = df

    # OKX / Bybit: empty (will use snapshots in table)
    for ex in ["OKX", "Bybit"]:
        data[ex] = {coin: pd.DataFrame(columns=["timestamp", "rate"]) for coin in COINS}

    # CoinGecko snapshots
    print("  Fetching CoinGecko snapshots ...", flush=True)
    current_rates = fetch_coingecko_current_rates()
    for (ex, coin), info in sorted(current_rates.items()):
        ann = info["rate"] * PERIODS_PER_DAY * 365 * 100
        print(f"    {ex:8s} {coin:5s} {info['symbol']:15s} "
              f"rate={info['funding_rate_pct']:+.6f}%  ann={ann:+.2f}%")

    return data, current_rates


# ══════════════════════════════════════════════════════════════════════════
# Analysis
# ══════════════════════════════════════════════════════════════════════════

def annualized_rate(df: pd.DataFrame, days: int) -> float | None:
    """Compute annualized funding rate over the most recent `days`."""
    if df.empty:
        return None
    cutoff = NOW - timedelta(days=days)
    subset = df[df["timestamp"] >= cutoff]
    if len(subset) < 3:
        return None
    avg_per_period = subset["rate"].mean()
    return avg_per_period * PERIODS_PER_DAY * 365 * 100


def build_summary_table(data: dict, current_rates: dict | None = None) -> pd.DataFrame:
    """Build summary DataFrame with annualized funding across horizons.

    If current_rates is provided, exchanges with empty history will use
    the snapshot values (marked with _snapshot=True).
    """
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
                row["_snapshot"] = False
                for h in horizons:
                    row[f"{h}d Ann. %"] = annualized_rate(df, h)
            elif current_rates:
                key = (exchange, coin)
                snap = current_rates.get(key)
                if snap:
                    ann = snap["rate"] * PERIODS_PER_DAY * 365 * 100
                    row["_snapshot"] = True
                    for h in horizons:
                        row[f"{h}d Ann. %"] = ann
                else:
                    row["_snapshot"] = False
                    for h in horizons:
                        row[f"{h}d Ann. %"] = None
            else:
                row["_snapshot"] = False
                for h in horizons:
                    row[f"{h}d Ann. %"] = None

            rows.append(row)

    return pd.DataFrame(rows)


def rolling_24h_funding(df: pd.DataFrame) -> pd.DataFrame:
    """Compute rolling 24h annualized funding (sum of 3 consecutive 8h periods * 365)."""
    if df.empty:
        return pd.DataFrame(columns=["timestamp", "rolling_24h_ann"])
    df = df.copy().set_index("timestamp").sort_index()
    df["rolling_24h_ann"] = df["rate"].rolling(window=3, min_periods=3).sum() * 365 * 100
    return df[["rolling_24h_ann"]].dropna().reset_index()


# ══════════════════════════════════════════════════════════════════════════
# Visualization
# ══════════════════════════════════════════════════════════════════════════

def render_table(summary: pd.DataFrame, output_path: str):
    """Render a formatted table image with conditional coloring."""
    horizons = ["7d Ann. %", "30d Ann. %", "60d Ann. %", "90d Ann. %"]

    all_vals = []
    for h in horizons:
        all_vals.extend(summary[h].dropna().tolist())
    if not all_vals:
        print("  No data to render table.")
        return

    abs_max = max(abs(min(all_vals)), abs(max(all_vals)), 0.01)

    fig, ax = plt.subplots(figsize=(16, 7.5))
    ax.axis("off")

    col_labels = ["Exchange", "Contract"] + horizons
    cell_text = []
    cell_colors = []

    for _, row in summary.iterrows():
        text_row = [row["Exchange"], row["Contract"]]
        color_row = ["#f5f5f5", "#f5f5f5"]
        is_snap = row.get("_snapshot", False)

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

                norm_val = val / abs_max
                if val > 0:
                    intensity = min(abs(norm_val), 1.0)
                    r = int(255 - intensity * 120)
                    g = int(255 - intensity * 40)
                    b = int(255 - intensity * 120)
                    color_row.append(f"#{r:02x}{g:02x}{b:02x}")
                elif val < 0:
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

    ax.set_title(
        "Inverse Perpetual Funding Rates — Annualized\n"
        "Binance | OKX | Bybit",
        fontsize=14, fontweight="bold", pad=25, loc="center"
    )

    has_snapshots = summary["_snapshot"].any() if "_snapshot" in summary.columns else False
    footnote = f"Data as of {NOW.strftime('%Y-%m-%d %H:%M UTC')}"
    if has_snapshots:
        footnote += " | Values marked * are current snapshots, not historical averages"
    footnote += "\nPositive = longs pay shorts | Annualized = avg per-period rate x 3 x 365"
    fig.text(0.5, 0.02, footnote,
             ha="center", fontsize=8.5, color="#666666", style="italic")

    plt.savefig(output_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Table saved to {output_path}")


def render_chart(data: dict, output_path: str):
    """Plot rolling 24h annualized funding per exchange x coin (2x2 per exchange)."""
    coin_colors = {"BTC": "#F7931A", "ETH": "#627EEA", "XRP": "#00AAE4", "DOGE": "#C2A633"}

    # Determine which exchanges have data
    exchanges_with_data = [ex for ex in EXCHANGES
                           if any(not data[ex][c].empty for c in COINS)]

    if not exchanges_with_data:
        print("  No historical data for chart.")
        return

    n_ex = len(exchanges_with_data)
    fig, axes = plt.subplots(n_ex, 4, figsize=(20, 4 * n_ex + 1),
                             sharex=True, squeeze=False)

    for row_idx, exchange in enumerate(exchanges_with_data):
        for col_idx, coin in enumerate(COINS):
            ax = axes[row_idx][col_idx]
            df = data[exchange][coin]
            rdf = rolling_24h_funding(df)

            if not rdf.empty:
                color = coin_colors[coin]
                ax.fill_between(rdf["timestamp"], rdf["rolling_24h_ann"], 0,
                                where=rdf["rolling_24h_ann"] >= 0,
                                alpha=0.3, color="#2ecc71", interpolate=True)
                ax.fill_between(rdf["timestamp"], rdf["rolling_24h_ann"], 0,
                                where=rdf["rolling_24h_ann"] < 0,
                                alpha=0.3, color="#e74c3c", interpolate=True)
                ax.plot(rdf["timestamp"], rdf["rolling_24h_ann"],
                        color=color, linewidth=1.2, alpha=0.9)
                ax.axhline(y=0, color="gray", linewidth=0.5, linestyle="-")

                mean_val = rdf["rolling_24h_ann"].mean()
                ax.text(0.03, 0.93, f"Avg: {mean_val:+.1f}%",
                        transform=ax.transAxes, fontsize=7.5, verticalalignment="top",
                        bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.8))
            else:
                ax.text(0.5, 0.5, "No data", transform=ax.transAxes,
                        ha="center", va="center", fontsize=11, color="gray")

            if row_idx == 0:
                ax.set_title(f"{coin}", fontsize=11, fontweight="bold")
            if col_idx == 0:
                ax.set_ylabel(f"{exchange}\nAnn. %", fontsize=9)

            ax.grid(True, alpha=0.2)
            ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))

    for ax in axes[-1]:
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
        ax.xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=30, fontsize=7.5)

    fig.suptitle(
        "Rolling 24-Hour Funding Rates — Inverse Perpetuals (Annualized)",
        fontsize=14, fontweight="bold", y=1.01
    )
    fig.text(0.5, -0.01,
             "Rolling 24h = sum of 3 consecutive 8h funding periods, annualized (x365) | "
             "Green = positive (longs pay), Red = negative (shorts pay)",
             ha="center", fontsize=8.5, color="#666666", style="italic")

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Chart saved to {output_path}")


def render_combined_chart(data: dict, output_path: str):
    """One panel per exchange, all 4 coins overlaid."""
    coin_colors = {"BTC": "#F7931A", "ETH": "#627EEA", "XRP": "#00AAE4", "DOGE": "#C2A633"}

    exchanges_with_data = [ex for ex in EXCHANGES
                           if any(not data[ex][c].empty for c in COINS)]
    if not exchanges_with_data:
        print("  No historical data for combined chart.")
        return

    n = len(exchanges_with_data)
    fig, axes = plt.subplots(n, 1, figsize=(18, 5 * n), sharex=True, squeeze=False)

    for idx, exchange in enumerate(exchanges_with_data):
        ax = axes[idx][0]
        for coin in COINS:
            rdf = rolling_24h_funding(data[exchange][coin])
            if not rdf.empty:
                ax.plot(rdf["timestamp"], rdf["rolling_24h_ann"],
                        label=f"{coin} ({SYMBOLS[exchange][coin]})",
                        color=coin_colors[coin],
                        linewidth=1.3 if coin in ("BTC", "ETH") else 0.9,
                        alpha=0.85)

        ax.axhline(y=0, color="gray", linewidth=0.6, linestyle="-")
        ax.set_ylabel("Annualized %", fontsize=10)
        ax.set_title(f"{exchange} — Inverse Perps Rolling 24h Funding",
                      fontsize=12, fontweight="bold")
        ax.legend(loc="upper left", fontsize=9, ncol=4, framealpha=0.9)
        ax.grid(True, alpha=0.25)
        ax.yaxis.set_major_formatter(mticker.FormatStrFormatter('%.0f%%'))

    axes[-1][0].xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    axes[-1][0].xaxis.set_major_locator(mdates.WeekdayLocator(interval=2))
    plt.setp(axes[-1][0].xaxis.get_majorticklabels(), rotation=30, fontsize=9)

    fig.suptitle("Rolling 24h Funding — All Exchanges Compared",
                 fontsize=14, fontweight="bold", y=1.01)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight", facecolor="white")
    plt.close()
    print(f"  Combined chart saved to {output_path}")


# ══════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════

def main():
    out_dir = SCRIPT_DIR

    print("=" * 65)
    print(" Inverse Perpetual Funding Rate Analysis")
    print(f" Exchanges: {', '.join(EXCHANGES)}")
    print(f" Coins: {', '.join(COINS)} | Lookback: {LOOKBACK_DAYS} days")
    print("=" * 65)
    print()

    # ── Step 1: Fetch data ─────────────────────────────────────────────
    current_rates = None  # only used in fallback mode

    if CCXT_AVAILABLE:
        print("[1/4] Fetching funding rates via ccxt ...")
        data = fetch_all_ccxt()

        # Check if ccxt actually returned data for all exchanges
        ccxt_worked = all(
            any(not data[ex][c].empty for c in COINS) for ex in EXCHANGES
        )

        if not ccxt_worked:
            print()
            print("  ccxt returned partial/no data — falling back to S3 + CoinGecko ...")
            data_fb, current_rates = fetch_all_fallback()
            # Merge: keep ccxt data where available, fill gaps with fallback
            for ex in EXCHANGES:
                for coin in COINS:
                    if data[ex][coin].empty and not data_fb[ex][coin].empty:
                        data[ex][coin] = data_fb[ex][coin]
    else:
        print("[1/4] ccxt not available — using S3 archive + CoinGecko fallback ...")
        data, current_rates = fetch_all_fallback()

    print()

    # ── Step 2: Summary table ──────────────────────────────────────────
    print("[2/4] Building summary table ...")
    summary = build_summary_table(data, current_rates)

    display_cols = ["Exchange", "Contract", "7d Ann. %", "30d Ann. %", "60d Ann. %", "90d Ann. %"]
    print()
    print(summary[display_cols].to_string(
        index=False,
        float_format=lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A"
    ))
    print()

    summary[display_cols].to_csv(out_dir / "funding_summary.csv", index=False)
    print(f"  CSV saved to {out_dir / 'funding_summary.csv'}")
    print()

    # ── Step 3: Table image ────────────────────────────────────────────
    print("[3/4] Rendering formatted table ...")
    render_table(summary, str(out_dir / "funding_table.png"))
    print()

    # ── Step 4: Charts ─────────────────────────────────────────────────
    print("[4/4] Rendering rolling 24h funding charts ...")
    render_chart(data, str(out_dir / "funding_chart_rolling24h.png"))
    render_combined_chart(data, str(out_dir / "funding_chart_combined.png"))
    print()

    # ── Summary ────────────────────────────────────────────────────────
    print("=" * 65)
    print(" Analysis complete!")
    print(f" Output directory: {out_dir}")
    print("   - funding_summary.csv")
    print("   - funding_table.png")
    print("   - funding_chart_rolling24h.png")
    print("   - funding_chart_combined.png")

    # Report data coverage
    print()
    for ex in EXCHANGES:
        counts = {c: len(data[ex][c]) for c in COINS}
        total = sum(counts.values())
        if total > 0:
            ranges = []
            for c in COINS:
                df = data[ex][c]
                if not df.empty:
                    ranges.append(f"{df['timestamp'].min():%Y-%m-%d}..{df['timestamp'].max():%Y-%m-%d}")
            rng = ranges[0] if ranges else "N/A"
            print(f"  {ex:8s}: {total:4d} total records ({rng})")
        else:
            print(f"  {ex:8s}: snapshot only (exchange API unreachable)")

    if current_rates:
        print()
        print("  NOTE: OKX/Bybit values marked * are point-in-time snapshots,")
        print("        not historical averages. Run locally for full history.")
    print("=" * 65)


if __name__ == "__main__":
    main()
