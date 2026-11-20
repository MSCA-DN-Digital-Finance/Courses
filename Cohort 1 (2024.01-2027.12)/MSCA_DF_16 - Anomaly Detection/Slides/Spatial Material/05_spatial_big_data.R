# 05_spatial_big_data.R -------------------------------------------------
# Lab 5 - Spatial big data in R (companion to python/05_spatial_big_data.py)
#   0. Re-simulate the Lab 4 panel and explode it into point events
#   1. Store events partitioned by week (arrow::write_dataset if available,
#      otherwise one compressed CSV per week with data.table::fwrite)
#   2. Bin points to a hexagonal grid with a spatial index (GEOS STRtree
#      inside sf::st_intersects) - compare with arithmetic binning
#   3. Aggregate with data.table (or duckdb SQL on the files if installed)
#   4. Streaming: week-by-week EWMA baseline + space-time Gi* on hexagons
# Packages: sf, spdep, data.table (optional: arrow, duckdb, h3jsr)
# Runtime ~2 min with SCALE = 2 (~580,000 events); most of it is point sampling.
# ----------------------------------------------------------------------
source("00_common.R")
suppressPackageStartupMessages(library(data.table))
L <- load_course(); g <- L$g
set.seed(2021)
SCALE <- 2; CELL <- 8000                      # events per case; hexagon width (m)
n <- nrow(g); TT <- 30; pop <- g$pop
xy <- st_coordinates(st_centroid(st_geometry(g))); D <- as.matrix(dist(xy))

# 0. simulate (same design as Lab 4) and explode to events ---------------
rr <- EBest(g$cases_w4, pop)$estmm / (sum(g$cases_w4) / sum(pop))
season <- 1 + 0.6 * sin(seq(0, 1.6 * pi, length.out = TT))
mu0 <- outer(pop * rr * 0.4 / 1000, season); arr <- matrix(1, n, TT)
A <- order(D[which(g$atu == "Vaslui")[1], ])[1:30]; arr[A, 23:30] <- 1.8
Y <- matrix(rnbinom(n * TT, size = 25, mu = mu0 * arr), n, TT) * SCALE

# Uniform points inside each polygon by rejection sampling in its bounding box.
# (sf::st_sample(..., exact = TRUE) does the same but took ~4 min here.)
geo <- st_geometry(g)
samp <- function(poly, k) {
  bb <- st_bbox(poly); out <- matrix(numeric(0), 0, 2)
  while (nrow(out) < k) {
    m <- ceiling((k - nrow(out)) * 2.5) + 20
    cand <- cbind(runif(m, bb["xmin"], bb["xmax"]), runif(m, bb["ymin"], bb["ymax"]))
    ok <- lengths(st_intersects(st_as_sf(as.data.frame(cand), coords = 1:2, crs = st_crs(poly)), poly)) > 0
    out <- rbind(out, cand[ok, , drop = FALSE])
  }
  out[seq_len(k), , drop = FALSE]
}
tm <- system.time({
  XY <- do.call(rbind, lapply(seq_len(n), function(i) samp(geo[i], sum(Y[i, ]))))
})
unit <- rep(seq_len(n), rowSums(Y))
week <- unlist(lapply(seq_len(n), function(i) rep(0:(TT - 1), Y[i, ])))
ev <- data.table(X = XY[, 1], Y = XY[, 2], week = week, siruta = g$siruta[unit])
cat(sprintf("%s events sampled in polygons in %.1f s\n", format(nrow(ev), big.mark = ","), tm[3]))

# 1. partitioned storage --------------------------------------------------
pdir <- file.path(DATA, "events_r"); unlink(pdir, recursive = TRUE); dir.create(pdir)
if (requireNamespace("arrow", quietly = TRUE)) {
  arrow::write_dataset(ev, pdir, partitioning = "week", format = "parquet")
} else {
  for (w in 0:(TT - 1)) fwrite(ev[week == w], file.path(pdir, sprintf("week=%02d.csv.gz", w)))
}
cat(sprintf("stored: %.1f MB in %d files\n",
            sum(file.size(list.files(pdir, recursive = TRUE, full.names = TRUE))) / 1e6,
            length(list.files(pdir, recursive = TRUE))))

# 2. hexagonal grid + binning ---------------------------------------------
hex <- st_make_grid(g, cellsize = CELL, square = FALSE)
hex <- st_sf(hid = seq_along(hex), geometry = hex)
hex <- hex[lengths(st_intersects(hex, st_union(st_geometry(g)))) > 0, ]
hex$hid <- seq_len(nrow(hex))
cat(sprintf("hex grid: %d cells of %.0f km2\n", nrow(hex), as.numeric(st_area(hex[1, ])) / 1e6))
sub <- ev[sample(.N, 100000)]
t_idx <- system.time(h_idx <- unlist(lapply(st_intersects(st_as_sf(sub, coords = c("X", "Y"), crs = st_crs(g)), hex),
                                            function(z) if (length(z)) z[1] else NA)))[3]
cat(sprintf("st_intersects (STRtree) for 100,000 points: %.2f s -> %.0f s for all events\n",
            t_idx, t_idx * nrow(ev) / 1e5))
# full binning in chunks (memory-bounded)
ev[, hid := NA_integer_]
chunks <- split(seq_len(nrow(ev)), ceiling(seq_len(nrow(ev)) / 2e5))
for (ch in chunks) {
  p <- st_as_sf(ev[ch], coords = c("X", "Y"), crs = st_crs(g))
  ev[ch, hid := vapply(st_intersects(p, hex), function(z) if (length(z)) z[1] else NA_integer_, 1L)]
}
ev <- ev[!is.na(hid)]

# 3. aggregation -----------------------------------------------------------
if (requireNamespace("duckdb", quietly = TRUE) && requireNamespace("DBI", quietly = TRUE)) {
  con <- DBI::dbConnect(duckdb::duckdb()); duckdb::duckdb_register(con, "ev", ev)
  agg <- as.data.table(DBI::dbGetQuery(con, "SELECT hid, week, count(*) AS n FROM ev GROUP BY ALL"))
  DBI::dbDisconnect(con, shutdown = TRUE)
} else {
  agg <- ev[, .N, by = .(hid, week)]; setnames(agg, "N", "n")
}
cat(sprintf("%d occupied cell-weeks\n", nrow(agg)))

# 4. streaming EWMA + space-time Gi* --------------------------------------
nbh <- poly2nb(hex, queen = TRUE)
Bw <- nb2listw(include.self(nbh), style = "B", zero.policy = TRUE)
k1 <- card(nbh) + 1
m <- nrow(hex); alpha <- 0.15; warm <- 8
mu <- rep(0, m); vv <- rep(1, m); prev <- rep(0, m); Z <- matrix(0, m, TT)
for (t in 0:(TT - 1)) {
  y <- numeric(m); a <- agg[week == t]; y[a$hid] <- a$n
  lev <- if (t >= warm) sum(y) / max(sum(mu), 1) else 1
  r <- (y - lev * mu) / sqrt(pmax(lev * vv, SCALE * lev * mu + 1))
  if (t >= warm) {
    cur <- lag.listw(Bw, r, zero.policy = TRUE) + lag.listw(Bw, prev, zero.policy = TRUE)
    allv <- c(r, prev); N <- length(allv); k <- 2 * k1
    Z[, t + 1] <- (cur - mean(allv) * k) / (sd(allv) * sqrt((N * k - k^2) / (N - 1)))
    prev <- r
  }
  d <- y - mu
  if (t == 0) { mu <- y; vv <- pmax(y, 1) } else { mu <- mu + alpha * d; vv <- (1 - alpha) * (vv + alpha * d^2) }
}
alarm <- Z > qnorm(0.999)
tot <- ev[, .(tot = .N), by = hid]
aN <- merge(ev[siruta %in% g$siruta[A], .N, by = hid], tot, by = "hid")
cellA <- aN[N > 0.5 * tot, hid]                 # cells whose events come mostly from cluster A
cat(sprintf("Cluster A cells: %d; first alarm week %s; recall weeks 22-29 = %.2f; alarm rate elsewhere = %.3f\n",
            length(cellA), (which(colSums(alarm[cellA, 23:30, drop = FALSE]) > 0)[1] + 21),
            mean(alarm[cellA, 23:30]), mean(alarm[-cellA, (warm + 1):TT])))
hex$zmax <- apply(Z[, 23:30], 1, max)
p <- ggplot(hex) + geom_sf(aes(fill = pmin(pmax(zmax, 0), 8)), colour = NA) +
  geom_sf(data = county_lines(g), colour = "#555555", linewidth = .2) +
  scale_fill_distiller(palette = "Reds", direction = 1, name = "max Gi* z") +
  labs(title = "Streaming hexagon space-time Gi*, weeks 22-29") + theme_void()
ggsave(file.path(FIG, "21_hex_stream_gistar.png"), p, width = 8, height = 5.6, dpi = 150)
cat("done\n")
