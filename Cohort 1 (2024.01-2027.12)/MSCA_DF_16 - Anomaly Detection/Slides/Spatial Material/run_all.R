# run_all.R --------------------------------------------------------------
# Runs every R lab in order and regenerates all R figures and tables
# (figures/R, outputs/R), then writes cropped copies of the figures
# (white margins removed, as in the slides) to figures/R/slides/.
#
# Usage, with the working directory set to the R/ folder:
#   source("run_all.R")                       # labs 01-05 + cropping
#   RUN <- c("01", "04"); source("run_all.R") # selected labs only
#   RUN <- character(0); source("run_all.R")  # just re-crop existing figures
# or from a terminal:  Rscript run_all.R
#
# setup.R (libraries + data checks) runs first; set SKIP_CHECK <- TRUE to skip it.
# Each lab runs in its own clean environment, so the labs do not see each
# other's objects. Cropping uses 'magick' if installed, otherwise 'png'.
# ----------------------------------------------------------------------
labs <- sort(list.files(pattern = "^0[1-5]_.*\\.R$"))
if (!length(labs)) stop("run this from the R/ folder (setwd to course/R)")
if (exists("RUN", inherits = FALSE)) labs <- labs[substr(labs, 1, 2) %in% RUN]

if (!(exists("SKIP_CHECK", inherits = FALSE) && SKIP_CHECK) && length(labs)) {
  cat("=== setup.R: libraries and data ", strrep("=", 28), "\n", sep = "")
  chk <- new.env(parent = globalenv())
  sys.source("setup.R", envir = chk, chdir = TRUE)
  if (!isTRUE(chk$ok)) stop("Preparation checks failed: fix the issues above (or set SKIP_CHECK <- TRUE).")
}

for (lab in labs) {
  cat("\n=== ", lab, " ", strrep("=", 60 - nchar(lab)), "\n", sep = "")
  t0 <- Sys.time()
  sys.source(lab, envir = new.env(parent = globalenv()), chdir = TRUE)
  cat(sprintf("--- %s finished in %.0f s\n", lab, as.numeric(difftime(Sys.time(), t0, units = "secs"))))
}

# crop white margins -----------------------------------------------------
fig_dir <- "../figures/R"; out_dir <- file.path(fig_dir, "slides")
dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
pngs <- list.files(fig_dir, pattern = "\\.png$", full.names = TRUE)

trim_png <- function(src, dst, pad = 10) {
  if (requireNamespace("magick", quietly = TRUE)) {
    im <- magick::image_read(src)
    im <- magick::image_border(magick::image_trim(im, fuzz = 1), "white", sprintf("%dx%d", pad, pad))
    magick::image_write(im, dst)
  } else if (requireNamespace("png", quietly = TRUE)) {
    a <- png::readPNG(src)
    rgb <- if (length(dim(a)) == 3) a[, , 1:min(3, dim(a)[3]), drop = FALSE] else array(a, c(dim(a), 1))
    ink <- apply(rgb < 0.99, c(1, 2), any)
    if (length(dim(a)) == 3 && dim(a)[3] %in% c(2, 4))     # transparent background (ggplot2 default)
      ink <- ink & a[, , dim(a)[3]] > 0.01
    r <- range(which(rowSums(ink) > 0)); c <- range(which(colSums(ink) > 0))
    r <- c(max(r[1] - pad, 1), min(r[2] + pad, nrow(ink)))
    c <- c(max(c[1] - pad, 1), min(c[2] + pad, ncol(ink)))
    png::writePNG(a[r[1]:r[2], c[1]:c[2], , drop = FALSE], dst)
  } else {
    file.copy(src, dst, overwrite = TRUE)
  }
}
for (f in pngs) trim_png(f, file.path(out_dir, basename(f)))
cat(sprintf("\n%d figures in figures/R, cropped copies in figures/R/slides/\n", length(pngs)))
