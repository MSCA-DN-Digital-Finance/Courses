"""Download Ken French daily factors and align them to the Krauss date window.

What this is
------------
Kenneth French's Data Library publishes **market-wide factor returns**
(Mkt-RF, SMB, HML, RMW, CMA, RF, Mom). One row per *day*, not per stock.

What this is not
----------------
It does **not** give book-to-market / profitability / investment for AAPL.
Those are Compustat characteristics. The 50-name Yahoo file only has prices.

Usage (from repo root, needs network):
    python data/download_ff_factors.py
"""

from __future__ import annotations

import io
import zipfile
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

OUT = Path(__file__).resolve().parent / "ff_daily_factors.csv"
START = "2015-01-01"
END = "2023-12-31"

FF5_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "F-F_Research_Data_5_Factors_2x3_daily_CSV.zip"
)
MOM_URL = (
    "https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/"
    "F-F_Momentum_Factor_daily_CSV.zip"
)


def _read_french_zip(url: str) -> pd.DataFrame:
    with urlopen(url, timeout=60) as resp:
        raw = resp.read()
    with zipfile.ZipFile(io.BytesIO(raw)) as zf:
        name = zf.namelist()[0]
        text = zf.read(name).decode("latin-1")
    lines = [ln for ln in text.splitlines() if ln.strip()[:8].isdigit()]
    df = pd.read_csv(io.StringIO("\n".join(lines)), header=None)
    df.columns = ["date"] + [f"c{i}" for i in range(1, df.shape[1])]
    df["date"] = pd.to_datetime(df["date"].astype(str), format="%Y%m%d")
    for c in df.columns[1:]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def main() -> None:
    ff5 = _read_french_zip(FF5_URL)
    ff5 = ff5.rename(
        columns={
            "c1": "mkt_rf",
            "c2": "smb",
            "c3": "hml",
            "c4": "rmw",
            "c5": "cma",
            "c6": "rf",
        }
    )
    mom = _read_french_zip(MOM_URL).rename(columns={"c1": "mom"})
    factors = ff5.merge(mom[["date", "mom"]], on="date", how="left")
    # Ken French files are in **percent**; keep decimals for returns work
    pct_cols = ["mkt_rf", "smb", "hml", "rmw", "cma", "rf", "mom"]
    factors[pct_cols] = factors[pct_cols] / 100.0
    factors = factors.loc[(factors["date"] >= START) & (factors["date"] <= END)]
    factors = factors.sort_values("date")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    factors.to_csv(OUT, index=False)
    print(
        f"wrote {OUT}  rows={len(factors):,}  "
        f"{factors['date'].min().date()} → {factors['date'].max().date()}"
    )


if __name__ == "__main__":
    main()
