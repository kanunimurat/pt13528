# pt13528

*A Python library for proficiency testing statistics according to ISO 13528*

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23137089.svg)](https://doi.org/10.5281/zenodo.23137089)

Statistical methods of **ISO 13528:2022 with Amd 1:2026** (*Statistical methods for use in
proficiency testing by interlaboratory comparison*) as a small,
framework-independent Python library.

## What it does

| Module | Content | Clauses |
|---|---|---|
| `robust` | median, MADe, nIQR, Algorithm A (with the C.3.2 variants), Algorithm S, Qn, Q method, Hampel estimator, Q/Hampel, small-sample dispersion | Annex C, D.1.4.2 |
| `assigned_value` | uncertainty budget, value from a CRM comparison, consensus values with u(x_pt), comparison with a reference value, bootstrap, kernel mode | 7.2 to 7.8 |
| `sigma_pt` | Horwitz model, precision-experiment formula, regression on previous rounds, limits | 8.3 to 8.6 |
| `scores` | D, D%, PA, z, z', zeta, E_n, classification, uncertainty criterion and screening | 9.2 to 9.8 |
| `homogeneity` | s_w, s_s for any number of replicates, criteria B.1 to B.3, expanded criterion, F test, stability criteria, t test | Annex B |
| `outliers` | Grubbs and Cochran critical values and statistics | 6.6, B.2.1, D.1.2 |
| `graphics` | kernel density, repeatability-plot statistic and region, ordinal summary | 10.3, 10.6, 11 |
| `record` | result record of one measurand: assigned value, u(x_pt), sigma_pt, criterion of 9.2.1, statistic, score and signal of every participant, each with its clause | 7 to 9 |

`docs/coverage.md` lists every formula of the standard and whether it is
implemented, and records the printed results of Annex E that do not follow
from the text of the standard.

## Example

```python
from pt13528 import assigned_value, scores

results = [0.227, 0.230, 0.243, 0.255, 0.264, 0.270, 0.274, 0.281, 0.289, 0.311]
av = assigned_value.consensus(results, "algorithm_a")      # x_pt, u(x_pt), s*
z = [scores.z_score(x, av.x_pt, av.scale) for x in results]
if not scores.uncertainty_negligible(av.u_x_pt, sigma_pt=av.scale):
    z = [scores.z_prime_score(x, av.x_pt, av.scale, av.u_x_pt) for x in results]
```

The same steps in one call, returning the record that a report is built from:

```python
import pt13528

rec = pt13528.round_record(results, method="algorithm_a")
rec.statistic, rec.uncertainty_negligible    # 'z_prime', False
rec.summary()                                # x_pt, u(x_pt), sigma_pt and its source, limits, counts
rec.rows()                                   # one dictionary per participant
rec.clauses                                  # clause of ISO 13528 behind each item
```

The library does not produce reports. `round_record` returns the numbers and
the choices behind them; layout, wording and file format belong to the
software that calls it.

## Installation

```
pip install pt13528
```

or, for the development version, `pip install git+https://github.com/kanunimurat/pt13528`.
Python 3.10 or later, NumPy and SciPy are required.

## Verification

```
pip install -e ".[test]"
pytest
```

- `tests/printed_values.py` lists 256 values printed in ISO 13528:2022 (228
  from the worked examples of Annex E, 28 from Table B.1) that the library
  reproduces to half a unit of the last printed digit, and the five printed
  items that do not follow from the text.
- `tests/test_external.py` compares Algorithm A, Qn, MADe and nIQR with
  statsmodels, which was written independently of the standard.
- `tests/test_real_round.py` recomputes a real round from its formal report.
- `crosscheck/compare.py` repeats the comparison with the PHP engine of the
  LAKSiS platform and measures the effect of the stopping rule of Algorithm A.

`docs/coverage.md` gives the details.

## Scope

The library computes; it does not decide. Choosing the method for the assigned
value, the evaluation criterion and the handling of outliers is the
responsibility of the proficiency testing provider (ISO/IEC 17043).

## How to cite

Sert M, Yağan MK, Aydın A, Heidarizadeh M, Tilki E, Selek AE, Mete Sert A.
pt13528: A Python library for proficiency testing statistics according to ISO 13528
Version 0.1.1. Zenodo; 2026. https://doi.org/10.5281/zenodo.23137089 (other versions are listed on the Zenodo page).

## Licence

Copyright (C) 2026 Kombobit Yazılım Madencilik LTD. ŞTİ.

pt13528 is free software: you can redistribute it and/or modify it under the
terms of the GNU Lesser General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version. It is distributed WITHOUT ANY WARRANTY; see `COPYING.LESSER`
and `COPYING` (both also in `LICENSE.txt`).

In practice: you may use the library in your own software, open or closed.
If you distribute a modified version of the library itself, the modifications
must be made available under the same licence.
