#!/usr/bin/env python3
"""GMC 30k stratified subsample: live and full 3×2 CV (metrics + OOF).

Writes data/cache/lessmann_gmc_live.pkl and lessmann_gmc_full.pkl.
"""
from __future__ import annotations

import os
import sys
import time
import warnings
import zipfile
from pathlib import Path

os.environ.setdefault("PYTHONWARNINGS", "ignore:.*encountered in matmul:RuntimeWarning")
warnings.filterwarnings("ignore", message=".*encountered in matmul")

import pandas as pd
from sklearn.model_selection import train_test_split

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import run_lessmann_full as L

SEED = 2015
N_SUB = 30_000
EXPECTED = 0.067
TOL = 0.005
TARGET = "SeriousDlqin2yrs"


def gmc_csv_path() -> Path:
    root = L.repo_root()
    return root / "data" / "gmc" / "cs-training.csv"


def ensure_gmc_csv(path: Path) -> Path:
    if path.is_file():
        return path
    zpath = path.parent / "cs-training.csv.zip"
    if zpath.is_file():
        with zipfile.ZipFile(zpath) as z:
            z.extract("cs-training.csv", path.parent)
        print("extracted", zpath.name, "->", path)
        return path
    raise SystemExit(
        f"Missing {path}. Place Kaggle Give Me Some Credit cs-training.csv in data/gmc/."
    )


def load_gmc(path: Path) -> tuple[pd.DataFrame, pd.Series]:
    df = pd.read_csv(path)
    drop = [c for c in df.columns if str(c).startswith("Unnamed")]
    df = df.drop(columns=drop)
    if TARGET not in df.columns:
        raise SystemExit(f"{path} has no column {TARGET}")
    y = df[TARGET].astype(int)
    X = df.drop(columns=[TARGET])
    return X, y


def stratified_subsample(X: pd.DataFrame, y: pd.Series, n: int, seed: int):
    idx = pd.RangeIndex(len(y))
    sub, _ = train_test_split(idx, train_size=n, stratify=y, random_state=seed)
    X = X.iloc[sub].reset_index(drop=True)
    y = y.iloc[sub].reset_index(drop=True)
    return X, y


def save_pack(path: Path, metrics: pd.DataFrame, oof: pd.DataFrame) -> None:
    pd.to_pickle({"metrics": metrics, "oof": oof}, path)
    print("wrote", path)


def main() -> None:
    csv = ensure_gmc_csv(gmc_csv_path())
    print("load", csv)
    X, y = load_gmc(csv)
    print(f"GMC full {len(y):,} rows, default rate {float(y.mean()):.4f}")
    X, y = stratified_subsample(X, y, N_SUB, SEED)
    rate = float(y.mean())
    print(f"GMC subsample {len(y):,} rows, default rate {rate:.4f}  expected {EXPECTED:.3f} ± {TOL}")
    print(f"GMC target value counts:\n{y.value_counts().sort_index().to_string()}")
    assert abs(rate - EXPECTED) <= TOL, (
        f"GMC default rate {rate} is not {EXPECTED} ± {TOL}; check subsample / label coding"
    )
    _, cache = L.data_dirs()
    prep = os.environ.get("PREP_LINEAR", L.PREP_LINEAR)
    L.PREP_LINEAR = prep
    print("PREP_LINEAR", L.PREP_LINEAR)

    t0 = time.time()
    live_path = L.gmc_pickle(cache, "live")
    full_path = L.gmc_pickle(cache, "full")
    print("\n=== GMC  3×2 CV  LIVE ===")
    live_tab, live_oof = L.run_dataset("GMC", X, y, n_repeats=3, mode="live")
    save_pack(live_path, live_tab, live_oof)
    print("\nLIVE mean metrics")
    print(L.mean_table(live_tab))

    print("\n=== GMC  3×2 CV  FULL (inner 5-fold + Platt) ===")
    full_tab, full_oof = L.run_dataset("GMC", X, y, n_repeats=3, mode="full")
    save_pack(full_path, full_tab, full_oof)
    print("\nFULL mean metrics")
    print(L.mean_table(full_tab))
    print(f"\nGMC precompute runtime {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
