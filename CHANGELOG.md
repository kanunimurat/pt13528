# Changelog

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
