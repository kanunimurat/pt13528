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
| 9.3.1, 9.3.6 | (11) to (13) | D, D%, PA | `scores.difference`, `percent_difference`, `percent_allowed` | yes | E.4 |
| 9.3.2, 9.4.2, 9.7.2 | | signals | `scores.classify_d`, `classify_z`, `classify_en` | yes* | |
| 9.4 | (14) | z | `scores.z_score` | yes | E.4 |
| 9.5 | (15) to (18) | z', delta_E', reduction factor | `scores.z_prime_score`, `delta_e_prime`, `z_reduction_factor` | yes | E.4 |
| 9.6 | (19) | zeta | `scores.zeta_score` | yes | E.4 |
| 9.7 | (20) | E_n | `scores.en_score` | yes | E.4 |
| 9.8 | | screening of reported uncertainties | `scores.uncertainty_flag` | yes* (see item 3 below) | |
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
| 6.6.3, B.2.1 c), D.1.2 | | Grubbs, Cochran (ISO 5725-2) | `outliers` | yes* (critical values against ISO 5725-2 tables) | |

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

Two items remain after Amd 1:2026 (`inconsistent()` in the same file).

1. **E.1, Table E.1, third column (0,5 x '<' value), x\*.** Printed 23,95.
   The three-figure criterion of C.3.1 stops at 23,9601 and full convergence
   gives 23,9585; both round to 23,96. The iterates of x* fall monotonically
   from 24,375 to 23,9585, so no stopping point gives 23,95. The printed value
   equals the converged one cut after the second decimal. The difference is
   one unit of the last digit.
2. **E.12, Table E.10.** The text states that the z scores use the robust
   mean and standard deviation of Algorithm A, and NOTE 2 of the table speaks
   of robust averages and standard deviations. The printed z scores and the
   "Average" and "Standard deviation" rows are reproduced by the arithmetic
   mean and standard deviation (11,54 / 3,29 and 7,66 / 2,90); Algorithm A
   gives 11,17 / 2,69 and 7,27 / 2,36. The printed z scores have mean 0,00 and
   standard deviation 1,00, as classical scores must.

Four further observations are not counted, because the text leaves the
matter open (`e6_flags()` and `notes()`):

- **E.4, Table E.6, flags.** The example states that the flags follow 9.8 and
  gives neither the limits nor the meaning of the letters a, b and c. 9.8.3
  and 9.8.4 suggest limits for a reported standard uncertainty: u(x_pt) =
  0,0041 as lower limit (only where it meets the criterion of 9.2.1, which it
  does not here: 0,3 sigma_pt = 0,0020) and 1,5 s* = 0,0247 as upper limit.
  Compared with u_lab = U_lab / k these limits give 9 of the 21 printed flags;
  compared with the expanded uncertainty U_lab they give all 21. The flags do
  not identify the limits: for u_lab, any lower limit above 0,0020 up to
  0,0025 and any upper limit from 0,0065 to below 0,015 gives all 21 (for
  example u(x_pt)/2, which for k = 2 is the same test as U_lab against
  u(x_pt)). Versions up to 0.1.4 described this item as "not reproduced by
  the limits of 9.8", and versions 0.1.5 to 0.1.6 counted it as a mismatch
  between text and table; it is an unstated choice.
- **Table E.1 follows no single stopping rule.** The printed s* of the first
  column (7,23) is the value of the three-figure rule (7,2296; convergence
  gives 7,2373). The printed s* of the third column (8,60) is the converged
  value (8,5960; the three-figure rule gives 8,5911). E.3 states the
  three-figure rule; E.1 states no rule.
- **E.3, Table E.5, row "Median, nIQR (MADe)".** The row prints two standard
  deviations, 0,0402 and (0,0386), and one u(x_pt), 0,0086, which follows
  from nIQR (1,25 x 0,0402 / sqrt(34)); MADe gives 0,0083.
  `consensus(..., "median")` uses nIQR by default.
- **E.8, coefficient of determination.** The text prints r^2 = 0,82. The
  data of Table E.9 give 0,8264 (0,83); the adjusted coefficient is 0,8167
  (0,82). Truncation, or rounding of the tabulated inputs (which moves r^2
  between 0,823 and 0,830), would explain the printed value as well.

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

C.3.1 of ISO 13528:2022 lets the iteration stop when there is no change "in
the third significant figures of the robust mean and robust standard
deviation"; NOTE 1 to C.3.1 and example E.3 use the same words, and Amd 1:2026
does not change them. The foreword of the 2022 edition lists its changes
against the 2015 edition, and C.3.1 is not among them. The library iterates by
default until the changes of x* and s* fall below 1e-10 s*
(`robust.DEFAULT_TOL`). The criterion of the standard is `tol="iso2022"` in
`algorithm_a`, `algorithm_s`, `consensus` and `round_record`. It is applied by
rounding x* and s* to three significant figures and comparing successive
iterates.

A second wording occurs in the literature: no change in the third significant
figure of the robust standard deviation and in "the equivalent" figure of the
robust average (Szewczak and Bondarzewski, Accred Qual Assur 2016;21:91-100,
who cite ISO 13528:2005 and ISO 5725-5:1998). Read as the same decimal place,
this is `tol="equivalent-figure"`. The authors have not seen the 2005 edition
and make no statement about its text.

Both criteria give the same values for every worked example of Annex E. They
differ in one property. Under the 2022 wording the figure that is tested in x*
moves with the level of the results, so the result depends on their origin.
Eleven results constructed for the test (`tests/test_inputs.py`) give, in
degrees Celsius, s* = 1,328 under both criteria; the same results in kelvin
give 1,328 under the equivalent-figure variant, and under the 2022 wording the
iteration stops after one step at s* = 0,297 and four results get an action
signal. The converged value is 1,330 in both units.

**History of this section.** Versions up to 0.1.5 implemented the 2022 wording
under the name `"sig3"`, and 0.1.5 reported the dependence on the origin. A
review then pointed to the second wording, and 0.1.6, written before the
authors had the 2022 text of C.3.1 before them, withdrew the statement and
called the second wording the one "that the wording of C.3.1 supports". That
was wrong for the current edition, and 0.1.7 corrects it: the dependence on
the origin is a property of the criterion as ISO 13528:2022 words it. In 0.1.6
the names were `"sig3-of-x"` (2022 wording) and `"sig3"` (variant); both are
still accepted.

Measured on 5200 generated data sets (`crosscheck/compare.py`: 6 to 40
results, normal with up to 20 % shifted results, half of the sets rounded to
one decimal), against convergence:

| | 2022 wording (`iso2022`) | variant (`equivalent-figure`) |
|---|---|---|
| median iterations (convergence: 28) | 6 | 6 |
| sets in which s* differs in the third significant figure | 2594 (50 %) | 2417 (46 %) |
| sets in which x* differs in the third significant figure | 108 | 99 |
| relative difference of s*: median, 95th percentile, maximum | 0,09 %, 0,56 %, 10 % | 0,08 %, 0,51 %, 3,2 % |
| z signals that change, of 120 754 results | 34 | 28 |
| after x 25,4: sets in which s* changes, signals that change, largest error | 4171, 45, 18 % | 4113, 38, 6,5 % |
| after + 273,15: sets in which s* changes, signals that change, largest error | 135, 5, 32 % | 5, 0, 3,2 % |

Signals are those of z scores with x_pt = x* and sigma_pt = s*. The shares
depend on the generator, and single sets on the implementation: where an
iterate lies on a rounding boundary of the third figure, an implementation
that does not scale the data internally can stop at another iteration (one
of the 5200 sets). Under the variant, the five sets that change after the
shift are such boundary cases.

Other software stops differently again (`crosscheck/r_compare.py`): `algA` of
the R package metRology stops by default at a relative change of s* of
1,2e-4 or after 25 iterations, and differs from its own converged result by up
to 4,2 % on the 200 sets; `hubers` of the R package MASS stops after 30
iterations without a message, and differs from the converged result in 55 of
the 200 sets, by up to 2,4 %. Of the 255 printed values, one (s* of the first
column of Table E.1, 7,23) is reproduced by both three-figure criteria and not
by the default, which gives 7,24.

## Degenerate data

When more than half of the results are identical, MADe is zero and the
iteration starts from the standard deviation (C.3.1). When the identical share
is larger (possible from 5 of 9 results, usual from about two thirds, always
for 6 of 7, 8 of 10 and 16 of 20 results), the iteration of Algorithm A drives
s* to zero. `algorithm_a` then returns `scale=0.0` and `degenerate=True`, and
`round_record` raises unless sigma_pt is given from Clause 8. `consensus`
returns a scale and an uncertainty of zero and `degenerate=True` in that case.
The collapse is detected when s* has fallen below 1e-9 of its starting value,
or as soon as all results that are not winsorized are identical and s* shrinks
by a constant factor. In 0.1.5 a slow collapse (five results of 10, one of 9
and one of 11: s* shrinks by 1,8 % per iteration) ran into the iteration limit
and returned s* = 8e-9 as a result; `consensus` and `round_record` now raise
if Algorithm A has not converged, and the default limit is 100 000 iterations
(some non-degenerate sets with many identical results need more than 1000).

C.3.1 NOTE 2 allows the standard deviation as starting value "after checking
for any gross outliers", and the NOTE to C.4 an average "after eliminating any
extreme outliers"; the library removes nothing, which is left to the caller,
and starts Algorithm S from the root mean square of the w_i.

Formula (22) is printed without the factor 1/sigma_k. `kernel_density`
includes it, so that the density has unit area as 10.3.1 describes; the
position of the modes is not affected.

The estimators, the scores, the homogeneity and stability checks and the
signal functions reject non-finite values; strings and mappings are not
accepted as data; negative uncertainties, non-positive sigma_pt and invalid
stopping criteria are rejected.

With the default settings Algorithm A, Algorithm S, the Q method, the Hampel
estimator and Q/Hampel do not depend on the unit or the origin of the data
(`tests/test_inputs.py`, units from 1e-200 to 1e160 for Algorithms A and S).
The Q method treats two differences as tied when they are closer than 4
machine epsilons of the largest absolute result. It forms all p(p - 1)/2
differences in memory and is meant for the sizes of proficiency testing
rounds (hundreds of results, not tens of thousands).

## Comparison with other software

- `tests/test_external.py` compares with statsmodels, which was written
  independently of ISO 13528. Algorithm A equals Huber's proposal 2 (c = 1,5)
  to 1e-9 when the consistency factor is not rounded (1,13339; the standard
  prints 1,134, which is not the rounded value, 1,133); the printed factor
  changes s* by 0,05 % to 0,3 %. Qn equals `qn_scale` multiplied by the
  finite-sample factors of Rousseeuw and Croux, typed in the test from the R
  package robustbase, to 1e-4 (the standard prints 2,2191 and rounds the
  factors). MADe and nIQR agree to the precision of the printed constants.
  The finite-step Hampel estimator equals the root nearest the median found
  by a separate root search, which shares only the psi function with the
  library.
- `crosscheck/r_compare.py` compares with R packages through stored reference
  values (`r_reference.csv`, produced by `r_compare.R` with R 4.3.3, metRology
  0.9-29-2, MASS 7.3-60.0.1 and robustbase 0.99-2 from the inputs in
  `r_sets.csv`). metRology was written from ISO 5725-5, the source of
  Algorithms A and S. On 200 sets of results and 200 sets of standard
  deviations (20 for each nu = 1 to 10): with the factors that the standard
  rounds replaced by their exact values, Algorithm A equals `algA` to 8e-14
  and Algorithm S equals `algS` to 2e-15, both run to convergence. With the
  printed factors the differences are at most 0,23 % (Algorithm A, factor
  1,134) and 0,15 % (Algorithm S, Table C.1). `MASS::hubers` agrees to 1e-9 in
  145 of the 200 sets and has not converged after its 30 iterations in the
  other 55. Qn agrees
  with `robustbase::Qn` to 7e-5.
- The Q method, the Hampel estimator and Q/Hampel have no comparison with
  code that the authors did not write. The Q method with ties is checked
  against integer arithmetic and the Hampel estimator against a root search,
  both written for the tests.
- `crosscheck/compare.py` compares with the PHP engine of the LAKSiS platform
  (version 1.6.0) on 200 data sets (16 quantities) and on 5000 more
  (Algorithm A). The PHP engine comes from the same group, and several of its
  functions were written together with this library, so this shows agreement
  of two implementations and not independence. All quantities agree to below
  1e-10, and Algorithm A in all 5200 sets; both iterate to convergence. Engine
  1.5.0 stopped on the third significant figures of x* and s*; against its
  stored outputs (`php_5000_engine_1.5.0.json`) the library with
  `tol="iso2022"` differs in one of 5000 sets, where an iterate lies on a
  rounding boundary.
- Until October 2026 both implementations shared a defect in the Q method:
  differences that are equal in exact arithmetic were not merged. The two
  agreed, so the comparison did not show it; a test of unit independence did.
  The library was corrected in 0.1.3 and the PHP engine afterwards. Against
  the outputs of the PHP engine before its correction
  (`php_200_before_fix.json`) the Q method differs in 64 of the 100 sets with
  ties (median 0,9 % in those 64 sets, at most 17 %) and in none of the sets
  without ties.
- The Q method with ties is checked against integer arithmetic
  (`tests/test_external.py`).
- `tests/test_real_round.py` recomputes a real round from its formal report.
