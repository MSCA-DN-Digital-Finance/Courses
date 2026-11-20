"""Shared helpers for the course labs: loading data/weights and drawing maps."""
import os
import numpy as np
import geopandas as gpd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from libpysal.weights import W

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")
FIG = os.path.join(HERE, "..", "figures")
OUT = os.path.join(HERE, "..", "outputs")
os.makedirs(FIG, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

# LISA quadrant colours (conventional GeoDa scheme)
LISA_COLORS = {"High-High": "#C0392B", "Low-Low": "#2E6DB4",
               "High-Low": "#F1948A", "Low-High": "#85C1E9",
               "Not significant": "#E5E5E5"}
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                     "axes.titlesize": 12, "axes.titleweight": "bold"})


def load():
    """Return (GeoDataFrame, row-standardised Queen W) in identical order."""
    g = gpd.read_file(os.path.join(DATA, "ro_course.gpkg"))
    nb = {}
    with open(os.path.join(DATA, "ro_course_queen.gal")) as f:
        f.readline()
        lines = f.read().split("\n")
    for k in range(0, len(lines) - 1, 2):
        i, _ = lines[k].split()
        nb[int(i)] = [int(x) for x in lines[k + 1].split()] if lines[k + 1] else []
    w = W(nb, id_order=g["siruta"].tolist(), silence_warnings=True)
    w.transform = "r"
    return g, w


_CTY = {}


def counties(g):
    """County outlines; a small buffer closes slivers left by simplification."""
    if "b" not in _CTY:
        gb = g[["county", "geometry"]].copy()
        gb["geometry"] = gb.buffer(80)
        _CTY["b"] = gb.dissolve("county").buffer(-80).boundary
    return _CTY["b"]


def base_map(ax, g, title=None):
    ax.set_axis_off()
    counties(g).plot(ax=ax, color="#555555", linewidth=0.35)
    if title:
        ax.set_title(title, loc="left")


def cat_map(g, col, colors, title, fname, legend_title=None):
    fig, ax = plt.subplots(figsize=(8, 5.6))
    for lab, c in colors.items():
        sub = g[g[col] == lab]
        if len(sub):
            sub.plot(ax=ax, color=c, linewidth=0)
    base_map(ax, g, title)
    handles = [Patch(color=c, label=f"{k} ({(g[col]==k).sum()})") for k, c in colors.items()]
    ax.legend(handles=handles, loc="lower left", frameon=False, title=legend_title, fontsize=8)
    fig.tight_layout()
    fig.savefig(os.path.join(FIG, fname), dpi=170)
    plt.close(fig)


def num_map(g, col, title, fname, cmap="YlOrRd", vmin=None, vmax=None, label=None, ax=None):
    own = ax is None
    if own:
        fig, ax = plt.subplots(figsize=(8, 5.6))
    g.plot(column=col, ax=ax, cmap=cmap, linewidth=0, vmin=vmin, vmax=vmax, legend=True,
           legend_kwds={"shrink": 0.6, "label": label or ""})
    base_map(ax, g, title)
    if own:
        fig.tight_layout()
        fig.savefig(os.path.join(FIG, fname), dpi=170)
        plt.close(fig)


def fdr(p, alpha=0.05):
    """Benjamini-Hochberg: boolean mask of discoveries."""
    p = np.asarray(p)
    n = len(p)
    o = np.argsort(p)
    thresh = alpha * np.arange(1, n + 1) / n
    ok = p[o] <= thresh
    k = np.max(np.where(ok)[0]) + 1 if ok.any() else 0
    mask = np.zeros(n, bool)
    mask[o[:k]] = True
    return mask
