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
| 9.3.1 | (11) to (13) | D, D%, PA | `scores.difference`, `percent_difference`, `percent_allowed` | yes | E.4 |
| 9.3.2, 9.4.2, 9.7.2 | | signals | `scores.classify_d`, `classify_z`, `classify_en` | yes* | |
| 9.4 | (14) | z | `scores.z_score` | yes | E.4 |
| 9.5 | (15) to (18) | z', delta_E', reduction factor | `scores.z_prime_score`, `delta_e_prime`, `z_reduction_factor` | yes | E.4 |
| 9.6 | (19) | zeta | `scores.zeta_score` | yes | E.4 |
| 9.7 | (20) | E_n | `scores.en_score` | yes | E.4 |
| 9.8 | | screening of reported uncertainties | `scores.uncertainty_flag` | yes* (see note 4) | |
| 9.9 | | combined scores | | no (the standard gives no formula) | |
| 10.3 | (21), (22) | kernel density | `graphics.kernel_density`, `assigned_value.kernel_mode` | yes | E.6 |
| 10.3.2 i) | | bandwidth | `graphics.bandwidth` | yes* | |
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

## Printed values reproduced

`tests/printed_values.py` lists 255 values printed in ISO 13528:2022 that the
functions of the library reproduce to within half a unit of the last printed
digit: 227 from the worked examples E.1 to E.7, E.9, E.10, E.12 and E.13 of
Annex E, and the 28 factors of Table B.1. Of the 227, 126 are the scores of
Table E.7 and 62 belong to Table E.10 (arithmetic mean, standard deviation and
z scores, see item 2 below). Locations and scales from the estimators of Annex C account for
15 of the values. `tests/test_printed_values.py` asserts the count and the tolerance.
E.14 is not covered, and E.15 is checked by equality of counts.

## Where a printed result does not follow from the text

Four items remain after Amd 1:2026 (`inconsistent()` in the same file).

One printed value is not reproduced by any reading of the text:

1. **E.1, Table E.1, third column (0,5 x '<' value), x\*.** Printed 23,95.
   The three-figure rule of C.3.1 stops at 23,9601 and full convergence gives
   23,9585; both round to 23,96. The iterates of x* fall monotonically from
   24,375 to 23,9585, so no stopping point gives 23,95. The printed value
   equals the converged one cut after the second decimal.

Three items are mismatches between the text and the table:

2. **E.12, Table E.10.** The text states that the z scores use the robust
   mean and standard deviation of Algorithm A. The printed z scores and the
   "Average" and "Standard deviation" rows are reproduced by the arithmetic
   mean and standard deviation (11,54 / 3,29 and 7,66 / 2,90); Algorithm A
   gives 11,17 / 2,68 and 7,27 / 2,35 (three-figure rule; 2,69 and 2,36 at
   convergence).
3. **E.3, Table E.5, row "Median, nIQR (MADe)".** The printed u(x_pt) of
   0,0086 is reproduced with nIQR (1,25 x 0,0402 / sqrt(34)); MADe gives
   0,0083. The row names both estimators, and the text does not say which one
   enters Formula (6). `consensus(..., "median")` uses nIQR by default.
4. **E.4, Table E.6, flags.** The limits of 9.8.3 and 9.8.4 (u_min = u(x_pt),
   u_max = 1,5 s*) do not reproduce the printed flags. They are reproduced
   with u_max = sigma_pt and a u_min between 0,002 and 0,0025, which the
   example does not state.

Two further observations are recorded by `notes()` and not counted:

- **Table E.1 follows no single stopping rule.** The printed s* of the first
  column (7,23) is the value of the three-figure rule (7,2296; convergence
  gives 7,2373). The printed s* of the third column (8,60) is the converged
  value (8,5960; the three-figure rule gives 8,5911).
- **E.8, coefficient of determination.** Printed 0,82. The data of Table E.9
  give 0,8264 (0,83); the adjusted coefficient is 0,8167 (0,82).

Bootstrap results (E.3, E.6) depend on the random number generator of R and
are checked within Monte Carlo error only.

Two cases of the 2022 edition are settled by the amendment:

- **C.5.2.1, Formulae (C.18) and (C.19).** As printed in 2022, h gave k = 0
  for p = 2 and 3 although Table C.2 tabulates b_p for them, and the factor
  was 2,221 9. The amendment prints h = floor(p/2) + 1 and 2,219 1, which is
  the default of `qn`. The documentation of the R package robustbase and
  Akinshin (2022, arXiv:2209.12268) had already identified 2.2219 as an error
  for 1/(sqrt(2) qnorm(5/8)) = 2.21914.
- **E.14, Table E.12.** The amendment corrects one assigned value and adds a
  footnote on the rounding of the displayed assigned values. The library has
  no test on this table.

## The stopping rule of Algorithm A

C.3.1 allows the iteration to stop when the third significant figure of x*
and s* no longer changes. That rule stops well before convergence: on 5200
generated data sets (`crosscheck/compare.py`: 6 to 40 results, normal with up
to 20 % shifted results, half of the sets rounded to one decimal) it stops
after a median of 6 iterations, against 34 for convergence to a relative
1e-12, and the resulting s* differs from the converged one in the third
significant figure in 2594 sets (50 %), x* in 107 sets (2 %). The relative
difference of s* has a median of 0,09 %, a 95th percentile of 0,56 % and a
maximum of 10 %. With x_pt = x* and sigma_pt = s*, the signal of a z score
(acceptable, warning, action) changes for 34 of the 120 754 results, in 34
sets. The share of affected sets depends on the generator. `algorithm_a(x)`
follows the rule of the standard; `algorithm_a(x, tol=1e-12)` iterates until
the changes fall below 1e-12 s*.

## Degenerate data

When more than half of the results are identical, MADe is zero and the
iteration starts from the standard deviation (C.3.1). When the identical share
is larger (from about two thirds, depending on the other results; always for
6 of 7, 8 of 10 and 16 of 20 results), the iteration of Algorithm A drives s*
to zero. `algorithm_a` then returns `scale=0.0` and `degenerate=True`, and
`round_record` raises unless sigma_pt is given from Clause 8. `consensus`
returns a scale and an uncertainty of zero in that case. The estimators, the
homogeneity check and the signal functions reject non-finite values.

Algorithm A, Algorithm S, the Q method, the Hampel estimator and Q/Hampel do
not depend on the unit of the data (`tests/test_inputs.py`, units from 1e-12 to 1e12).

## Comparison with other software

- `tests/test_external.py` compares with statsmodels, which was written
  independently of ISO 13528. Algorithm A run to convergence equals Huber's
  proposal 2 (c = 1,5) to 1e-9 when the consistency factor is not rounded
  (1,13339 instead of the printed 1,134); the rounding changes s* by 0,05 %
  to 0,3 %. Qn equals `qn_scale` multiplied by the finite-sample factors of
  Rousseeuw and Croux, which are typed in the test from the R package
  robustbase and agree with Table C.2 and Formulae (C.20) and (C.21). MADe
  and nIQR agree to the precision of the printed constants. The finite-step
  Hampel estimator equals the root nearest the median found by a separate
  root search, which shares only the psi function with the library. The Q method and Algorithm S have no comparison with code
  that the authors did not write.
- `crosscheck/compare.py` compares with the PHP engine of the LAKSiS platform
  on 200 data sets (16 quantities) and on 5000 more (Algorithm A). The PHP
  engine comes from the same group, and several of its functions were written
  together with this library, so this shows agreement of two implementations
  and not independence. All quantities agree to below 1e-10 except Algorithm
  A in one set of the 5200 (a set with ties), where a first iterate of exactly
  41,15 is rounded to three figures as 41,1 by Python and as 41,2 by PHP, so
  that the two stop one iteration apart.
- Until October 2026 both implementations shared a defect in the Q method:
  differences that are equal in exact arithmetic were not merged. The two
  agreed, so the comparison did not show it; a test of unit independence did.
  The library was corrected in 0.1.3 and the PHP engine afterwards. Against
  the outputs of the PHP engine before its correction
  (`php_200_before_fix.json`) the Q method differs in 64 of the 100 sets with
  ties (median 0,3 %, at most 17 %) and in none of the sets without ties.
- The Q method with ties is checked against integer arithmetic
  (`tests/test_external.py`).
- `tests/test_real_round.py` recomputes a real round from its formal report.
