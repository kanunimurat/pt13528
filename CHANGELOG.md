# Changelog

## 0.1.7 (2026-10-05)

No calculation changes. This version corrects a statement of 0.1.6 about the standard.

- **The stopping criterion of ISO 13528:2022 is the one that depends on the origin of the results.** C.3.1 of the
  2022 edition, its NOTE 1 and example E.3 word the criterion as no change in the third significant figures of
  the robust mean and of the robust standard deviation. 0.1.6 was written from quotations of the 2015 edition
  (third significant figure of s* and "the equivalent figure" of x*) before the authors had the 2022 text of
  C.3.1 before them; it called the 2015 wording the one "that the wording of C.3.1 supports" and withdrew the
  statement of 0.1.5. That was wrong for the current edition. The finding of 0.1.5 stands: with the criterion
  as ISO 13528:2022 words it, eleven results give s* = 1,328 in degrees Celsius and, in kelvin, stop after one
  iteration at s* = 0,297 with four action signals. With the wording quoted from the 2015 edition they give
  1,328 in both units. Both wordings reproduce Annex E.
- The criteria are now named after the editions: `tol="iso2022"` and `tol="iso2015"`. The names of 0.1.6,
  `"sig3-of-x"` and `"sig3"`, are still accepted with the meaning they had there. The default (convergence)
  is unchanged.
- The whole standard was compared with the test data: every number typed from Annex E and Table B.1, every
  printed value used as an expectation and every constant agrees with ISO 13528:2022. Corrections to the
  documentation that came out of this: Grubbs' and Cochran's tests are cited from 6.6.3 (not 6.6.2); Algorithm A
  covers Formulae (C.5) to (C.10); `kernel_density` includes the factor 1/sigma_k that Formula (22) omits;
  Table E.10 itself (NOTE 2) says robust; 9.8.3 gives u(x_pt) as lower limit only where it meets 9.2.1; other
  explanations of the printed r^2 of E.8 are named; the PA scores of Table E.7 are tested to half a unit.
- `crosscheck/php_evaluate_round.json` and a test: a simulated round of 20 participants evaluated end to end
  by the function that the LAKSiS platform calls for a round (PHP engine 1.6.0) and by `round_record`; assigned
  value, uncertainty, sigma_pt, z, z', zeta, E_n and signals agree. 136 tests.

## 0.1.6 (2026-10-05)

This version withdraws a statement of 0.1.5 and corrects the defect behind it.

- **The three-figure stopping criterion has two readings, and 0.1.5 presented a property of one of them as
  a property of the standard.** C.3.1, as quoted in the literature, stops when the third significant figure
  of s* and the *equivalent figure* of x* (the same decimal place) no longer change; example E.3 words the
  rule as "their third significant figures". Up to 0.1.5 the library implemented the second wording only.
  The dependence on the origin of the results that 0.1.5 reported (eleven results giving four action
  signals in kelvin and none in degrees Celsius) holds for that reading and not for the first; the
  statement that it is a property of the rule of the standard is withdrawn. `tol="sig3"` now implements
  the first reading (s* = 1,328 for the eleven results in both units); the earlier criterion is kept as
  `tol="sig3-of-x"`. Annex E comes out the same under both, so the printed values did not show the
  difference; an independent review did. The default (convergence, since 0.1.5) is not affected. Under
  both readings the criterion stops before convergence and its result changes with the unit
  (`docs/coverage.md`).
- A slow collapse of s* was not detected: for five results of 10, one of 9 and one of 11, `algorithm_a`
  ran into `max_iter` and returned s* = 8e-9 with `converged=False`, and `round_record` used it as
  sigma_pt. The collapse is now detected as soon as all results that are not winsorized are identical
  and s* shrinks by a constant factor; `consensus` and `round_record` raise if Algorithm A has not
  converged; `max_iter` defaults to 100 000. `algorithm_s` detects the corresponding case.
- Algorithms A and S iterate on data scaled to unit size, so that results of the order of 1e-200 or
  1e160 are handled.
- Scores (`z_score`, `z_prime_score`, `zeta_score`, `en_score`, differences) and `uncertainty_negligible`
  reject non-finite values; `round_record`, `q_method`, `q_hampel`, the homogeneity, outlier and
  graphics functions reject strings and mappings; `hampel` rejects a negative or non-finite scale;
  `stability` rejects a non-positive sigma_pt; an invalid `tol` is rejected.
- `crosscheck/r_compare.py`, `r_compare.R`: comparison with the R packages metRology (`algA`, `algS`), MASS
  (`hubers`) and robustbase (`Qn`) through stored reference values. With unrounded factors Algorithm A and
  Algorithm S equal metRology to 1e-13 on 200 sets each.
- Tests: Table C.1 against the chi-squared distribution, Algorithm S for every nu, Formula (23), Formula (3)
  with four terms, Formulae (C.20) and (C.21), the weights of the iterative Hampel estimator, critical values of Cochran's test; 134 tests.
  The sentence of 0.1.5 on a mutation run ("one passes now") referred to a list of 101 hand-picked
  changes and overstated the result: an independent run with randomly chosen changes of operators and
  constants found that 41 of 153 passed the tests of 0.1.5. With the tests of this version, 32 of 232
  such changes pass; they are boundary comparisons (< against <=), tolerances and input checks that a
  second check makes redundant.
- The tests also run in CI with the lowest versions of NumPy and SciPy that the package allows (1.24, 1.11).
  The test extra requires statsmodels 0.15 or later; with 0.14 its Huber estimator does not reach the
  tolerance of the comparison in one set.
- `crosscheck/`: `php_200.json` and `php_5000.json` now hold the outputs of the PHP engine 1.6.0, which iterates
  to convergence as well (the Algorithm A outputs of engine 1.5.0 are kept as `php_5000_engine_1.5.0.json`).
- `crosscheck/compare.py` reports the two readings of the three-figure criterion separately, uses the default
  tolerance for convergence (median 28 iterations, not 34 as with 1e-12), and gives the median Q-method
  difference over the sets that differ.

## 0.1.5 (2026-10-04)

Results of Algorithm A and Algorithm S change in the third significant figure for about half of the data
sets, because the default stopping rule changes.

- `algorithm_a`, `algorithm_s`, `consensus` and `round_record` iterate to convergence by default
  (`tol=robust.DEFAULT_TOL`, 1e-10). The three-figure rule of C.3.1 remains available as `tol="sig3"`;
  `consensus` and `round_record` gain the `tol` argument. The rule depends on the unit and on the origin of
  the results: eleven results in degrees Celsius give s* = 1,328, the same results in kelvin stop after one
  iteration at s* = 0,297 (`tests/test_inputs.py`). `crosscheck/compare.py` measures this on 5200 sets.
- Table E.6 was described wrongly. Its flags are reproduced (21 of 21) when the limits of 9.8.3 and 9.8.4
  are compared with the expanded uncertainty U_lab; 9.8 words the limits for the standard uncertainty, for
  which 9 of 21 agree. The earlier statement that the limits of 9.8 do not reproduce the flags is withdrawn.
  The ledger now lists three inconsistent items and three notes; the u(x_pt) of the median row of
  Table E.5 moves to the notes.
- The Q method treats differences as tied when closer than 4 machine epsilons of the largest absolute
  result, and a group of ties extends from its first member (no chaining).
- `RobustResult` raises `AttributeError` for unknown attributes (`hasattr`, `copy.deepcopy` work);
  strings and mappings are rejected as data; negative uncertainties are rejected by z', zeta and E_n;
  `uncertainty_negligible` takes exactly one of `sigma_pt` and `delta_e`; homogeneity, stability and
  outlier functions check for non-finite values and non-positive criteria; `consensus` and `q_hampel`
  report `degenerate`.
- `tests/test_by_hand.py`: 21 tests with values worked by hand for functions that had no direct test. In a
  mutation run of 0.1.4 (101 single changes of operators and constants) 27 changes passed the tests. Of the
  98 that still apply, one passes now: the starting value of NOTE 2 to C.3.1, which does not change a
  converged result.

## 0.1.4 (2026-10-04)

No change in any calculation.

- `tests/test_real_round.py`: the participants of the recomputed round are labelled P1, P2 and P3.
- `crosscheck/`: `php_200.json` now holds the outputs of the PHP engine after its Q method was corrected
  in the same way as in 0.1.3 (tied differences merged); the earlier outputs are kept as
  `php_200_before_fix.json`. `compare.py` reports both. All 16 quantities now agree to below 1e-10 except
  Algorithm A in one set.

## 0.1.3 (2026-10-04)

Results for valid, non-degenerate data are unchanged with the default settings (differences at the level of
floating-point rounding).

- `algorithm_a` iterates on x minus the median. In 0.1.2 a collapsing s* was not detected when the spread
  of the results was small against their level (for example nine results of 10 and two that differ in the
  sixth decimal), and a tiny s* was returned as converged.
- The statement of 0.1.2 that s* goes to zero "when more than half of the results are identical" was wrong.
  With more than half identical, MADe is zero and the iteration starts from the standard deviation; s* goes
  to zero only for a larger identical share (from about two thirds, depending on the other results).
  Docstring, documentation and error message are corrected.
- `q_method` merges differences that are equal in exact arithmetic. Results reported to a fixed number of
  decimals give tied differences (12,3 - 12,2 and 5,1 - 5,0) that differ by rounding noise in binary, and
  0.1.2 treated them as separate discontinuity points of H1. For such data the Q-method standard deviation
  changes (in the 100 tied sets of `crosscheck/`: 64 sets, median 0,3 %, at most 17 %), and Q/Hampel with
  it. Continuous data and the printed value of example E.3 are unaffected. A test against integer
  arithmetic is added.
- `hampel` (finite-step) and `q_hampel` search the roots on standardized results. Before, two absolute
  tolerances made the result depend on the unit of the data for values below about 1e-6.
- `algorithm_s` reports a collapse to zero as `degenerate=True`; a negative or non-finite fixed `scale` of
  `algorithm_a` and an unknown `method` of `hampel` are rejected; `classify_en`, `classify_d` and
  `uncertainty_flag` reject NaN.

## 0.1.2 (2026-10-04)

Results for valid, non-degenerate data are unchanged with the default settings.

- `algorithm_a`, `algorithm_s`: a numerical `tol` is now relative to s* (w*). Before, it was an absolute
  difference, so data in small units stopped early and were reported as converged.
- `algorithm_a`: when more than half of the results are identical the iteration drives s* to zero; this is
  now detected and returned as `scale=0.0` with `degenerate=True`. `round_record` raises in that case
  unless sigma_pt is given.
- Non-finite and empty input is rejected by `consensus`, `q_method`, `homogeneity`, `kernel_mode` and
  `bootstrap`; `algorithm_s` rejects negative values; `classify_z` rejects NaN; negative u(x_pt) is rejected;
  an unknown `median_scale` raises; `hampel(..., "iterative")` no longer returns NaN.
- `tests/printed_values.py`: the values of Table E.10 are now computed with the functions of the library.
  The correlation coefficient of that table has no function in the library and was removed, which leaves
  255 values. The list of printed items that do not follow from the text has four entries: E.8 was
  removed (the printed 0,82 equals the adjusted coefficient of determination) and the entry for Table E.1
  states that neither stopping rule gives the printed x*.
- `tests/test_external.py`: Qn is compared against finite-sample factors typed in the test (the previous
  test cancelled the library output); the Hampel estimator is compared with a root search.
- `tests/test_inputs.py`: new.
- `crosscheck/compare.py`: counts the z signals that change between the two stopping rules.
- `figures/`: scripts of the simulated examples of the article.

## 0.1.1 (2026-10-04)

No change in any calculation.

- `tests/printed_values.py`: one ledger of the printed values compared (256 reproduced, five that do
  not follow from the text). E.8 is now listed as such a case; its test no longer truncates R squared.
- `tests/test_external.py`: comparison with statsmodels (Huber's proposal 2, Qn, MAD, IQR).
- `tests/test_real_round.py`: a real round recomputed from its formal report.
- `crosscheck/`: generator, stored outputs of the PHP engine and the comparison script, including the
  effect of the three-figure stopping rule of Algorithm A.
- The four functions of `outliers` name the clauses of ISO 13528 they serve.

## 0.1.0 (2026-10-04)

First version. Implements the calculations of ISO 13528:2022 listed in
`docs/coverage.md` and checks them against the worked examples of Annex E.

Follows the text as amended by ISO 13528:2022/Amd 1:2026: `robust.qn` uses
h = floor(p/2) + 1 and the factor 2,219 1 by default; the 2022 text remains
available as `h_rule="iso-literal"`.

`round_record` assembles the result record of one measurand (assigned value,
u(x_pt), sigma_pt, criterion of 9.2.1, statistic, scores and signals) from
the single functions. It adds no calculation of its own.
