#!/usr/bin/env python3
"""Full Lessmann protocol on GC and AC: inner 5-fold tuning + Platt.

Saves data/cache/lessmann_full_gc.pkl and lessmann_full_ac.pkl.
n_jobs=-1 only inside GridSearchCV; estimators use n_jobs=1. No GMC.
"""
from __future__ import annotations

import os
import time
import warnings
from pathlib import Path

os.environ.setdefault("PYTHONWARNINGS", "ignore:.*encountered in matmul:RuntimeWarning")
warnings.filterwarnings("ignore", message=".*encountered in matmul")

import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist, friedmanchisquare, norm
from sklearn.base import BaseEstimator, TransformerMixin, clone
from sklearn.calibration import CalibratedClassifierCV
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss, roc_auc_score, roc_curve
from sklearn.model_selection import GridSearchCV, RepeatedStratifiedKFold, StratifiedKFold
from sklearn.neural_network import MLPClassifier
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, OrdinalEncoder, StandardScaler

EXPECTED = {"GC": 0.300, "AC": 0.445}
TOL = 0.005
SEED = 2015
PREP_LINEAR = os.environ.get("PREP_LINEAR", "robust")  # "standard" | "robust"; trees are unchanged


def repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for base in [here, *here.parents]:
        if (base / "data" / "krauss_sp500_daily.csv").exists() or (base / "data" / "README.md").exists():
            return base
    return here.parent


def data_dirs() -> tuple[Path, Path]:
    root = repo_root()
    credit = root / "data" / "credit"
    cache = root / "data" / "cache"
    credit.mkdir(parents=True, exist_ok=True)
    cache.mkdir(parents=True, exist_ok=True)
    return credit, cache


def load_openml(name, version=1):
    from sklearn.datasets import fetch_openml

    bun = fetch_openml(name, version=version, as_frame="auto", parser="auto")
    X, y = bun.data.copy(), bun.target.copy()
    if not isinstance(X, pd.DataFrame):
        X = pd.DataFrame(np.asarray(X))
    return X, y


def report_and_assert(name, y):
    y = np.asarray(y).astype(int)
    rate = float(y.mean())
    print(f"{name} target value counts:\n{pd.Series(y).value_counts().sort_index().to_string()}")
    print(f"{name} default rate {rate:.4f}  expected {EXPECTED[name]:.3f} ± {TOL}")
    assert abs(rate - EXPECTED[name]) <= TOL, (
        f"{name} default rate {rate} is not {EXPECTED[name]} ± {TOL}; check label coding"
    )
    return y


def load_credit_csv(credit: Path, name: str):
    path = credit / f"{name.lower()}.csv"
    if not path.is_file():
        return None
    with path.open() as f:
        first = f.readline()
    cat_cols = []
    if first.startswith("# catcols="):
        cat_cols = [c for c in first[len("# catcols="):].strip().split(",") if c]
    df = pd.read_csv(path, comment="#")
    y = df["default"].astype(int)
    X = df.drop(columns=["default"])
    for c in cat_cols:
        if c in X.columns:
            X[c] = X[c].astype(str)
    print("load cache", path)
    return X, y


def save_credit(credit: Path, name: str, X, y):
    path = credit / f"{name.lower()}.csv"
    df = X.copy()
    cat_cols = [c for c in df.columns if not pd.api.types.is_numeric_dtype(df[c])]
    for c in cat_cols:
        df[c] = df[c].astype(str)
    df["default"] = np.asarray(y).astype(int)
    with path.open("w") as f:
        f.write("# catcols=" + ",".join(cat_cols) + "\n")
        df.to_csv(f, index=False)
    print("wrote", path)


def fetch_gc_ac():
    Xg, yg = load_openml("credit-g", 1)
    yg = (yg.astype(str).str.lower() == "bad").astype(int)
    Xa, ya = load_openml("australian", "active")
    ya = pd.to_numeric(ya, errors="coerce").fillna(0).astype(int)
    if ya.mean() > 0.5:
        ya = 1 - ya
    return {"GC": (Xg, yg), "AC": (Xa, ya)}


def load_gc_ac(credit: Path):
    sets = {}
    for name in ["GC", "AC"]:
        packed = load_credit_csv(credit, name)
        if packed is None:
            continue
        X, y = packed
        y = report_and_assert(name, y)
        sets[name] = (X, y)
    if len(sets) < 2:
        fetched = fetch_gc_ac()
        for name in ["GC", "AC"]:
            if name in sets:
                continue
            X, y = fetched[name]
            y = report_and_assert(name, y)
            save_credit(credit, name, X, y)
            sets[name] = (X, y)
    return sets


def h_measure(y, p, alpha=2.0, beta=2.0, n_c=501):
    """Hand (2009) H-measure from the ROC, cost ~ Beta(2,2)."""
    y = np.asarray(y).astype(int)
    p = np.asarray(p, float)
    n1 = int(y.sum())
    n0 = len(y) - n1
    if n0 == 0 or n1 == 0:
        return np.nan
    pi1, pi0 = n1 / len(y), n0 / len(y)
    fpr, tpr, _ = roc_curve(y, p)
    fnr = 1.0 - tpr
    cs = np.linspace(1e-6, 1 - 1e-6, n_c)
    pdf = beta_dist.pdf(cs, alpha, beta)
    L = np.min(
        pi0 * cs[:, None] * fpr[None, :] + pi1 * (1.0 - cs)[:, None] * fnr[None, :],
        axis=1,
    )
    Lmax = np.minimum(pi0 * cs, pi1 * (1.0 - cs))
    trap = getattr(np, "trapezoid", np.trapz)
    den = trap(Lmax * pdf, cs)
    if den <= 0:
        return np.nan
    return 1.0 - trap(L * pdf, cs) / den


def partial_gini(y, p, cutoff=0.4):
    y = np.asarray(y).astype(int)
    p = np.asarray(p, float)
    m = p <= cutoff
    if m.sum() < 20 or y[m].min() == y[m].max():
        return np.nan
    return 2.0 * roc_auc_score(y[m], p[m]) - 1.0


def all_metrics(y, p):
    y = np.asarray(y).astype(int)
    p = np.asarray(p, float)
    return {
        "AUC": roc_auc_score(y, p),
        "H": h_measure(y, p),
        "PG04": partial_gini(y, p),
        "Brier": brier_score_loss(y, p),
    }


def pickle_tag(prep=None):
    p = PREP_LINEAR if prep is None else prep
    if p not in ("standard", "robust"):
        raise ValueError(f"PREP_LINEAR must be 'standard' or 'robust', got {p!r}")
    return "" if p == "standard" else f"_{p}"


def gmc_pickle(cache: Path, kind: str, prep=None) -> Path:
    return cache / f"lessmann_gmc_{kind}{pickle_tag(prep)}.pkl"


def full_pickle(cache: Path, name: str, prep=None) -> Path:
    return cache / f"lessmann_full_{name.lower()}{pickle_tag(prep)}.pkl"


def full_oof_pickle(cache: Path, prep=None) -> Path:
    return cache / f"lessmann_full_oof{pickle_tag(prep)}.pkl"


class RobustNumericTransformer(BaseEstimator, TransformerMixin):
    """Clip numerics at the training-fold 1st/99th percentile, then log1p.

    log1p is applied only to columns that are non-negative after clipping
    and have pandas skew > 2 on the training fold. StandardScaler is a
    separate pipeline step.
    """

    def __init__(self, low_q=0.01, high_q=0.99, skew_threshold=2.0):
        self.low_q = low_q
        self.high_q = high_q
        self.skew_threshold = skew_threshold

    def fit(self, X, y=None):
        X = np.asarray(X, dtype=float)
        if X.ndim != 2:
            raise ValueError("expected a 2-d numeric array")
        self.n_features_in_ = X.shape[1]
        lo = np.nanpercentile(X, 100.0 * self.low_q, axis=0)
        hi = np.nanpercentile(X, 100.0 * self.high_q, axis=0)
        self.clip_lo_ = lo
        self.clip_hi_ = np.maximum(hi, lo)
        Xc = np.clip(X, self.clip_lo_, self.clip_hi_)
        mins = np.nanmin(Xc, axis=0)
        skews = np.empty(X.shape[1], dtype=float)
        for j in range(X.shape[1]):
            col = pd.Series(Xc[:, j])
            skews[j] = float(col.skew()) if col.notna().sum() > 2 else 0.0
        self.log_mask_ = (mins >= 0.0) & np.isfinite(skews) & (skews > self.skew_threshold)
        return self

    def transform(self, X):
        X = np.asarray(X, dtype=float)
        if X.shape[1] != self.n_features_in_:
            raise ValueError("feature count changed between fit and transform")
        X = np.clip(X, self.clip_lo_, self.clip_hi_)
        if self.log_mask_.any():
            X = np.array(X, copy=True)
            X[:, self.log_mask_] = np.log1p(np.maximum(X[:, self.log_mask_], 0.0))
        return X


def split_cols(X):
    num, cat = [], []
    for c in X.columns:
        if pd.api.types.is_numeric_dtype(X[c]):
            num.append(c)
        else:
            cat.append(c)
    return num, cat


def make_preps(X, prep_linear=None):
    prep_linear = PREP_LINEAR if prep_linear is None else prep_linear
    if prep_linear not in ("standard", "robust"):
        raise ValueError(f"PREP_LINEAR must be 'standard' or 'robust', got {prep_linear!r}")
    num, cat = split_cols(X)
    num_steps = [("imp", SimpleImputer(strategy="mean"))]
    if prep_linear == "robust":
        num_steps.append(("robust", RobustNumericTransformer()))
    num_steps.append(("sc", StandardScaler()))
    num_lin = Pipeline(num_steps)
    num_tree = SimpleImputer(strategy="mean")
    cat_oh = Pipeline([
        ("imp", SimpleImputer(strategy="most_frequent")),
        ("oh", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    cat_ord = Pipeline([
        ("imp", SimpleImputer(strategy="most_frequent")),
        ("ord", OrdinalEncoder(handle_unknown="use_encoded_value", unknown_value=-1)),
    ])
    if cat:
        lin = ColumnTransformer([("num", num_lin, num), ("cat", cat_oh, cat)])
        tree = ColumnTransformer([("num", num_tree, num), ("cat", cat_ord, cat)])
    else:
        lin = ColumnTransformer([("num", num_lin, num)])
        tree = ColumnTransformer([("num", num_tree, num)])
    return lin, tree


def model_space(lin, tree, mode: str):
    """mode='live': fixed hyperparams. mode='full': small grids for inner CV."""
    if mode == "live":
        return {
            "LR": Pipeline([("prep", lin), ("m", LogisticRegression(penalty=None, solver="lbfgs", max_iter=2000))]),
            "LR_L2": Pipeline([("prep", lin), ("m", LogisticRegression(C=1.0, solver="lbfgs", max_iter=2000))]),
            "RF": Pipeline([("prep", tree), ("m", RandomForestClassifier(n_estimators=300, max_depth=8, random_state=SEED, n_jobs=1))]),
            "HGB": Pipeline([("prep", tree), ("m", HistGradientBoostingClassifier(max_depth=3, max_iter=200, random_state=SEED))]),
            "MLP": Pipeline([("prep", lin), ("m", MLPClassifier(hidden_layer_sizes=(16,), solver="lbfgs", alpha=1.0, max_iter=2000, random_state=SEED))]),
        }, {}
    specs = {
        "LR": (Pipeline([("prep", lin), ("m", LogisticRegression(penalty=None, solver="lbfgs", max_iter=4000))]), {}),
        "LR_L2": (Pipeline([("prep", lin), ("m", LogisticRegression(solver="lbfgs", max_iter=4000))]),
                  {"m__C": [0.1, 1.0, 10.0]}),
        "RF": (Pipeline([("prep", tree), ("m", RandomForestClassifier(n_estimators=120, random_state=SEED, n_jobs=1))]),
               {"m__max_depth": [4, 8]}),
        "HGB": (Pipeline([("prep", tree), ("m", HistGradientBoostingClassifier(max_iter=80, random_state=SEED))]),
                {"m__max_depth": [3, 6]}),
        "MLP": (Pipeline([("prep", lin), ("m", MLPClassifier(hidden_layer_sizes=(16,), solver="lbfgs", alpha=1.0, max_iter=2000, random_state=SEED))]),
                {"m__alpha": [0.1, 1.0, 10.0]}),
    }
    return specs, "full"


def fit_predict_live(est, Xtr, ytr, Xte):
    est = clone(est)
    est.fit(Xtr, ytr)
    return est.predict_proba(Xte)[:, 1]


def fit_predict_full(est, grid, Xtr, ytr, Xte):
    inner = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    est = clone(est)
    if grid:
        gs = GridSearchCV(est, grid, cv=inner, scoring="roc_auc", n_jobs=-1)
        gs.fit(Xtr, ytr)
        base = clone(est).set_params(**gs.best_params_)
    else:
        base = est
    cal = CalibratedClassifierCV(base, method="sigmoid", cv=3)
    cal.fit(Xtr, ytr)
    return cal.predict_proba(Xte)[:, 1]


def run_dataset(name, X, y, n_repeats=5, mode="live"):
    cv = RepeatedStratifiedKFold(n_splits=2, n_repeats=n_repeats, random_state=SEED)
    rows = []
    oof_parts = []
    n_folds = n_repeats * 2
    for fold, (tr, te) in enumerate(cv.split(X, y)):
        Xtr, Xte = X.iloc[tr], X.iloc[te]
        ytr, yte = np.asarray(y)[tr], np.asarray(y)[te]
        lin, tree = make_preps(Xtr)
        space, kind = model_space(lin, tree, mode)
        probs = {}
        if kind == "full":
            for mname, (est, grid) in space.items():
                p = fit_predict_full(est, grid, Xtr, ytr, Xte)
                probs[mname] = p
                rows.append({"dataset": name, "fold": fold, "model": mname, **all_metrics(yte, p)})
        else:
            for mname, est in space.items():
                p = fit_predict_live(est, Xtr, ytr, Xte)
                probs[mname] = p
                rows.append({"dataset": name, "fold": fold, "model": mname, **all_metrics(yte, p)})
        avg = np.mean(np.vstack(list(probs.values())), axis=0)
        probs["AVG"] = avg
        rows.append({"dataset": name, "fold": fold, "model": "AVG", **all_metrics(yte, avg)})
        oof_parts.append(pd.DataFrame({"dataset": name, "fold": fold, "y": yte, **probs}))
        print(f"  {name} {mode} fold {fold + 1}/{n_folds} done")
    return pd.DataFrame(rows), pd.concat(oof_parts, ignore_index=True)


METRICS = ["AUC", "H", "PG04", "Brier"]


def mean_table(cv_tab):
    return cv_tab.groupby(["dataset", "model"])[METRICS].mean().round(4)


def rank_and_tests(cv_tab):
    mean_m = cv_tab.groupby(["dataset", "model"])[METRICS].mean().reset_index()
    rank_rows = []
    for ds, g in mean_m.groupby("dataset"):
        r = g.set_index("model")
        ranks = pd.DataFrame({
            "AUC": r["AUC"].rank(ascending=False),
            "H": r["H"].rank(ascending=False),
            "PG04": r["PG04"].rank(ascending=False),
            "Brier": r["Brier"].rank(ascending=True),
        })
        ranks["dataset"] = ds
        rank_rows.append(ranks.reset_index())
    ranks = pd.concat(rank_rows, ignore_index=True)
    avg_rank = ranks.groupby("model")[METRICS].mean()
    avg_rank["overall"] = avg_rank.mean(axis=1)
    avg_rank = avg_rank.sort_values("overall")

    per_ds = ranks.copy()
    per_ds["r"] = per_ds[METRICS].mean(axis=1)
    wide = per_ds.pivot(index="dataset", columns="model", values="r")
    rank_mat = wide.rank(axis=1, method="average")
    stat, p = friedmanchisquare(*[rank_mat[c].to_numpy() for c in rank_mat.columns])
    N, k = rank_mat.shape
    R = rank_mat.mean(axis=0)
    best = R.idxmin()
    se = np.sqrt(k * (k + 1) / (6.0 * N))
    holm = []
    pairs = []
    for m in R.index:
        if m == best:
            continue
        z = (R[m] - R[best]) / se
        pv = 2.0 * float(norm.sf(abs(z)))
        pairs.append((m, float(R[m]), float(z), pv))
    pairs.sort(key=lambda t: t[3])
    running = 0.0
    for i, (m, Ri, z, pv) in enumerate(pairs):
        p_h = min(1.0, max(running, (len(pairs) - i) * pv))
        running = p_h
        holm.append((m, Ri, z, pv, p_h))
    return {
        "avg_rank": avg_rank,
        "rank_mat": rank_mat,
        "friedman_chi2": float(stat),
        "friedman_p": float(p),
        "N": int(N),
        "k": int(k),
        "best": best,
        "R_best": float(R[best]),
        "holm": holm,
        "R": R,
    }


def print_tests(res, label):
    print(f"\n{label} — Average metric ranks (1 = best)")
    print(res["avg_rank"].round(2))
    friedman_r = res["R"].sort_values().to_frame("R")
    print(f"\n{label} — Friedman ranks (R used in Friedman and Holm; 1 = best)")
    print(friedman_r.round(2))
    print(f"\nDatasets: {list(res['rank_mat'].index)}")
    print(f"Friedman chi2={res['friedman_chi2']:.3f}  p={res['friedman_p']:.4f}  on Friedman ranks across {res['N']} datasets.")
    print(f"N = {res['N']} datasets gives this test little power. That is why Lessmann used eight.")
    print(f"\nLessmann Eq. (1) vs best={res['best']}: z=(R_i-R_best)/sqrt(k(k+1)/(6N)), k={res['k']}, N={res['N']}")
    print(f"  {res['best']:6s}  R={res['R_best']:.2f}  (best)")
    for m, Ri, z, pv, p_h in res["holm"]:
        print(f"  {m:6s}  R={Ri:.2f}  z={z:.3f}  p={pv:.3f}  p_Holm={p_h:.3f}  reject={p_h < 0.05}")


def expected_cost(y, p, c_fn, c_fp=1.0):
    t = 1.0 / (1.0 + c_fn)
    yhat = (np.asarray(p) >= t).astype(int)
    y = np.asarray(y).astype(int)
    fp = ((y == 0) & (yhat == 1)).mean()
    fn = ((y == 1) & (yhat == 0)).mean()
    return c_fp * fp + c_fn * fn


def cost_reductions(oof, grid=None):
    if grid is None:
        grid = np.arange(2, 51)
    models = [c for c in oof.columns if c not in ("dataset", "fold", "y")]
    rows = []
    for (ds, fold), g in oof.groupby(["dataset", "fold"]):
        y = g["y"].to_numpy()
        lr_p = g["LR"].to_numpy()
        for c in grid:
            lr_c = expected_cost(y, lr_p, c)
            for m in models:
                cst = expected_cost(y, g[m].to_numpy(), c)
                red = 0.0 if m == "LR" else 100.0 * (lr_c - cst) / max(lr_c, 1e-12)
                rows.append({"dataset": ds, "fold": fold, "model": m, "C": int(c), "red": red})
    red = pd.DataFrame(rows)
    by_ds = red.groupby(["dataset", "model", "C"], as_index=False)["red"].mean()
    overall = by_ds.groupby(["model", "C"], as_index=False)["red"].mean()
    return by_ds, overall


def pivot_metric(df, value, cuts=(2, 5, 10, 25, 50), ndigits=2):
    tab = df[df["C"].isin(cuts)].pivot(index="model", columns="C", values=value)
    tab.columns = [f"C={c}" for c in tab.columns]
    return tab.round(ndigits)


def pivot_cost(df, cuts=(2, 5, 10, 25, 50)):
    return pivot_metric(df, "red", cuts=cuts, ndigits=2)


def print_wide_tables(by_ds, overall, value, title, cuts=(2, 5, 10, 25, 50), ndigits=2):
    order = [d for d in ["GC", "AC", "GMC"] if d in set(by_ds["dataset"])]
    parts = {ds: pivot_metric(by_ds[by_ds["dataset"] == ds], value, cuts, ndigits) for ds in order}
    parts["mean"] = pivot_metric(overall, value, cuts, ndigits)
    wide = pd.concat(parts, axis=1)
    print(title)
    print(wide.to_string())
    return wide


def print_cost_tables(by_ds, overall, cuts=(2, 5, 10, 25, 50)):
    return print_wide_tables(
        by_ds, overall, "red",
        "% reduction in expected cost vs LR (fold mean; per dataset, then mean)",
        cuts=cuts, ndigits=2,
    )


def reject_rates(oof, grid=None):
    """Share of applicants predicted default at the Bayes threshold t=1/(1+C)."""
    if grid is None:
        grid = np.arange(2, 51)
    models = [c for c in oof.columns if c not in ("dataset", "fold", "y")]
    rows = []
    for (ds, fold), g in oof.groupby(["dataset", "fold"]):
        for c in grid:
            t = 1.0 / (1.0 + float(c))
            for m in models:
                rej = float((g[m].to_numpy() >= t).mean())
                rows.append({"dataset": ds, "fold": fold, "model": m, "C": int(c), "rej": rej})
    rej = pd.DataFrame(rows)
    by_ds = rej.groupby(["dataset", "model", "C"], as_index=False)["rej"].mean()
    overall = by_ds.groupby(["model", "C"], as_index=False)["rej"].mean()
    return by_ds, overall


def print_reject_tables(by_ds, overall, cuts=(2, 5, 10, 25, 50)):
    return print_wide_tables(
        by_ds, overall, "rej",
        "share of applicants rejected (fold mean; per dataset, then mean)",
        cuts=cuts, ndigits=3,
    )


def main():
    global PREP_LINEAR
    prep = os.environ.get("PREP_LINEAR", PREP_LINEAR)
    PREP_LINEAR = prep
    credit, cache = data_dirs()
    print("PREP_LINEAR", PREP_LINEAR)
    sets = load_gc_ac(credit)
    t0 = time.time()
    tabs = []
    oofs = []
    for name in ["GC", "AC"]:
        X, y = sets[name]
        print(f"\n=== {name}  5×2 CV  FULL (inner 5-fold + Platt) ===")
        tab, oof = run_dataset(name, X, y, n_repeats=5, mode="full")
        out = full_pickle(cache, name)
        tab.to_pickle(out)
        print("wrote", out)
        tabs.append(tab)
        oofs.append(oof)
    oof_path = full_oof_pickle(cache)
    pd.concat(oofs, ignore_index=True).to_pickle(oof_path)
    print("wrote", oof_path)
    elapsed = time.time() - t0
    cv_tab = pd.concat(tabs, ignore_index=True)
    print("\nFULL mean metrics")
    print(mean_table(cv_tab))
    print_tests(rank_and_tests(cv_tab), "FULL")
    print(f"\nfull protocol runtime {elapsed:.1f}s")


if __name__ == "__main__":
    main()
