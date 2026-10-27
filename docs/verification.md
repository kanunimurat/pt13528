# Verification of pt13528

This file breaks the verification evidence down by family of functions and states what each piece of
evidence can and cannot show. It was added in 0.1.9 at the request of the reviewers of the article
describing the library. `docs/coverage.md` maps every function to its clause.

Three kinds of evidence are kept apart:

1. **Printed values** of ISO 13528:2022 that the functions reproduce (`tests/printed_values.py`).
2. **Independent software**: implementations that the authors did not write (`tests/test_external.py`,
   `crosscheck/r_compare.py`, `crosscheck/robusto/`).
3. **Regression checks**: the PHP engine of the same group (`crosscheck/compare.py`) and hand-worked values.
   They show that two implementations agree, not that either reads the standard correctly.

## Printed values by family

Tolerance: half a unit of the last printed digit. "Default" means the default settings of the library and the
method that the text of the example names.

| Family | Printed values | With the default and the named method | Source of the expected value |
|---|---|---|---|
| Scores z, z′, ζ, En, D%, PA (Table E.7) | 126 | 126 | Table E.7 (input: Table E.6, example E.4) |
| Arithmetic mean, SD and z (Table E.10, example E.12) | 62 | 0 | Table E.10; the text names Algorithm A, the table follows the arithmetic mean |
| Factors F1, F2 of Table B.1, g = 7 to 20 | 28 | 28 | Table B.1; computed from the chi-squared and F quantiles, not stored |
| Robust location and scale (Annex C) | 15 | 14 | E.1, E.3, E.7, E.13; s* of the first column of Table E.1 (7,23) only with the three-figure criterion |
| Homogeneity and stability (Annex B) | 8 | 8 | Tables E.2 and E.3 (example E.2) |
| Uncertainty of the assigned value, comparison with a reference (7.7.7, 7.8) | 6 | 6 | E.3, E.7 |
| Arithmetic mean, SD, u (E.3) | 3 | 3 | Table E.5 |
| Assigned value from a CRM (7.5) | 3 | 3 | E.5 |
| σpt by the Horwitz model and from a precision experiment (8.4, 8.5) | 3 | 3 | E.9, E.10 |
| Kernel density mode (10.3) | 1 | 1 | E.6 |
| **Total** | **255** | **192** | |

The 15 robust values are: Algorithm A 9 (E.1 four, E.3 two, E.7 two, E.13 one), Algorithm S 1 (E.13),
median, nIQR and MADe 1 each (E.3), Q/Hampel 2 (E.3: the Q method scale and the Hampel location).
Qn has no printed value. Two printed results are not reproduced (Table E.1, third column, x*; Table E.10);
see `docs/coverage.md` and `crosscheck/annex_e_checks.py`.

## Functions without a printed example

Checked against the formula by hand-worked values (`tests/test_by_hand.py`, `tests/test_formulae.py`), against
published tables or against simulation:

- Qn (C.5.2.1): against robustbase (7e-5, rounded finite-sample factors) and Robusto.
- Combined uncertainty (7.2.2), limits on σpt (8.6.2), expanded σpt (B.2.5), single-measurement homogeneity
  (B.1.2), expanded stability criterion (B.18), t test on item means (B.5.4), F test (B.2.4 a)): hand-worked values.
- Grubbs and Cochran (ISO 5725-2): critical values against the tables of ISO 5725-2.
- Bandwidth (10.3.2), repeatability plot (10.6), small-sample dispersion (D.1.4.2): hand-worked values.
- Signal rules of 9.3.2, 9.4.2 and 9.7.2: tests at and next to every limit (`tests/test_boundaries.py`).

"Hand-worked values" are written in the tests as plain arithmetic on the formula of the standard (or as a
quantile taken directly from SciPy), not through the library (`tests/test_by_hand.py`). They were written with
the assistance of a language model, like the rest of the code; they check that the code evaluates the formula
as transcribed, not that the transcription of the formula is right.

## Independent software

| Estimator | Software | Data | Agreement |
|---|---|---|---|
| Algorithm A | metRology `algA` (R) | 200 generated sets | 8e-14 with the exact consistency factor; 0,23 % with the printed 1,134 |
| Algorithm A | statsmodels Huber's proposal 2 (Python) | 300 sets | 1e-9 (exact factor) |
| Algorithm A | MASS `hubers` (R) | 200 sets | 1e-9 in 145 sets; not converged after its 30 iterations in 55 |
| Algorithm S | metRology `algS` (R) | 200 sets of SDs | 2e-15 with exact factors; 0,15 % with Table C.1 |
| Qn | robustbase `Qn` (R) | 200 sets | 7e-5 |
| Q method | Robusto 0.2.0 (Go) | 200 sets | machine precision without ties; differs in 64 of 100 sets with ties, where Robusto repeats the defect described in coverage.md |
| Q/Hampel | Robusto 0.2.0 | 100 sets without ties | 2e-11 s* |
| Hampel estimator | Robusto 0.2.0 | 600 cases (Q, MADe, Qn as fixed scales) | 5e-11 s* (finite-step algorithm) |
| MADe, nIQR | statsmodels, R | | to the precision of the printed constants |

## Test suite

Version 0.1.9: 176 tests. Coverage (pytest-cov, branch coverage on): see `docs/quality.md`.
Mutation testing (mutmut 3.8.0) on 0.1.8 and 0.1.9: see `docs/quality.md`.

## Generated inputs

The data sets of `crosscheck/` are stored (`crosscheck/inputs.json.gz`, `crosscheck/inputs_moderate.json.gz`),
because NumPy does not guarantee its random streams across versions. `compare.py` reports whether the NumPy at
hand regenerates them identically.
