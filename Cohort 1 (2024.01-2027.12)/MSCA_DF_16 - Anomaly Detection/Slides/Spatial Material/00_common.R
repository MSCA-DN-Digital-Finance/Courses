# 00_common.R -----------------------------------------------------------
# Shared helpers for the R labs of the course
# "Spatial and Spatio-Temporal Anomaly Detection".
# Packages: sf, spdep, spatialreg, ggplot2, dplyr
# (optional: isotree for Isolation Forest, SpatialEpi / rsatscan for scans)
# Run the scripts from the R/ folder:  setwd(".../course/R")
# ----------------------------------------------------------------------
suppressPackageStartupMessages({
  library(sf); library(spdep); library(ggplot2); library(dplyr)
})
DATA <- "../data"; FIG <- "../figures/R"; OUT <- "../outputs/R"
dir.create(FIG, showWarnings = FALSE, recursive = TRUE)
dir.create(OUT, showWarnings = FALSE, recursive = TRUE)
set.seed(42)
invisible(Sys.setlocale("LC_ALL", "C.UTF-8"))   # Romanian diacritics in tables

# Load the course GeoPackage (built by python/00_prepare_data.py) and the
# Queen contiguity list computed on the ORIGINAL borders (identical to Python).
load_course <- function() {
  g <- st_read(file.path(DATA, "ro_course.gpkg"), quiet = TRUE)
  nb <- read.gal(file.path(DATA, "ro_course_queen.gal"), region.id = as.character(g$siruta))
  lw <- nb2listw(nb, style = "W", zero.policy = TRUE)
  list(g = g, nb = nb, lw = lw)
}

# If you prefer to build everything in R from the raw shapefile:
build_from_raw <- function(shp = "../data/ro_atu.shp", csv = "../data/ro_vaccines.csv") {
  g <- st_read(shp, quiet = TRUE)
  d <- read.csv(csv, check.names = FALSE, encoding = "UTF-8")
  g <- merge(g, d, by = "siruta")
  nb <- poly2nb(g, queen = TRUE)          # slow-ish on the 72 MB file (~1 min)
  list(g = g, nb = nb, lw = nb2listw(nb, style = "W", zero.policy = TRUE))
}

LISA_COLS <- c("High-High" = "#C0392B", "Low-Low" = "#2E6DB4", "High-Low" = "#F1948A",
               "Low-High" = "#85C1E9", "Not significant" = "#E5E5E5")

county_lines <- function(g) {
  st_boundary(g %>% st_buffer(80) %>% group_by(county) %>% summarise(.groups = "drop") %>% st_buffer(-80))
}

cat_map <- function(g, col, cols, title, file) {
  g$.cls <- factor(g[[col]], levels = names(cols))
  cnt <- table(g$.cls)
  p <- ggplot(g) + geom_sf(aes(fill = .cls), colour = NA) +
    geom_sf(data = county_lines(g), colour = "#555555", linewidth = 0.2) +
    scale_fill_manual(values = cols, labels = paste0(names(cols), " (", cnt[names(cols)], ")"),
                      drop = FALSE, name = NULL) +
    labs(title = title) + theme_void(base_size = 10) +
    theme(legend.position = c(0.12, 0.18), plot.title = element_text(face = "bold"))
  ggsave(file.path(FIG, file), p, width = 8, height = 5.6, dpi = 150)
  invisible(p)
}

# LISA quadrant labels with Benjamini-Hochberg control
lisa_classes <- function(x, lw, nsim = 999, alpha = 0.05, adjust = "BH") {
  # "Pr(folded) Sim" = one-sided conditional-permutation pseudo p-value,
  # the same quantity as PySAL's p_sim (minimum 1/(nsim+1)).
  lm <- localmoran_perm(x, lw, nsim = nsim, zero.policy = TRUE)
  p <- p.adjust(lm[, "Pr(folded) Sim"], method = adjust)
  q <- as.character(attr(lm, "quadr")$mean)
  ifelse(p < alpha, q, "Not significant")
}
