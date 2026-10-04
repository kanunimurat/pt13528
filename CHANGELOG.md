# Changelog

## 0.1.0 (unreleased)

First version. Implements the calculations of ISO 13528:2022 listed in
`docs/coverage.md` and checks them against every worked example of Annex E
that prints numbers.

Follows the text as amended by ISO 13528:2022/Amd 1:2026: `robust.qn` uses
h = floor(p/2) + 1 and the factor 2,219 1 by default; the 2022 text remains
available as `h_rule="iso-literal"`.

`round_record` assembles the result record of one measurand (assigned value,
u(x_pt), sigma_pt, criterion of 9.2.1, statistic, scores and signals) from
the single functions. It adds no calculation of its own.
