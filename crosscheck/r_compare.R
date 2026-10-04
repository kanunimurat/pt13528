# SPDX-License-Identifier: LGPL-3.0-or-later
# Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.
# Reference values from R packages for crosscheck/r_compare.py.
# Needs MASS, robustbase and metRology. If metRology is not installed, pass the path of its
# file R/algAS.r (https://cran.r-project.org/package=metRology) as the first argument.
args <- commandArgs(trailingOnly = TRUE)
if (requireNamespace("metRology", quietly = TRUE)) {
  algA <- metRology::algA; algS <- metRology::algS
} else {
  source(args[1])
}
lines <- readLines("r_sets.csv")
out <- file("r_reference.csv", "w")
writeLines("id,algA_mu,algA_s,hubers_mu,hubers_s,Qn,algS,algA_default_s", out)
num <- function(v) if (is.null(v) || is.na(v)) "NA" else sprintf("%.17g", v)
for (ln in lines) {
  f <- strsplit(ln, ";")[[1]]
  v <- as.numeric(strsplit(f[4], ",")[[1]])
  if (f[2] == "x") {
    a <- tryCatch(suppressWarnings(algA(v, tol = 1e-13, maxiter = 5000)), error = function(e) list(mu = NA, s = NA))
    h <- tryCatch(MASS::hubers(v, k = 1.5, tol = 1e-13), error = function(e) list(mu = NA, s = NA))
    q <- robustbase::Qn(v)
    a0 <- tryCatch(suppressWarnings(algA(v)), error = function(e) list(mu = NA, s = NA))   # default tol and maxiter
    writeLines(paste(f[1], num(a$mu), num(a$s), num(h$mu), num(h$s), num(q), "NA", num(a0$s), sep = ","), out)
  } else {
    s <- suppressWarnings(algS(v, as.numeric(f[3]), tol = 1e-13, maxiter = 5000))
    writeLines(paste(f[1], "NA", "NA", "NA", "NA", "NA", num(s), "NA", sep = ","), out)
  }
}
close(out)
cat("R", as.character(getRversion()), "MASS", as.character(packageVersion("MASS")),
    "robustbase", as.character(packageVersion("robustbase")), "\n")
