# Code quality: coverage, mutation testing, review

This file reports the quality of the code and of its tests, separately from the numerical verification in
`docs/verification.md`. It was added in 0.1.9. The mutation testing was carried out at the request of the
reviewers of the article describing the library, and the gaps it revealed were closed in 0.1.9.

## Coverage

pytest-cov, branch coverage on, all tests.

| Version | Tests | Statements covered | Branches covered |
|---|---|---|---|
| 0.1.8 | 140 | 731 of 790 (92,5 %) | 259 of 320 (81 %) |
| 0.1.9 | 176 | 752 of 790 (95,2 %) | 281 of 320 (88 %) |

## Mutation testing

mutmut 3.8.0 (Python 3.13, NumPy 2.5.3, SciPy at the version of the test environment), all of `src/pt13528`,
the complete test suite. A mutant is a small change of the code (an operator, a constant, a comparison, an
argument); it is killed when at least one test fails.

| Version | Mutants | Killed | Survived |
|---|---|---|---|
| 0.1.8 | 2885 | 2108 (73,1 %) | 777 |
| 0.1.9 | 2885 | 2267 (78,6 %) | 618 |

The survivors were classified automatically from their diffs and the numerical and logical ones were read one
by one:

| Class | 0.1.8 | 0.1.9 | Meaning |
|---|---|---|---|
| message text | 267 | 239 | only the text of an error message changes; the tests check the exception, not its message |
| input check | 187 | 176 | one condition of the rejection of invalid input |
| numerical or logical | 175 | 88 | see below |
| tolerance or iteration guard | 67 | 67 | stopping tolerance, iteration limit, collapse threshold |
| unchecked result field | 52 | 28 | a field of a returned record (label, count, flag) |
| boundary (< or <=) | 18 | 9 | differs only when two values are exactly equal |
| default argument | 11 | 11 | for example an iteration limit of 100 001 instead of 100 000 |

### What 0.1.8 did not check

Among the numerical and logical survivors of 0.1.8 were branches that no test exercised. None of them changed a
result: the tests added in 0.1.9 (`tests/test_boundaries.py`) pass on the unchanged code. They are:

- the stability criterion of B.5.1 (its value was not compared, only the decision);
- the criteria with delta_E instead of sigma_pt (Formula (10), B.2, B.17);
- the zero limits of the input checks of z, z', zeta and E_n, and the signal limits of 9.3.2, 9.4.2 and 9.7.2
  at and next to each limit;
- the fields returned for degenerate data (Algorithm A, Algorithm S, the consensus);
- the 2022 order statistic of Qn (option `h_rule="iso-literal"`) for even p;
- the grid of the kernel density, the bandwidth when sigma_pt is also given, the median of an ordinal quantity
  when the cumulative share reaches one half exactly, and the clauses recorded by `round_record` for other
  methods than Algorithm A.

### What survives in 0.1.9

Of the 88 numerical or logical survivors, 73 are in `robust.py`. Most are equivalent or concern paths that the
data of a proficiency test do not reach:

- equivalent: `1.5 * sign(q)` and `1.5 / sign(q)` in the psi function (sign is +1 or -1); `p // 2` and
  `(p - 1) // 2` for odd p in the 2022 order statistic of Qn; the starting value of Algorithm S (the iteration
  converges to the same fixed point); reversing the sign of the six psi nodes of the finite-step Hampel
  algorithm (the set of nodes is symmetric);
- comparisons with `<` or `<=` that differ only when a standardized residual is exactly 1,5, 3 or 4,5;
- the arithmetic of the three-figure criterion when s* is zero, and the return values of the slow-collapse
  path of Algorithm A (`degenerate=True` is checked, the location of the identical results is not);
- the result fields of degenerate Algorithm S runs that end after one or more iterations.

The full list with the class of each survivor is `docs/mutation_survivors_0.1.9.csv`.

## Review of the code

The code, the tests and the reviews were written with the assistance of a large language model, as declared in
the article. Numerical correctness rests on the printed values of the standard, on the independent software
(`docs/verification.md`) and on the hand-worked values of the tests. [Human review procedure: to be completed by
the authors.]

No static analysis tool is part of the continuous integration; the code passes `python -m pyflakes`.
[To be confirmed when run.]

## Quality attributes

With reference to ISO/IEC 25010:2023, the evidence above addresses functional correctness (printed values,
independent software), reliability under invalid and degenerate input (input checks, degenerate data, boundary
tests) and maintainability (coverage, mutation testing, regression checks against stored outputs). It does not
address performance efficiency beyond the sizes of proficiency testing rounds, usability, or security.
