# Spatial and Spatio-Temporal Anomaly Detection: course materials

Case study: COVID-19 incidence, vaccination uptake and socio-economic profile of
Romania's 3,181 administrative-territorial units (ATU / UAT, LAU2), 2021.

```
course/
├── slides/        Spatial_and_Spatio-Temporal_Anomaly_Detection_(with_Big_Data).pptx
├── data/          ro_vaccines.csv; the original ro_atu.shp/.shx/.dbf/.prj/.cpg 
│                  ro_course.gpkg (joined + simplified), ro_course_queen.gal (Queen weights) to be found here Belbe et al. (2021): https://github.com/stefanacioban/covid_19_spatial_analysis
├── python/        requirements.txt, setup_check.py, common.py, labs 00-05, run_all.py
├── R/             setup.R, 00_common.R, labs 01-05, run_all.R
├── figures/       figures produced by the Python labs (figures/R for the R labs);
│                  figures/slides and figures/R/slides hold cropped copies (as in the deck)
└── outputs/       CSV tables produced by the labs (outputs/R for the R labs)
```

## Sessions and labs

| Session | Topic | Python | R |
|---|---|---|---|
| 0 | Data preparation, spatial weights | `00_prepare_data.py` | (uses its output; `build_from_raw()` in `00_common.R` rebuilds it in R) |
| 1 | Local spatial statistics: Moran, LISA + FDR, Gi*, EB rates, Kulldorff scan | `01_spatial_anomalies.py` | `01_spatial_anomalies.R` |
| 2 | Model-based and multivariate anomalies: OLS / spatial lag residuals, Isolation Forest, LOF | `02_model_based_anomalies.py` | `02_model_based_anomalies.R` (Mahalanobis; Isolation Forest if `isotree` is installed) |
| 3 | Space-time with the two observed snapshots: change LISA, bivariate Moran, hot-spot transitions | `03_spatiotemporal_two_waves.py` | `03_spatiotemporal_two_waves.R` |
| 4 | Surveillance on a simulated 30-week panel with injected anomalies: EARS-like, space-time Gi*, space-time permutation scan, emerging hot spots | `04_spatiotemporal_surveillance_sim.py` | `04_spatiotemporal_surveillance_sim.R` |
| 5 | Spatial big data: 2.9M events, Parquet partitions, H3 indexing, DuckDB SQL, streaming EWMA + space-time Gi*, scaling benchmark | `05_spatial_big_data.py` (run Lab 4 first) | `05_spatial_big_data.R` (sf hexagons + data.table; uses arrow / duckdb if installed) |

## Step 0: preparation (libraries + data)

Run once before the labs. Each script checks the language version, loads
(and if needed installs) every library, checks the data files, loads the data
with the same loader the labs use, and prints a summary.

Python (from `python/`):
```
pip install -r requirements.txt     # or: python setup_check.py --install
python setup_check.py
```
R (working directory `R/`):
```r
source("setup.R")                   # installs missing CRAN packages, loads data
# INSTALL <- FALSE; source("setup.R")   # check only, no installation
```
After `source("setup.R")` the session contains `g` (sf data), `nb`, `lw`
(weights) and `raw` (CSV), ready for interactive work.
On Linux, `sf` needs GDAL/GEOS/PROJ system libraries
(`sudo apt install libgdal-dev libgeos-dev libproj-dev libudunits2-dev`).

## Quick start: regenerate everything

```
cd python && python run_all.py      # all Python labs + cropped figures, ~2 min
cd R && Rscript run_all.R           # all R labs + cropped figures, ~5 min
```
`run_all` runs the Step 0 checks first and stops with a message if something is
missing. Options: `python run_all.py --only 01 04` (selected labs), `--prep`
(rebuild the GeoPackage from the original shapefile first), `--trim-only`
(re-crop only), `--skip-check`. In R: `RUN <- c("01", "04"); source("run_all.R")`,
`SKIP_CHECK <- TRUE`.
The cropped copies in `figures/slides/` are pixel-identical in size to the images
used in the deck. Three slide charts are native PowerPoint charts built from
`outputs/lab2_ols_coefficients.csv`, `lab4_evaluation.csv` and `lab5_scaling.csv`.

## Setup

Python 3.10+:
```
pip install geopandas libpysal esda spreg scikit-learn matplotlib scipy pandas h3 duckdb pyarrow pyproj pillow
cd python
python 00_prepare_data.py --shp ../data/ro_atu.shp --csv ../data/ro_vaccines.csv
python 01_spatial_anomalies.py      # ~15 s
python 02_model_based_anomalies.py  # ~20 s
python 03_spatiotemporal_two_waves.py
python 04_spatiotemporal_surveillance_sim.py   # ~1 min
python 05_spatial_big_data.py --scale 10 --res 6  # ~30 s; writes ~105 MB of Parquet to data/events_parquet
```

R 4.3+:
```r
install.packages(c("sf", "spdep", "spatialreg", "ggplot2", "dplyr", "data.table", "png"))  # optional: magick, isotree, arrow, duckdb
setwd("R"); source("01_spatial_anomalies.R")   # etc.
```
Run `00_prepare_data.py` first: the R labs read `data/ro_course.gpkg` and the
GAL weights, so Python and R use the same neighbours.

## Notes on the data
* `inc_w3` = maximum incidence in the 3rd wave; `inc_w4` = incidence on 20.10.2021
  (4th wave). Both are rates per 1,000 inhabitants, as coded in the source table.
  Approximate case counts are rebuilt as rate × population / 1,000.
* `vac_may`, `vac_oct` = first-dose vaccination rate (%) on 26.05.2021 and 05.10.2021.
* Variable names are shortened in `00_prepare_data.py` (`RENAME` dictionary).

## Why R and Python results differ slightly
Permutation p-values depend on the random-number stream; the Python spatial-lag
model (`spreg.GM_Lag`) and R's `spatialreg::stsls` use different instrument sets;
PySAL's Gi* is row-standardised and R's here is binary. The conclusions are the
same; the exact counts of significant units differ by a few percent.

## Exercises
1. Re-run the LISA with 99, 999 and 9,999 permutations, with and without FDR. How
   does the number of "anomalies" change? Why does the minimum attainable p-value matter?
2. Replace Queen contiguity with k-nearest neighbours (k = 6, 10) and with a
   distance band. Which outliers are robust to the choice of W?
3. Compute LISA on the Empirical-Bayes rates instead of the raw rates. Which
   High-Low outliers disappear, and what is their population?
4. Add `vac_may` to the vaccination model (a temporal lag). How do the residual
   anomalies change in meaning?
5. In Lab 4, set the overdispersion `k` to 5 and to 1000. What happens to the
   scan's false alarms in Bucharest? Propose a fix (for example, a negative-binomial
   or Poisson-gamma expectation, or excluding units above a population cap).
6. Turn Lab 4 into a prospective system: run the detectors week by week using
   only past data and record the time to first alarm for anomaly A.
7. Big data (Lab 5): rerun with `--res 5`, `6` and `7`. Plot the false-alarm rate
   against cell size and explain the pattern with the support of the simulated
   shocks. Then make the threshold data-driven: calibrate it on weeks 8-15 so that
   at most 0.1% of cell-weeks alarm, and re-score cluster A.
