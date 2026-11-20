"""
setup_check.py
------------------------------------------------------------------
Preparation steps for the Python labs. Run this first.

  Step 1  Python version
  Step 2  Load every library used in the labs (optionally install the
          missing ones with --install)
  Step 3  Check that the data files are in ../data
  Step 4  Load the data: course GeoPackage + Queen weights (the same
          loader the labs use), and the raw CSV
  Step 5  Print a short summary of what was loaded

Usage (from the python/ folder):
    python setup_check.py             # check only
    python setup_check.py --install   # pip-install missing packages first
"""
import argparse
import importlib
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..", "data")

# import name -> pip name, and where it is used
PACKAGES = [
    ("numpy", "numpy", "all labs"),
    ("pandas", "pandas", "all labs"),
    ("scipy", "scipy", "all labs"),
    ("matplotlib", "matplotlib", "all figures"),
    ("shapely", "shapely", "geometry"),
    ("pyproj", "pyproj", "coordinate systems"),
    ("pyogrio", "pyogrio", "fast reading of shapefile / GeoPackage"),
    ("geopandas", "geopandas", "spatial data frames"),
    ("mapclassify", "mapclassify", "map classification"),
    ("libpysal", "libpysal", "spatial weights"),
    ("esda", "esda", "Moran, LISA, Gi*, EB rates (labs 1-3)"),
    ("spreg", "spreg", "spatial regression (lab 2)"),
    ("sklearn", "scikit-learn", "Isolation Forest, LOF (lab 2)"),
    ("PIL", "pillow", "cropping figures (run_all)"),
    ("h3", "h3", "H3 grid (lab 5)"),
    ("duckdb", "duckdb", "SQL on Parquet (lab 5)"),
    ("pyarrow", "pyarrow", "Parquet files (lab 5)"),
]

DATA_FILES = [
    ("ro_course.gpkg", True, "joined + simplified ATU layer (all labs)"),
    ("ro_course_queen.gal", True, "Queen contiguity weights (all labs)"),
    ("ro_vaccines.csv", True, "original attribute table"),
    ("ro_atu.shp", False, "original shapefile, only for 00_prepare_data.py"),
]


def step(n, title):
    print(f"\n[Step {n}] {title}\n" + "-" * 60)


def main(install):
    ok = True

    step(1, "Python version")
    v = sys.version_info
    print(f"Python {v.major}.{v.minor}.{v.micro}")
    if v < (3, 10):
        print("  WARNING: Python 3.10 or newer is recommended")

    step(2, "Libraries")
    missing = []
    for mod, pipname, use in PACKAGES:
        try:
            m = importlib.import_module(mod)
            print(f"  ok       {mod:<12} {getattr(m, '__version__', ''):<10} {use}")
        except ImportError:
            print(f"  MISSING  {mod:<12} {'':<10} {use}   (pip install {pipname})")
            missing.append(pipname)
    if missing and install:
        print(f"\nInstalling: {' '.join(missing)}")
        subprocess.run([sys.executable, "-m", "pip", "install", *missing], check=False)
        importlib.invalidate_caches()
        still = []
        for mod, pipname, _ in PACKAGES:
            if pipname in missing:
                try:
                    importlib.import_module(mod)
                except ImportError:
                    still.append(pipname)
        missing = still
    if missing:
        ok = False
        print(f"\n  -> install the missing packages:  pip install {' '.join(missing)}"
              f"\n     or:  python setup_check.py --install   (or: pip install -r requirements.txt)")

    step(3, "Data files in ../data")
    for f, required, what in DATA_FILES:
        p = os.path.join(DATA, f)
        if os.path.exists(p):
            print(f"  ok       {f:<22} {os.path.getsize(p)/1e6:7.1f} MB  {what}")
        else:
            print(f"  {'MISSING ' if required else 'absent  '} {f:<22} {'':>10}  {what}")
            ok = ok and not required
    if not os.path.exists(os.path.join(DATA, "ro_course.gpkg")) and os.path.exists(os.path.join(DATA, "ro_atu.shp")):
        print("  -> build the course data first:  python 00_prepare_data.py")

    if not ok:
        print("\nStopping before loading data: see the messages above.")
        return 1

    step(4, "Loading the data (same loader as the labs: common.load())")
    try:
        import pandas as pd
        from common import load
        g, w = load()
        raw = pd.read_csv(os.path.join(DATA, "ro_vaccines.csv"))
    except Exception as e:                                  # noqa: BLE001
        print(f"  FAILED: {e}")
        return 1
    print(f"  GeoPackage: {len(g):,} ATUs x {g.shape[1] - 1} attribute columns + geometry, CRS = {g.crs.name}")
    print(f"  Weights:    {w.n:,} units, mean {w.mean_neighbors:.2f} neighbours, "
          f"islands = {len(w.islands)}, transform = {w.transform}")
    print(f"  Raw CSV:    {raw.shape[0]:,} rows x {raw.shape[1]} columns")
    same = (g["siruta"].values == list(w.id_order)).all()
    print(f"  Row order of data and weights identical: {same}")
    ok = ok and same

    step(5, "Summary of the main variables")
    cols = ["pop", "inc_w3", "inc_w4", "vac_may", "vac_oct", "vac_change", "inc_change"]
    print(g[cols].describe().T[["mean", "50%", "min", "max"]].round(2).to_string())
    print(f"\n  Counties: {g['county'].nunique()}  |  missing values in these columns: "
          f"{int(g[cols].isna().sum().sum())}")

    print("\n" + ("All set: run the labs (python 01_spatial_anomalies.py ... or python run_all.py)"
                  if ok else "Some checks failed: see the messages above."))
    return 0 if ok else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--install", action="store_true", help="pip-install missing packages")
    sys.exit(main(ap.parse_args().install))
