# 01_spatial_anomalies.R ------------------------------------------------
# Lab 1 - Spatial anomaly detection (R version of python/01_spatial_anomalies.py)
#   1. Global Moran's I        2. LISA + FDR (clusters and spatial outliers)
#   3. Getis-Ord Gi*           4. Empirical Bayes rates, Poisson excess risk
#   5. Kulldorff circular Poisson scan (implemented from scratch)
# ----------------------------------------------------------------------
source("00_common.R")
L <- load_course(); g <- L$g; lw <- L$lw; nb <- L$nb

# 1. Global Moran's I --------------------------------------------------
for (v in c("inc_w4", "vac_oct")) {
  mt <- moran.mc(g[[v]], lw, nsim = 999, zero.policy = TRUE)
  cat(sprintf("Global Moran's I %s = %.3f  p = %.3f\n", v, mt$statistic, mt$p.value))
}
png(file.path(FIG, "01_moran_scatter.png"), 1000, 850, res = 160)
moran.plot(as.numeric(scale(g$inc_w4)), lw, labels = FALSE, pch = 16, cex = .4,
           xlab = "Incidence 20.10.2021 (z)", ylab = "Spatial lag")
dev.off()

# 2. LISA --------------------------------------------------------------
g$lisa_raw <- lisa_classes(g$inc_w4, lw, adjust = "none")
g$lisa_fdr <- lisa_classes(g$inc_w4, lw, adjust = "BH")
print(table(g$lisa_raw)); print(table(g$lisa_fdr))
cat_map(g, "lisa_fdr", LISA_COLS, "LISA incidence 20.10.2021 - FDR 5%", "03_lisa_inc_fdr.png")
outl <- g %>% st_drop_geometry() %>% filter(lisa_fdr %in% c("High-Low", "Low-High")) %>%
  select(siruta, atu, county, pop, inc_w4, lisa_fdr)
write.csv(outl, file.path(OUT, "lisa_spatial_outliers_inc_w4.csv"), row.names = FALSE)

# 3. Getis-Ord Gi* (include self in the neighbourhood) -----------------
lw_star <- nb2listw(include.self(nb), style = "B", zero.policy = TRUE)
gi <- localG_perm(g$inc_w4, lw_star, nsim = 999, zero.policy = TRUE)
gi_z <- as.numeric(gi)
gi_p <- p.adjust(attr(gi, "internals")[, "Pr(folded) Sim"], "BH")   # permutation p, as in PySAL
g$gi_class <- ifelse(gi_p < .05 & gi_z > 0, "Hot spot", ifelse(gi_p < .05 & gi_z < 0, "Cold spot", "Not significant"))
print(table(g$gi_class))
cat_map(g, "gi_class", c("Hot spot" = "#C0392B", "Cold spot" = "#2E6DB4", "Not significant" = "#E5E5E5"),
        "Getis-Ord Gi* incidence 20.10.2021 - FDR 5%", "05_gistar_inc.png")

# 4. Rates: Empirical Bayes & Poisson excess risk ----------------------
eb <- EBest(g$cases_w4, g$pop)                # global EB (Marshall 1991)
g$inc_eb <- eb$estmm * 1000
ebl <- EBlocal(g$cases_w4, g$pop, nb)         # local EB (neighbourhood prior)
g$inc_ebl <- ebl$est * 1000
E <- g$pop * sum(g$cases_w4) / sum(g$pop)
g$smr <- g$cases_w4 / E
g$p_pois <- ppois(g$cases_w4 - 1, E, lower.tail = FALSE)
g$pois_anom <- p.adjust(g$p_pois, "BH") < .05
cat("Poisson excess-risk anomalies (FDR):", sum(g$pois_anom), "\n")
ebi <- EBImoran.mc(g$cases_w4, g$pop, lw, nsim = 999, zero.policy = TRUE)
cat(sprintf("EB Moran's I = %.3f p = %.3f\n", ebi$statistic, ebi$p.value))

# 5. Kulldorff circular Poisson scan -----------------------------------
kulldorff_scan <- function(xy, cases, pop, max_frac = .05, k_max = 250, n_sim = 99, n_out = 5) {
  n <- nrow(xy); k_max <- min(k_max, n)
  D <- as.matrix(dist(xy))
  NN <- t(apply(D, 1, order))[, 1:k_max]                # n x k neighbour indices
  P <- t(apply(matrix(pop[NN], n), 1, cumsum)); C <- sum(cases); Pt <- sum(pop)
  valid <- P <= max_frac * Pt
  llr_mat <- function(cs) {
    cz <- t(apply(matrix(cs[NN], n), 1, cumsum)); ez <- C * P / Pt
    l <- ifelse(cz > 0, cz * log(cz / ez), 0) + ifelse(C - cz > 0, (C - cz) * log((C - cz) / (C - ez)), 0)
    l[cz <= ez | !valid] <- 0
    list(l = l, cz = cz, ez = ez)
  }
  obs <- llr_mat(cases)
  maxnull <- replicate(n_sim, max(llr_mat(as.numeric(rmultinom(1, C, pop / Pt)))$l))
  ord <- order(-obs$l); used <- rep(FALSE, n); res <- list()
  for (o in ord) {
    if (obs$l[o] <= 0 || length(res) >= n_out) break
    i <- (o - 1) %% n + 1; k <- (o - 1) %/% n + 1
    mem <- NN[i, 1:k]
    if (any(used[mem])) next
    used[mem] <- TRUE
    res[[length(res) + 1]] <- list(center = i, members = mem, llr = obs$l[o], obs = obs$cz[o],
                                   exp = obs$ez[o], p = (1 + sum(maxnull >= obs$l[o])) / (n_sim + 1))
  }
  res
}
xy <- st_coordinates(st_centroid(st_geometry(g)))
cl <- kulldorff_scan(xy, g$cases_w4, g$pop)
g$scan <- "None"
tab <- do.call(rbind, lapply(seq_along(cl), function(r) {
  c <- cl[[r]]; g$scan[c$members] <<- sprintf("Cluster %d", r)
  data.frame(rank = r, centre = g$atu[c$center], county = g$county[c$center], n_units = length(c$members),
             observed = round(c$obs), expected = round(c$exp, 1), LLR = round(c$llr, 1), p = c$p)
}))
print(tab); write.csv(tab, file.path(OUT, "scan_clusters_inc_w4.csv"), row.names = FALSE)
cat_map(g, "scan", c("Cluster 1" = "#C0392B", "Cluster 2" = "#E67E22", "Cluster 3" = "#8E44AD",
                     "Cluster 4" = "#16A085", "Cluster 5" = "#B7950B", "None" = "#EEEEEE"),
        "Kulldorff circular scan (Poisson) - incidence 20.10.2021", "08_scan_inc.png")

write.csv(st_drop_geometry(g), file.path(OUT, "lab1_results.csv"), row.names = FALSE)
cat("done\n")
