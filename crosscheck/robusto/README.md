# Comparison with Robusto

Robusto is an independently written Go library for robust statistics of interlaboratory data
(github.com/victoralmeida428/estatistica_robusta). It was used at tag v0.2.0 (commit a0fca48). Robusto
states no license, so its code is not included here; only its outputs (`robusto_out.json`) are stored.
The only local change needed was the `go` directive of its go.mod (1.27 to 1.24, the compiler at hand).

    python crosscheck/robusto/compare_robusto.py prepare
    git clone https://github.com/victoralmeida428/estatistica_robusta && git -C estatistica_robusta checkout v0.2.0
    # go.mod of this folder: require github.com/victoralmeida428/estatistica_robusta v0.0.0
    #                        replace github.com/victoralmeida428/estatistica_robusta => <path of the clone>
    cd crosscheck/robusto && go run . > robusto_out.json && cd ../..
    python crosscheck/robusto/compare_robusto.py

Result (`robusto_result.json`): in the 100 sets without ties the Q method agrees to machine precision and the
Q/Hampel location to 1e-10 s*; the Hampel estimator at fixed scales agrees with the finite-step algorithm of the
library to 1e-10 s* in all 600 cases (Robusto iterates to convergence; the iterative variant of the library stops
at 0,01 s*/sqrt(p), C.5.3.2). In the 100 sets with ties the Q method of Robusto differs in 64 sets and equals the
outputs of the PHP engine before its correction (`../php_200_before_fix.json`) in all 200 sets: Robusto does not
merge differences that are equal in decimal but not in binary arithmetic, the defect described in docs/coverage.md.
