"""Download a classroom S&P-style daily panel for the Krauss notebook.

Not a replication of Krauss et al. (2017):
- tickers are a *fixed* large-cap list (survivorship vs true index membership);
- market = SPY total-return proxy via adjusted close.

Usage (from repo root):
    python data/download_krauss_panel.py
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import yfinance as yf

OUT = Path(__file__).resolve().parent / "krauss_sp500_daily.csv"

# Liquid, long-history names (not a point-in-time S&P 500).
TICKERS = [
    "SPY",
    "AAPL", "MSFT", "AMZN", "GOOGL", "META", "NVDA", "TSLA", "BRK-B", "JPM", "JNJ",
    "V", "UNH", "XOM", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "PEP",
    "KO", "COST", "AVGO", "WMT", "MCD", "CSCO", "ACN", "LIN", "ABT", "TMO",
    "DHR", "NFLX", "CRM", "AMD", "INTC", "ORCL", "ADBE", "TXN", "NKE", "QCOM",
    "PM", "IBM", "AMGN", "HON", "GE", "CAT", "BA", "GS", "MS", "BLK",
]

START = "2015-01-01"
END = "2023-12-31"


def main() -> None:
    raw = yf.download(
        TICKERS,
        start=START,
        end=END,
        auto_adjust=True,
        progress=True,
        threads=True,
        group_by="ticker",
    )
    if raw.empty:
        raise RuntimeError("yfinance returned no data")

    frames = []
    # yfinance layout varies; normalize to ticker -> Close
    if isinstance(raw.columns, pd.MultiIndex):
        # Could be (ticker, field) or (field, ticker)
        level0 = raw.columns.get_level_values(0)
        if "Close" in set(level0):
            close = raw["Close"]
        else:
            pieces = []
            for t in TICKERS:
                if t in raw.columns.get_level_values(0):
                    pieces.append(raw[t]["Close"].rename(t))
            close = pd.concat(pieces, axis=1)
    else:
        close = raw[["Close"]].rename(columns={"Close": TICKERS[0]})

    close = close.sort_index()
    for t in close.columns:
        s = close[t].dropna()
        if s.empty:
            continue
        frames.append(
            pd.DataFrame(
                {
                    "date": s.index.tz_localize(None) if s.index.tz is not None else s.index,
                    "ticker": t,
                    "close": s.to_numpy(),
                }
            )
        )
    panel = pd.concat(frames, ignore_index=True)
    panel["date"] = pd.to_datetime(panel["date"]).dt.tz_localize(None)
    panel = panel.sort_values(["ticker", "date"])
    OUT.parent.mkdir(parents=True, exist_ok=True)
    panel.to_csv(OUT, index=False)
    print(f"wrote {OUT}  rows={len(panel):,}  tickers={panel['ticker'].nunique()}  "
          f"{panel['date'].min().date()} → {panel['date'].max().date()}")


if __name__ == "__main__":
    main()
