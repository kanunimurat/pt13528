# Versioning and maintenance

This file states how pt13528 is versioned. It was added in 0.1.9 at the request of the reviewers of the
article describing the library.

## Version numbers

Versions are numbered MAJOR.MINOR.PATCH. Until 1.0.0 the library is in its initial phase, but the following
rules already apply from 0.1.9 on:

- **Patch versions** (0.1.x) correct documentation, tests and code without changing any numerical result or
  default of a public function. Version 0.1.9 is of this kind: no public function and no result changed
  against 0.1.8.
- **Minor versions** (0.x.0) are needed for any change of a numerical result, of a default (for example the
  stopping criterion of Algorithm A or the order statistic of Qn) or of the signature of a public function.
  The changelog marks such changes under the heading "Changes results" and names the functions concerned.
- **1.0.0** will freeze the public API, that is, the 52 public functions listed in `docs/coverage.md`.

Versions 0.1.0 to 0.1.8 were released within two days (4 and 5 October 2026), before these rules existed.
Several of them changed results or defaults (see `CHANGELOG.md`).

## What every release must pass

- the complete test suite, including the ledger of printed values (`tests/printed_values.py`, 255 values
  within half a unit of the last printed digit);
- the comparisons with stored outputs, which pin the numerical results: the PHP engine
  (`crosscheck/php_200.json`, `php_5000*.json`), R (`crosscheck/r_reference.csv`), Robusto
  (`crosscheck/robusto/robusto_out.json`) and the stored inputs (`crosscheck/inputs*.json.gz`).

The continuous integration (`.github/workflows/tests.yml`) runs the test suite on every push.

## Releases and archives

Each release is tagged on GitHub (vX.Y.Z), published on PyPI and archived on Zenodo with its own DOI. The
Zenodo record holds the content of the tag. The concept DOI 10.5281/zenodo.23135796 always resolves to the
latest version. An article that reports numbers cites the DOI of the version that produced them.

## Degenerate and difficult data

The behaviour for many identical results, very few results, ties and invalid input is documented in
`docs/coverage.md` (sections "Degenerate data" and "The stopping rule of Algorithm A"). In short: when
Algorithm A drives s* to zero, `algorithm_a` returns `scale=0.0` and `degenerate=True`, `consensus` returns a
zero scale and uncertainty, and `round_record` raises unless sigma_pt is given; non-finite values and
invalid arguments are rejected; in the Q method, differences that are equal in exact arithmetic but differ by binary rounding noise are merged. Small numbers
of participants are not refused: the choice of method for small p is left to the provider (ISO 13528:2022,
D.1).
