#!/usr/bin/env python3
"""KMZ / Nagel RFF + kernel precompute (steps 1–3 and the RFF placebo).

Forecasts of R_{t+1} use information through month t only:
- predictors x_t (infl lagged one extra month);
- training pairs (x_{t-T}, R_{t-T+1}), ..., (x_{t-1}, R_t);
- vol-mom weight 12/78 sits on R_t (Nagel eq. 14).
"""
from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 34104
GAMMA = 2.0
T_DEFAULT = 12
P_GRID = (2, 6, 12, 60, 120, 600, 1200, 6000, 12000)
Z_RIDGE = (1e-3, 1e-2, 1e-1, 1.0, 10.0, 100.0, 1e3)
Z_LABELS = [*(f"{z:g}" for z in Z_RIDGE), "ridgeless"]
N_DRAWS_GRID = 20
N_DRAWS_HEAD = 100
N_PLACEBO_PATHS = 20
N_PLACEBO_PATH_DRAWS = 5  # range of t-stats; headline path still uses 100 draws
P_HEAD = 12000
VOLMOM_SCALE = 0.05
KERNEL_RIDGE = 1e-10
PRED_NAMES = [
    "dfy", "dfr", "infl", "svar", "lty", "tbl", "ltr", "tms",
    "log_dp", "log_dy", "log_ep", "log_de", "b/m", "ntis", "R_t",
]
EVAL_MAIN = (193001, 202012)
EVAL_POST = (202101, 202512)


def repo_root() -> Path:
    here = Path(__file__).resolve().parent
    for base in [here, *here.parents]:
        if (base / "data" / "goyal_welch" / "goyal_welch_2025.csv").exists() or (
            base / "data" / "README.md"
        ).exists():
            return base
    return here.parent


def cache_dir() -> Path:
    d = repo_root() / "data" / "cache"
    d.mkdir(parents=True, exist_ok=True)
    return d


def cache_path() -> Path:
    return cache_dir() / "kmz_nagel.pkl"


def yyyymm_to_period(yyyymm: np.ndarray) -> pd.PeriodIndex:
    s = pd.Series(yyyymm.astype(int).astype(str))
    return pd.PeriodIndex(s, freq="M")


def load_goyal() -> pd.DataFrame:
    path = repo_root() / "data" / "goyal_welch" / "goyal_welch_2025.csv"
    df = pd.read_csv(path)
    n = len(df)
    print("load", path, "rows", n, "cols", len(df.columns), flush=True)
    for col in ("yyyymm", "ret", "Rfree"):
        if col not in df.columns:
            raise SystemExit(f"{path.name} is not monthly Welch–Goyal data: missing {col}")
    if n < 100:
        raise SystemExit(f"{path.name} has {n} rows — this looks like the variable list, not the monthly file")
    if n not in (1859, 1860):
        raise SystemExit(f"{path.name} has {n} rows; expected 1,859 monthly rows (1871-01 to 2025-12)")
    if n != 1859:
        print(f"note: brief says 1,859 rows; file has {n} (1871-01 through 2025-12 is 1,860 months)", flush=True)
    return df


def build_design(df: pd.DataFrame, return_std: bool = False):
    """Aligned design: row t uses info through month t to forecast R_{t+1}.

    X[t] is the 15 standardized predictors dated t (infl is CPI of t-1).
    y[t] is the excess return of month t. The regression target at t is y[t+1].
    y_fit[t] is the estimation target for the pair that ends at t (y[t] or y[t]/σ_{t-1}).
    """
    raw = df.copy()
    raw["yyyymm"] = raw["yyyymm"].astype(int)
    raw["R"] = raw["ret"] - raw["Rfree"]
    raw["infl_pub"] = raw["infl"].shift(1)
    for src, dst in [("d/p", "log_dp"), ("d/y", "log_dy"), ("e/p", "log_ep"), ("d/e", "log_de")]:
        if (raw[src] <= 0).any():
            raise SystemExit(f"non-positive {src}; logs are not safe")
        raw[dst] = np.log(raw[src])

    cols_raw = [
        "dfy", "dfr", "infl_pub", "svar", "lty", "tbl", "ltr", "tms",
        "log_dp", "log_dy", "log_ep", "log_de", "b/m", "ntis", "R",
    ]
    need = cols_raw + ["yyyymm", "ret", "Rfree"]
    joint = raw.loc[raw["yyyymm"] >= 192612, need].copy()
    if joint[cols_raw + ["ret", "Rfree"]].isna().any().any():
        raise SystemExit("NaNs in the 1926-12 to end joint sample")
    n = len(joint)
    print(f"joint 1926-12 to {int(joint['yyyymm'].iloc[-1])} : {n} months (spec 1,189 through 2025-12)", flush=True)
    if int(joint["yyyymm"].iloc[-1]) == 202512 and n != 1189:
        raise SystemExit(f"expected 1,189 joint months, got {n}")

    ym = joint["yyyymm"].to_numpy()
    y = joint["R"].to_numpy(float)
    X_raw = joint[cols_raw].to_numpy(float)

    # Expanding-window std through t, min 36 months, no future.
    X = np.full_like(X_raw, np.nan)
    for j in range(X_raw.shape[1]):
        s = pd.Series(X_raw[:, j]).expanding(min_periods=36).std(ddof=1).to_numpy()
        s = np.where(np.isfinite(s) & (s > 1e-12), s, np.nan)
        X[:, j] = X_raw[:, j] / s

    # Trailing 12-month uncentered second moment of returns, through t.
    r2 = pd.Series(y ** 2).rolling(12, min_periods=12).mean().to_numpy()
    sigma = np.sqrt(r2)

    # y_fit[t] = target used with feature row t, i.e. a transform of y[t+1]
    # known-at-t scale: σ_t uses R_t ... R_{t-11}, never R_{t+1}.
    y_fit = y.copy()
    if return_std:
        y_fit = np.concatenate([y[1:] / sigma[:-1], [np.nan]])
    else:
        y_fit = np.concatenate([y[1:], [np.nan]])

    ok = np.isfinite(X).all(axis=1) & np.isfinite(sigma)
    print(f"KMZ_RETURN_STD={return_std}  rows with 36m predictor std and 12m vol: {int(ok.sum())}", flush=True)
    return {
        "yyyymm": ym,
        "y": y,
        "y_fit": y_fit,
        "sigma": sigma,
        "X": X,
        "ok": ok,
        "names": list(PRED_NAMES),
        "return_std": bool(return_std),
    }


def rolling_dual_forecast(S, y_fit, T, z_list):
    """yhat[i, t] forecasts the target at t+1 for z_list[i] (None = ridgeless).

    Training features are S_{t-T},...,S_{t-1}; training targets are y_fit at
    those rows (y_fit[s] = f(R_{s+1})). Test feature is S_t. Never reads
    y[t+1] or S after t.
    """
    N = S.shape[0]
    n_z = len(z_list)
    yhat = np.full((n_z, N), np.nan)
    n_pinv = 0
    eye = np.eye(T)
    with np.errstate(all="ignore"):
        for t in range(T, N - 1):
            Z = S[t - T : t]
            r = y_fit[t - T : t]
            if not np.isfinite(r).all() or not np.isfinite(Z).all():
                continue
            sd = Z.std(axis=0, ddof=0)
            sd = np.where(sd < 1e-15, 1.0, sd)
            Zs = Z / sd
            G = Zs @ Zs.T
            st = S[t] / sd
            kvec = Zs @ st
            for i, z in enumerate(z_list):
                if z is None:
                    try:
                        alpha = np.linalg.solve(G, r)
                    except np.linalg.LinAlgError:
                        alpha = np.linalg.pinv(G) @ r
                        n_pinv += 1
                else:
                    alpha = np.linalg.solve(G + z * eye, r)
                yhat[i, t] = float(kvec @ alpha)
    return yhat, n_pinv


def rolling_kernel_forecast(X, y_fit, T, gamma=GAMMA):
    """Ridgeless Gaussian kernel on standardized x, same 12-month window."""
    N, K = X.shape
    yhat = np.full(N, np.nan)
    n_ridge = 0
    coef = (gamma ** 2) / 2.0
    eye = np.eye(T)
    with np.errstate(all="ignore"):
        for t in range(T, N - 1):
            Xt = X[t - T : t]
            r = y_fit[t - T : t]
            if not np.isfinite(r).all() or not np.isfinite(Xt).all():
                continue
            d2 = ((Xt[:, None, :] - Xt[None, :, :]) ** 2).sum(axis=2)
            Kmat = np.exp(-coef * d2)
            try:
                alpha = np.linalg.solve(Kmat, r)
            except np.linalg.LinAlgError:
                alpha = np.linalg.solve(Kmat + KERNEL_RIDGE * eye, r)
                n_ridge += 1
            d2t = ((Xt - X[t]) ** 2).sum(axis=1)
            kt = np.exp(-coef * d2t)
            yhat[t] = float(kt @ alpha)
    return yhat, n_ridge


def volmom_forecast(X, y, T):
    """Nagel eq. 14. Weight (12-k)/78 on R_{t-k}; k=0 is R_t (most recent)."""
    N = y.shape[0]
    yhat = np.full(N, np.nan)
    w = np.array([(12 - k) / 78.0 for k in range(12)], dtype=float)
    assert abs(w[0] - 12.0 / 78.0) < 1e-15
    assert abs(w.sum() - 1.0) < 1e-12
    for t in range(T, N - 1):
        # training window of predictors: x_{t-T},...,x_{t-1}
        Xt = X[t - T : t]
        if not np.isfinite(Xt).all():
            continue
        sigx2 = float(Xt.var(axis=0, ddof=0).mean())
        if sigx2 < 1e-18:
            continue
        # R_t, R_{t-1}, ..., R_{t-11}
        rets = np.array([y[t - k] for k in range(12)])
        yhat[t] = VOLMOM_SCALE * (1.0 / sigx2) * float(w @ rets)
    return yhat


def rff_matrix(X, omega, gamma=GAMMA):
    """S_{i,t} = [sin(γ ω_i'x_t), cos(γ ω_i'x_t)], interleaved, P = 2 * n_freq."""
    Xc = np.nan_to_num(X, nan=0.0, posinf=0.0, neginf=0.0)
    with np.errstate(all="ignore"):
        proj = Xc @ omega.T
        n, m = proj.shape
        S = np.empty((n, 2 * m), dtype=float)
        S[:, 0::2] = np.sin(gamma * proj)
        S[:, 1::2] = np.cos(gamma * proj)
    # Keep rows with invalid predictors as NaN so rolling windows skip them.
    bad = ~np.isfinite(X).all(axis=1)
    S[bad] = np.nan
    return S


def strategy_from_yhat(yhat, y, return_std, sigma):
    """Position at t times realized excess return R_{t+1}.

    yhat[t] forecasts y_fit[t] ≡ f(R_{t+1}). If returns were standardized,
    convert the forecast back to return units with σ_t (known at t).
    """
    N = y.shape[0]
    strat = np.full(N, np.nan)
    pos = yhat.copy()
    if return_std:
        pos = yhat * sigma
    # strat[t+1] = position_t * R_{t+1}
    strat[1:] = pos[:-1] * y[1:]
    return pos, strat


def eval_mask(yyyymm, start, end):
    return (yyyymm >= start) & (yyyymm <= end)


def r2_oos(y, yhat, mask):
    """R²_OOS vs a trailing expanding mean that uses only past returns."""
    n = y.shape[0]
    mu = np.full(n, np.nan)
    csum = np.cumsum(y)
    cnt = np.arange(1, n + 1, dtype=float)
    # expanding mean through t-1, used when forecasting t (index t)
    mu[1:] = csum[:-1] / cnt[:-1]
    m = mask & np.isfinite(yhat) & np.isfinite(y) & np.isfinite(mu)
    e = y[m] - yhat[m]
    d = y[m] - mu[m]
    sse, sst = float(np.dot(e, e)), float(np.dot(d, d))
    return np.nan if sst <= 0 else 1.0 - sse / sst


def sharpe(strat, mask):
    s = strat[mask]
    s = s[np.isfinite(s)]
    if s.size < 12 or s.std(ddof=1) == 0:
        return np.nan
    return float(s.mean() / s.std(ddof=1) * np.sqrt(12.0))


def ols_hac(y, X, lags=6):
    """OLS with Newey–West HAC s.e. X should already include a constant."""
    y = np.asarray(y, float)
    X = np.asarray(X, float)
    n, k = X.shape
    with np.errstate(all="ignore"):
        xtx = X.T @ X
        beta = np.linalg.solve(xtx, X.T @ y)
        e = y - X @ beta
        u = e[:, None] * X
        S = u.T @ u
        for lag in range(1, lags + 1):
            w = 1.0 - lag / (lags + 1.0)
            G = u[lag:].T @ u[:-lag]
            S += w * (G + G.T)
        inv = np.linalg.inv(xtx)
        V = inv @ S @ inv
    se = np.sqrt(np.maximum(np.diag(V), 0.0))
    tstat = np.divide(beta, se, out=np.full_like(beta, np.nan), where=se > 0)
    return {"beta": beta, "se": se, "tstat": tstat, "resid": e, "n": n}


def capm_stats(strat, mkt, mask, lags=6):
    m = mask & np.isfinite(strat) & np.isfinite(mkt)
    y = strat[m]
    x = np.column_stack([np.ones(y.size), mkt[m]])
    fit = ols_hac(y, x, lags=lags)
    a, se_a, t_a = fit["beta"][0], fit["se"][0], fit["tstat"][0]
    resid = fit["resid"]
    sig = float(resid.std(ddof=1))
    ir = np.nan if sig == 0 else (a / sig) * np.sqrt(12.0)
    return {
        "alpha_m": float(a),
        "alpha_ann": float(12.0 * a),
        "tstat": float(t_a),
        "ir": float(ir),
        "n": int(fit["n"]),
    }


def spanning_stats(strat, mkt, other, mask, lags=6):
    m = mask & np.isfinite(strat) & np.isfinite(mkt) & np.isfinite(other)
    y = strat[m]
    x = np.column_stack([np.ones(y.size), mkt[m], other[m]])
    fit = ols_hac(y, x, lags=lags)
    a, t_a = fit["beta"][0], fit["tstat"][0]
    return {"alpha_m": float(a), "alpha_ann": float(12.0 * a), "tstat": float(t_a), "n": int(fit["n"])}


def assert_no_lookahead():
    """Tiny synthetic check: training target for forecast at t is never y[t+1]."""
    rng = np.random.default_rng(0)
    N, P, T = 40, 6, 12
    X = rng.normal(size=(N, 3))
    y = rng.normal(size=N)
    y_fit = np.concatenate([y[1:], [np.nan]])
    omega = rng.normal(size=(P // 2, 3))
    S = rff_matrix(X, omega)
    yhat, _ = rolling_dual_forecast(S, y_fit, T, z_list=[None])
    yhat = yhat[0]
    t = 20
    # rebuild one window and confirm the target vector is y_fit[t-T:t] == y[t-T+1:t+1]
    targ = y_fit[t - T : t]
    assert np.allclose(targ, y[t - T + 1 : t + 1])
    assert t + 1 not in range(t - T + 1, t + 1)
    vm = volmom_forecast(X, y, T)
    w0 = 12.0 / 78.0
    # manual eq. 14 at t=20
    Xt = X[t - T : t]
    sigx2 = float(Xt.var(axis=0, ddof=0).mean())
    manual = 0.05 / sigx2 * sum(((12 - k) / 78.0) * y[t - k] for k in range(12))
    assert abs(manual - vm[t]) < 1e-12
    assert abs(w0 - 12.0 / 78.0) < 1e-15
    print("lookahead asserts ok: targets end at R_t; vol-mom 12/78 on R_t", flush=True)


def draw_omegas(rng, n_draws, n_freq, k):
    return [rng.normal(size=(n_freq, k)) for _ in range(n_draws)]


def average_forecast(X, y_fit, omegas, P, T, z_list):
    n_z, N = len(z_list), X.shape[0]
    acc = np.zeros((n_z, N))
    n_ok = np.zeros((n_z, N))
    n_pinv = 0
    for omega in omegas:
        S = rff_matrix(X, omega)[:, :P]
        yhat, npv = rolling_dual_forecast(S, y_fit, T, z_list)
        n_pinv += npv
        m = np.isfinite(yhat)
        acc[m] += yhat[m]
        n_ok[m] += 1
    out = np.full((n_z, N), np.nan)
    m = n_ok > 0
    out[m] = acc[m] / n_ok[m]
    return out, n_pinv


def placebo_returns(y, rng):
    xi = rng.normal(loc=0.0, scale=0.1, size=y.shape[0])  # var 0.01
    tilde = y.copy()
    tilde = y + xi
    tilde[1:] -= 0.2 * xi[:-1]
    tilde[2:] -= 0.2 * xi[:-2]
    return tilde


def replace_lagged_return(pack, tilde):
    """Keep 14 real predictors; swap the lagged-market column and the y series."""
    X = pack["X"].copy()
    X[:, -1] = np.nan
    # lagged market is R_t, already the last column of raw X before expanding std.
    # Recompute expanding std for that column from tilde, 36 months.
    s = pd.Series(tilde).expanding(min_periods=36).std(ddof=1).to_numpy()
    X[:, -1] = tilde / s
    y_fit = np.concatenate([tilde[1:], [np.nan]])
    if pack["return_std"]:
        r2 = pd.Series(tilde ** 2).rolling(12, min_periods=12).mean().to_numpy()
        sigma = np.sqrt(r2)
        y_fit = np.concatenate([tilde[1:] / sigma[:-1], [np.nan]])
    else:
        sigma = pack["sigma"]
    return X, tilde, y_fit, sigma


def summarize_strategy(yhat, y, sigma, return_std, yyyymm, mkt=None):
    pos, strat = strategy_from_yhat(yhat, y, return_std, sigma)
    if mkt is None:
        mkt = y
    yhat_on_ret = np.r_[np.nan, pos[:-1]]
    out = {}
    for label, lo, hi in (("main", *EVAL_MAIN), ("post", *EVAL_POST)):
        mask = eval_mask(yyyymm, lo, hi) & np.isfinite(strat)
        out[label] = {
            "sharpe": sharpe(strat, mask),
            "r2": r2_oos(y, yhat_on_ret, mask),
            "capm": capm_stats(strat, mkt, mask),
            "n": int(mask.sum()),
        }
    out["yhat"] = yhat
    out["strat"] = strat
    out["pos"] = pos
    return out


def run_one_std(df, return_std, omegas_grid, omegas_head, placebo_rng_seed):
    pack = build_design(df, return_std=return_std)
    X, y, y_fit, sigma, ym = pack["X"], pack["y"], pack["y_fit"], pack["sigma"], pack["yyyymm"]
    T = T_DEFAULT
    n_freq = P_HEAD // 2

    z_list = [float(z) for z in Z_RIDGE] + [None]
    sharpe_grid = np.full((len(Z_LABELS), len(P_GRID)), np.nan)
    r2_grid = np.full_like(sharpe_grid, np.nan)
    t0g = time.time()
    for j, P in enumerate(P_GRID):
        yhats, _ = average_forecast(X, y_fit, omegas_grid, P, T, z_list)
        for i in range(len(z_list)):
            pos, strat = strategy_from_yhat(yhats[i], y, return_std, sigma)
            yhat_ret = np.r_[np.nan, pos[:-1]]
            mask = eval_mask(ym, *EVAL_MAIN) & np.isfinite(strat)
            sharpe_grid[i, j] = sharpe(strat, mask)
            r2_grid[i, j] = r2_oos(y, yhat_ret, mask)
        print(f"  grid P={P}  KMZ_RETURN_STD={return_std}  {time.time()-t0g:.1f}s", flush=True)

    yhat_rff, _ = average_forecast(X, y_fit, omegas_head, P_HEAD, T, [None])
    yhat_rff = yhat_rff[0]
    yhat_ker, n_kridge = rolling_kernel_forecast(X, y_fit, T)
    yhat_vm = volmom_forecast(X, y, T)
    print(f"  headline+kernel+volmom  KMZ_RETURN_STD={return_std}  {time.time()-t0g:.1f}s", flush=True)
    rff = summarize_strategy(yhat_rff, y, sigma, return_std, ym)
    ker = summarize_strategy(yhat_ker, y, sigma, return_std, ym)
    vm = summarize_strategy(yhat_vm, y, sigma, False, ym)  # vol-mom always uses raw R

    def corr_fcst(a, b, lo, hi):
        ret_m = eval_mask(ym, lo, hi)
        made_at = np.zeros_like(ret_m)
        made_at[:-1] = ret_m[1:]
        m = made_at & np.isfinite(a) & np.isfinite(b)
        if m.sum() < 3:
            return np.nan
        return float(np.corrcoef(a[m], b[m])[0, 1])

    corr_main = corr_fcst(yhat_rff, yhat_ker, *EVAL_MAIN)
    corr_post = corr_fcst(yhat_rff, yhat_ker, *EVAL_POST)

    span = {}
    for label, lo, hi in (("main", *EVAL_MAIN), ("post", *EVAL_POST)):
        mask = eval_mask(ym, lo, hi)
        span[label] = {
            "rff_on_ker": spanning_stats(rff["strat"], y, ker["strat"], mask),
            "rff_on_vm": spanning_stats(rff["strat"], y, vm["strat"], mask),
        }

    # Placebo: headline path + 20 paths (20 RFF draws each, same omegas_grid)
    rng_p = np.random.default_rng(placebo_rng_seed)
    tilde = placebo_returns(y, rng_p)
    Xp, yp, y_fit_p, sig_p = replace_lagged_return(pack, tilde)
    yhat_p, _ = average_forecast(Xp, y_fit_p, omegas_head, P_HEAD, T, [None])
    placebo_head = summarize_strategy(yhat_p[0], yp, sig_p, return_std, ym, mkt=yp)

    path_t = []
    path_ir = []
    omegas_paths = omegas_grid[:N_PLACEBO_PATH_DRAWS]
    for p in range(N_PLACEBO_PATHS):
        rng_i = np.random.default_rng(placebo_rng_seed + 1 + p)
        ti = placebo_returns(y, rng_i)
        Xi, yi, yfi, si = replace_lagged_return(pack, ti)
        yh, _ = average_forecast(Xi, yfi, omegas_paths, P_HEAD, T, [None])
        sm = summarize_strategy(yh[0], yi, si, return_std, ym, mkt=yi)
        path_t.append(sm["main"]["capm"]["tstat"])
        path_ir.append(sm["main"]["capm"]["ir"])
    print(f"  placebo  KMZ_RETURN_STD={return_std}  {time.time()-t0g:.1f}s", flush=True)

    return {
        "return_std": return_std,
        "yyyymm": ym,
        "y": y,
        "X": X,
        "sigma": sigma,
        "grid": {
            "P": list(P_GRID),
            "z": list(Z_LABELS),
            "sharpe_main": sharpe_grid,
            "r2_main": r2_grid,
            "n_draws": N_DRAWS_GRID,
        },
        "rff": rff,
        "kernel": ker,
        "kernel_n_ridge": int(n_kridge),
        "volmom": vm,
        "corr_main": corr_main,
        "corr_post": corr_post,
        "span": span,
        "placebo_head": placebo_head,
        "placebo_tilde": tilde,
        "placebo_paths_t": path_t,
        "placebo_paths_ir": path_ir,
        "n_head_draws": N_DRAWS_HEAD,
        "n_placebo_path_draws": N_PLACEBO_PATH_DRAWS,
        "grid_seconds": time.time() - t0g,
    }


def main():
    assert_no_lookahead()
    df = load_goyal()
    rng = np.random.default_rng(SEED)
    n_freq = P_HEAD // 2
    k = len(PRED_NAMES)
    omegas_head = draw_omegas(rng, N_DRAWS_HEAD, n_freq, k)
    omegas_grid = omegas_head[:N_DRAWS_GRID]
    t0 = time.time()
    out = {
        "seed": SEED,
        "T": T_DEFAULT,
        "gamma": GAMMA,
        "P_head": P_HEAD,
        "n_draws_grid": N_DRAWS_GRID,
        "n_draws_head": N_DRAWS_HEAD,
        "pred_names": PRED_NAMES,
        "eval_main": EVAL_MAIN,
        "eval_post": EVAL_POST,
        "by_std": {},
    }
    for return_std in (False, True):
        print(f"\n=== KMZ_RETURN_STD={return_std} ===", flush=True)
        out["by_std"][return_std] = run_one_std(
            df, return_std, omegas_grid, omegas_head, placebo_rng_seed=SEED + 17
        )
    out["runtime_s"] = time.time() - t0
    path = cache_path()
    pd.to_pickle(out, path)
    print("wrote", path, f"precompute runtime {out['runtime_s']:.1f}s", flush=True)


if __name__ == "__main__":
    main()
