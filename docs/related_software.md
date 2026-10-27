# Search for related software (record for Table 1 of the article)

Table 1 of the article was first compiled on 3 to 5 October 2026 from the documentation of each product. At the
request of the reviewers the search was repeated and recorded on 27 October 2026.

## Inclusion criterion

A tool is included when its documentation names at least one estimator of Annex C of ISO 13528 (Algorithm A,
Algorithm S, Qn, Q method, Hampel estimator, Q/Hampel) or one performance score of Clause 9 (z, z′, ζ, En, D,
D%, PA). General statistics libraries are included when they provide an estimator that equals one of Annex C
(Huber's proposal 2 with c = 1,5 is Algorithm A). Only the calculations are compared, as documented by the
publisher or author; "n.d." means not documented in the sources consulted.

## Searches of 27 October 2026

| Source | How | Terms | Result |
|---|---|---|---|
| PyPI | full project index (https://pypi.org/simple/, 923 425 names), names matched against a pattern | 13528, proficien, interlab, inter-lab, ringtest, round robin, robust stat, hampel, Q/Hampel, EQA | pt13528. Other matches were unrelated (Hampel filters for time series, robust mean estimation under adversarial corruption, agent frameworks, a finance package) |
| GitHub | web search restricted to github.com | "ISO 13528" proficiency testing; "Algorithm A" "ISO 13528" | pt13528; ptscore (R, MIT; created 6 October 2026, version 0.0.0.9000, no code yet: not included); Robusto (already in Table 1) |
| CRAN | web search restricted to cran.r-project.org | proficiency testing ISO 13528 package | the search returned no package for ISO 13528; the R packages of Table 1 (metRology, MASS, robustbase, ILS) were found in October 2026 through their documentation and the literature |
| Literature | web search; reviewer suggestion | ISO 13528 Python; proficiency testing software | AlMuhlaki et al. 2025 (SASO Proficiency Test Machine, IMEKO TC6 M4Dconf2025, doi:10.21014/tc6-2025.057): Python; Algorithm A, Q/Hampel, median with nIQR or MADe, z, En, homogeneity and stability; the authors report agreement with the examples of Annex E; no code released. Included. MetricGate (web platform, R based; z scores, IQR-based sigma; source not available): its documentation does not establish an Annex C estimator, not included |

## Status of preprints cited

WAPT (Leal and Rocha, Research Square, doi:10.21203/rs.3.rs-4170397/v1): on 27 October 2026 still a preprint
(version 1, not peer reviewed); the page states a CC BY 4.0 licence for the article, none for the software.
