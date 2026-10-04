# Changelog

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
