# setup.R ----------------------------------------------------------------
# Preparation steps for the R labs. Run this first.
#
#   Step 1  R version
#   Step 2  Install the missing CRAN packages and load all of them
#   Step 3  Check that the data files are in ../data
#   Step 4  Load the data: course GeoPackage + Queen weights (the same
#           loader the labs use, load_course() in 00_common.R), and the CSV
#   Step 5  Print a short summary of what was loaded
#
# Usage: setwd("path/to/course/R"); source("setup.R")
#        or from a terminal:  Rscript setup.R
# Set INSTALL <- FALSE before sourcing to only check, without installing.
#
# Note for Linux: sf needs the system libraries GDAL, GEOS and PROJ, e.g.
#   sudo apt install libgdal-dev libgeos-dev libproj-dev libudunits2-dev
# (or install r-cran-sf from your distribution). Windows and macOS get
# binary packages from CRAN and need nothing extra.
# ----------------------------------------------------------------------
if (!exists("INSTALL")) INSTALL <- TRUE
options(repos = c(CRAN = "https://cloud.r-project.org"))
step <- function(n, title) cat(sprintf("\n[Step %d] %s\n%s\n", n, title, strrep("-", 60)))
ok <- TRUE

step(1, "R version")
cat(R.version.string, "\n")
if (getRversion() < "4.2") cat("  WARNING: R 4.2 or newer is recommended\n")

step(2, "Packages")
required <- c(sf = "spatial data frames", spdep = "weights, Moran, LISA, Gi*, EB rates",
              spatialreg = "spatial regression (lab 2)", ggplot2 = "maps and figures",
              dplyr = "data manipulation", data.table = "fast tables (lab 5)",
              png = "cropping figures (run_all)")
optional <- c(magick = "better figure cropping", isotree = "Isolation Forest (lab 2)",
              arrow = "Parquet files (lab 5)", duckdb = "SQL on files (lab 5)", DBI = "used with duckdb")
miss <- names(required)[!vapply(names(required), requireNamespace, logical(1), quietly = TRUE)]
if (length(miss) && INSTALL) {
  cat("Installing:", paste(miss, collapse = ", "), "\n")
  install.packages(miss)
  miss <- names(required)[!vapply(names(required), requireNamespace, logical(1), quietly = TRUE)]
}
for (p in names(required)) {
  if (p %in% miss) cat(sprintf("  MISSING  %-11s %-10s %s\n", p, "", required[[p]]))
  else {
    suppressPackageStartupMessages(library(p, character.only = TRUE))
    cat(sprintf("  ok       %-11s %-10s %s\n", p, as.character(packageVersion(p)), required[[p]]))
  }
}
for (p in names(optional)) {
  have <- requireNamespace(p, quietly = TRUE)
  cat(sprintf("  %-8s %-11s %-10s %s (optional)\n", if (have) "ok" else "absent", p,
              if (have) as.character(packageVersion(p)) else "", optional[[p]]))
}
if (length(miss)) {
  ok <- FALSE
  cat(sprintf('\n  -> install.packages(c(%s))\n', paste0('"', miss, '"', collapse = ", ")))
}

step(3, "Data files in ../data")
files <- list(c("ro_course.gpkg", TRUE, "joined + simplified ATU layer (all labs)"),
              c("ro_course_queen.gal", TRUE, "Queen contiguity weights (all labs)"),
              c("ro_vaccines.csv", TRUE, "original attribute table"),
              c("ro_atu.shp", FALSE, "original shapefile, only for build_from_raw()"))
for (f in files) {
  p <- file.path("../data", f[1])
  if (file.exists(p)) cat(sprintf("  ok       %-22s %7.1f MB  %s\n", f[1], file.size(p) / 1e6, f[3]))
  else {
    cat(sprintf("  %-8s %-22s %10s  %s\n", if (f[2] == "TRUE") "MISSING" else "absent", f[1], "", f[3]))
    if (f[2] == "TRUE") ok <- FALSE
  }
}

if (!ok) {
  cat("\nStopping before loading data: see the messages above.\n")
} else {
  step(4, "Loading the data (same loader as the labs: load_course())")
  source("00_common.R")
  L <- load_course(); g <- L$g; nb <- L$nb; lw <- L$lw
  raw <- read.csv("../data/ro_vaccines.csv", check.names = FALSE)
  cat(sprintf("  GeoPackage: %s ATUs x %d attribute columns + geometry, CRS = %s\n",
              format(nrow(g), big.mark = ","), ncol(g) - 1, st_crs(g)$Name))
  cat(sprintf("  Weights:    %d units, mean %.2f neighbours, islands = %d, style = W\n",
              length(nb), mean(card(nb)), sum(card(nb) == 0)))
  cat(sprintf("  Raw CSV:    %s rows x %d columns\n", format(nrow(raw), big.mark = ","), ncol(raw)))
  same <- identical(as.character(g$siruta), attr(nb, "region.id"))
  cat("  Row order of data and weights identical:", same, "\n")
  ok <- ok && same

  step(5, "Summary of the main variables")
  cols <- c("pop", "inc_w3", "inc_w4", "vac_may", "vac_oct", "vac_change", "inc_change")
  s <- sapply(st_drop_geometry(g)[, cols], function(x) c(mean = mean(x), median = median(x), min = min(x), max = max(x)))
  print(round(t(s), 2))
  cat(sprintf("\n  Counties: %d  |  missing values in these columns: %d\n",
              length(unique(g$county)), sum(is.na(st_drop_geometry(g)[, cols]))))
  cat("\n  Objects now in your session: g (sf data), nb (neighbours), lw (row-standardised weights), raw (CSV)\n")
}
cat("\n", if (ok) "All set: run the labs (source(\"01_spatial_anomalies.R\") ... or source(\"run_all.R\"))"
     else "Some checks failed: see the messages above.", "\n", sep = "")
