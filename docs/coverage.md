# Coverage of ISO 13528:2022 with Amd 1:2026

Legend: **yes** implemented and checked against a worked example of Annex E;
**yes\*** implemented, no numerical example in the standard (checked against
the formula, a published table or a simulation); **no** not implemented.

## Formulae

| Clause | Formula | Content | Function | Status | Example |
|---|---|---|---|---|---|
| 7.2.2 | (2), (3) | uncertainty budget of x_pt | `assigned_value.combine_uncertainty` | yes* | |
| 7.5.2 | (4), (5) | value assigned against a CRM | `assigned_value.from_crm_comparison` | yes | E.5 |
| 7.6 | | consensus of expert laboratories with uncertainties | | no (the standard prescribes no procedure) | |
| 7.7.6 | | bootstrap standard error | `assigned_value.bootstrap` | yes (Monte Carlo tolerance) | E.3, E.6 |
| 7.7.7 | (6) | u(x_pt) = 1,25 s*/sqrt(p) | `assigned_value.u_robust`, `consensus` | yes | E.3, E.7 |
| 7.8 | (7) | comparison with a reference value | `assigned_value.compare_with_reference` | yes | E.7 |
| 8.3 | | regression on previous rounds | `sigma_pt.fit_previous_rounds` | yes | E.8 |
| 8.4 | (8) | Horwitz/Thompson model | `sigma_pt.horwitz` | yes | E.9 |
| 8.5 | (9) | sigma_pt from a precision experiment | `sigma_pt.from_precision` | yes | E.10 |
| 8.6.2 | | limits on sigma_pt | `sigma_pt.limit_sigma` | yes* | |
| 9.2.1 | (10) | u(x_pt) < 0,3 sigma_pt | `scores.uncertainty_negligible` | yes | E.6 |
| 9.3 | (11) to (13) | D, D%, PA | `scores.difference`, `percent_difference`, `percent_allowed` | yes | E.4 |
| 9.4 | (14) | z | `scores.z_score` | yes | E.4 |
| 9.5 | (15) to (18) | z', delta_E', reduction factor | `scores.z_prime_score`, `delta_e_prime`, `z_reduction_factor` | yes | E.4 |
| 9.6 | (19) | zeta | `scores.zeta_score` | yes | E.4 |
| 9.7 | (20) | E_n | `scores.en_score` | yes | E.4 |
| 9.8 | | screening of reported uncertainties | `scores.uncertainty_flag` | yes* (see note 4) | |
| 9.9 | | combined scores | | no (the standard gives no formula) | |
| 10.3 | (21), (22) | kernel density | `graphics.kernel_density`, `assigned_value.kernel_mode` | yes | E.6 |
| 10.6 | (23) to (25) | repeatability plot | `graphics.repeatability_statistic`, `repeatability_region` | yes* | E.13 (robust values only) |
| 10.2, 10.4, 10.5, 10.7, 10.8 | | histograms, bar plots, Youden plot, split samples, control charts | | no (plots are left to the caller) | |
| 11 | | ordinal quantities | `graphics.ordinal_summary` | yes | E.15 |
| B.2.2 | (B.1), (B.2) | s_s <= 0,3 sigma_pt | `homogeneity.homogeneity` | yes | E.2 |
| B.2.3 | Table B.1 | expanded criterion | `homogeneity.expanded_criterion_factors` | yes (table reproduced for g = 7..20) | |
| B.2.4 a) | | analysis of variance F test | `homogeneity.homogeneity` | yes* | |
| B.2.5 a) | (B.3) | sigma'_pt | `homogeneity.expanded_sigma_pt` | yes* | |
| B.3 | (B.4) to (B.16) | s_x, s_w, s_s | `homogeneity.homogeneity` | yes | E.2 |
| B.1.2 | | one measurement per item | `homogeneity.homogeneity_single` | yes* | |
| B.5.1 | (B.17) | stability criterion | `homogeneity.stability` | yes | E.2 |
| B.5.2 | (B.18) | expanded stability criterion | `homogeneity.stability` | yes* | |
| B.5.4 | | t test on item means | `homogeneity.stability_t_test` | yes* | |
| C.2 | (C.1) to (C.4) | median, MADe, nIQR | `robust.median`, `made`, `niqr` | yes | E.3 |
| C.3.1 | (C.5) to (C.10) | Algorithm A | `robust.algorithm_a` | yes | E.1, E.3, E.7, E.13 |
| C.3.2 | | fixed-scale variants | `robust.algorithm_a(update_scale=False)` | yes* | |
| C.4 | (C.11) to (C.14) | Algorithm S | `robust.algorithm_s` | yes | E.13 |
| C.5.2.1 | (C.15) to (C.21) | Qn | `robust.qn` | yes* (Amd 1:2026) | |
| C.5.2.2 | (C.22) to (C.25) | Q method | `robust.q_method` | yes | E.3 |
| C.5.3 | (C.26) to (C.30) | Hampel estimator, both algorithms | `robust.hampel` | yes | E.3 |
| C.5.4 | | Q/Hampel | `robust.q_hampel` | yes | E.3 |
| D.1.4.2 | (D.1) | small-sample dispersion | `robust.mean_abs_dev_sd`, `sd_two_results` | yes* | |
| 6.6, D.1.2 | | Grubbs, Cochran (ISO 5725-2) | `outliers` | yes* (critical values against ISO 5725-2 tables) | |

`record.round_record` adds no formula. It calls the functions above for one
measurand and returns their results together with the choices made (method,
source of sigma_pt, statistic, limits) and the clause behind each item.

Repeatability standard deviation by the second Q algorithm (C.5.4, last
paragraph) and maximum-likelihood treatment of censored values (E.1 NOTE) are
not implemented; the standard refers to the literature for both.

## Edition and amendment

The library follows ISO 13528:2022 as amended by Amd 1:2026 (published
2026-07-28). The consolidated text was compared with the 2022 edition clause
by clause on 2026-10-03. The amendment changes five things that concern the
calculations:

| Place | 2022 edition | With Amd 1:2026 | Library |
|---|---|---|---|
| 7.7.7 | Formula (6) for robust averages of C.2 and C.3 | also for C.5 | `consensus` applies Formula (6) to all three |
| C.3.2 b) | cross-reference "as i) above" | "as a) above" | no effect |
| (C.18) | h = p/2 or (p - 1)/2 | h = p/2 + 1 or (p - 1)/2 + 1 | default of `qn`; the 2022 text is `h_rule="iso-literal"` |
| (C.19), NOTE 1 | factor 2,221 9 | factor 2,219 1 | default of `qn`; 2,221 9 only with `h_rule="iso-literal"` |
| Table E.12 | assigned value 5,9 (round 104, item C) | 6,0, and a footnote: assigned values are shown to one decimal, so PA scores can differ from hand calculation | no test is derived from this table |

All other changes update references to ISO/IEC 17043:2023 or wording
(Foreword, 0.3, 3.4, 5.2.1, 5.3.1, 5.3.5, 5.4.1, 5.5.1.1, 6.3.1, 9.2.1,
9.4.2). Formula (10), Clause 9.8 and Annex B are unchanged.

## Where Annex E cannot be reproduced from the text

The amendment leaves cases 1 to 4 as they were printed in 2022.

1. **E.1, third column (0,5 x '<' value).** Printed 23,95 / 8,60. The
   stopping rule of C.3.1 gives 23,96 / 8,59; full convergence gives 23,9585 /
   8,5960. The first two columns agree with the C.3.1 rule. The test accepts
   one unit of the last digit and pins the fully converged values.
2. **E.3, Table E.5, row "Median, nIQR (MADe)".** The printed u(x_pt) of
   0,0086 corresponds to nIQR (1,25 x 0,0402 / sqrt(34)); MADe gives 0,0083.
   `consensus(..., "median")` uses nIQR by default for that reason.
3. **E.12, Table E.10.** The text states that the z scores use the robust
   mean and standard deviation of Algorithm A. The printed z scores and the
   "Average" and "Standard deviation" rows are reproduced only by the
   arithmetic mean and standard deviation (11,54 / 3,29 and 7,66 / 2,90);
   Algorithm A gives 11,17 / 2,69 and 7,27 / 2,36.
4. **E.4, Table E.6, flags.** The limits of 9.8.3 and 9.8.4 do not reproduce
   the printed flags. They follow from u_max = sigma_pt and a u_min between
   0,002 and 0,0025 that the example does not state. This is the rule of the
   source study IMEP-111 (u_min = u_ref, u_max = sigma_pt).
5. **E.3 and E.6, bootstrap.** Results depend on the random number generator
   of R; they are checked within Monte Carlo error only.

Two cases of the 2022 edition are settled by the amendment:

- **C.5.2.1, Formulae (C.18) and (C.19).** As printed in 2022, h gave k = 0
  for p = 2 and 3 although Table C.2 tabulates b_p for them, and the factor
  was 2,221 9. The amendment prints h = floor(p/2) + 1 and 2,219 1, which is
  the definition of the estimator's authors and the default of `qn`. The
  documentation of the R package robustbase and Akinshin (2022,
  arXiv:2209.12268) had already identified 2.2219 as a typographical error
  for 1/(sqrt(2) qnorm(5/8)) = 2.21914.
- **E.14, Table E.12.** The printed PA scores imply allowances that do not
  follow from the stated rule when computed from the displayed values. The
  amendment corrects one assigned value and adds a footnote that attributes
  the remaining differences to rounding of the displayed assigned values.

