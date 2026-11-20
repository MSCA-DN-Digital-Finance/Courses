"""
run_all.py
------------------------------------------------------------------
Runs every Python lab in order and regenerates all figures and tables,
then writes cropped copies of the figures (white margins removed, as
used in the slides) to figures/slides/.

Usage (from the python/ folder):
    python run_all.py              # labs 01-05 + cropping
    python run_all.py --prep       # also rebuild the GeoPackage from the
                                   # original shapefile (needs data/ro_atu.*)
    python run_all.py --only 01 03 # run selected labs only
    python run_all.py --trim-only  # just re-crop existing figures
    python run_all.py --skip-check # do not run setup_check.py first
"""
import argparse
import glob
import os
import subprocess
import sys
import time

from PIL import Image, ImageChops

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, "..", "figures")
SLIDES = os.path.join(FIG, "slides")
LABS = ["01_spatial_anomalies.py", "02_model_based_anomalies.py",
        "03_spatiotemporal_two_waves.py", "04_spatiotemporal_surveillance_sim.py",
        "05_spatial_big_data.py"]          # 05 needs the outputs of 04


def trim(src, dst, pad=10):
    """Crop the uniform white border around a figure, keeping `pad` pixels."""
    im = Image.open(src).convert("RGB")
    box = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
    if box:
        im = im.crop((max(box[0] - pad, 0), max(box[1] - pad, 0),
                      min(box[2] + pad, im.width), min(box[3] + pad, im.height)))
    im.save(dst)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prep", action="store_true", help="run 00_prepare_data.py first")
    ap.add_argument("--only", nargs="*", help="lab numbers to run, e.g. 01 04 05")
    ap.add_argument("--trim-only", action="store_true")
    ap.add_argument("--skip-check", action="store_true", help="skip setup_check.py")
    a = ap.parse_args()

    if not a.trim_only and not a.skip_check:
        print("=== setup_check.py: libraries and data " + "=" * 23)
        if subprocess.run([sys.executable, "setup_check.py"], cwd=HERE).returncode != 0:
            sys.exit("Preparation checks failed: fix the issues above (or use --skip-check).")

    if not a.trim_only:
        labs = LABS if not a.only else [l for l in LABS if l[:2] in a.only]
        if a.prep:
            labs = ["00_prepare_data.py"] + labs
        for lab in labs:
            print(f"\n=== {lab} " + "=" * (60 - len(lab)))
            t0 = time.time()
            r = subprocess.run([sys.executable, lab], cwd=HERE)
            if r.returncode != 0:
                sys.exit(f"{lab} failed (exit code {r.returncode}); stopping.")
            print(f"--- {lab} finished in {time.time() - t0:.0f} s")

    os.makedirs(SLIDES, exist_ok=True)
    files = sorted(glob.glob(os.path.join(FIG, "*.png")))
    for f in files:
        trim(f, os.path.join(SLIDES, os.path.basename(f)))
    print(f"\n{len(files)} figures in figures/, cropped copies in figures/slides/")


if __name__ == "__main__":
    main()
