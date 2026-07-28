# benchmarks/ — reproducible cost & speed evidence

**What this folder does.** Standalone scripts (each runnable directly, and importable — see
`tests/test_retained_reverse_compiler.py` importing `benchmarks.coupled_nd_retained_compiler` /
`benchmarks.retained_reverse_compiler`) that recompute the Retained Contraction Protocol (RCP) work-
token and RCP-Energy numbers reported in the root README: `coupled_nd_retained_compiler.py` (the
coupled 11-D integral, direct vs RCP work tokens), `direct_nd_work_tokens.py` (separable N-D
quadrature token counts, no radial reduction), `competitor_benchmark.py` (RCP vs `opt_einsum` /
TensorLy TT-SVD / TT-cross on a sparse factor graph), `rcp_energy_challenge.py` (the RCP-Energy
96-tick site-plan example), `rcp_ten_problem_suite.py` (ten preregistered RCP problems plus four
fail-closed controls), `retained_fold_tree.py` (the native Retained Fold Tree / RFT executor),
`retained_readout_pullback_benchmark.py` (Retained Readout Pullback self-check against an independent
tilted-factor contraction and finite-difference gradients), `retained_reverse_compiler.py` (one
forward contraction + one reverse pass for all axis moments), `compiled_retained_readout_pullback.py`
(a Numba/LLVM-compiled execution substrate for the same RRP semantics). The `*_RESULTS.md` files and
`rcp_energy_results.json` / `retained_readout_pullback_results.json` are the recorded output of the
corresponding script.

**The PUBLIC api.** These are benchmark *scripts*, run with `python3 -m benchmarks.<module>` or
`python3 benchmarks/<module>.py`; the handful of dataclasses/functions imported by the test suite
(`PairwiseProblem`, `Factor`, `CompilerResult`, `DenseFactor`, `ReverseCompilerResult`, `ReverseStep`,
`ReverseWorkPlan`, etc.) are the closest thing to a stable surface, and only because
`tests/test_retained_reverse_compiler.py` and `tests/test_retained_fold_tree.py` already depend on
them.

**What NOT to import directly.** Don't treat any single benchmark's printed number as portable across
hosts — every headline in the root README is qualified "this host, this run" and is meant to be
regenerated (`make benchmark`, or the individual `python3 -m benchmarks.<module>` commands), not
copied as a universal constant. Don't import the underscore-prefixed helpers (`_triangle`,
`_kahan_add`, `_dense_weighted_tensor`, `_median_run`, …) — those are per-script internals.

**How to test it.** `pytest -q tests/test_retained_contraction_protocol.py
tests/test_retained_fold_tree.py tests/test_retained_reverse_compiler.py` covers the importable core;
the benchmark scripts themselves are self-checking (they print `ACCEPT`/`HOLD`-style verdicts and
exit non-zero on failure) — run the specific script named in the claim you're checking.

**Limits.** Every number here is `finite_diagnostic`: exact-`Fraction` work-token counts and wall-clock
medians on a declared, pinned environment, not an asymptotic or universal-hardware claim. RCP savings
are reported as bit-identical to the direct computation (a stated max witness difference, not zero
in the abstract) — read the specific tolerance in each `*_RESULTS.md` rather than assuming exact
equality holds outside the reported precision. The founder's untracked
`benchmarks/competitor_benchmark.png` / `benchmarks/competitor_showdown*` assets referenced from the
root README are not part of this folder's tracked, documented API.
