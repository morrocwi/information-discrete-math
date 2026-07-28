# tests/ — the pytest suite (40 files)

**What this folder does.** Standard `pytest` tests covering the exact-ℚ kernel (`test_kernel_p1.py`
through `test_kernel_p6.py`, `test_kernel_eigen.py`, `test_kernel_simplify.py`,
`test_kernel_migration_snapshot.py`), the polynomial tower (`test_groebner.py`, `test_factorize.py`,
`test_partial_fractions.py`, `test_subresultant.py`, `test_summation.py`, `test_linsolve.py`,
`test_matrix_minpoly.py`, `test_interpolate.py`, `test_ode_linear.py`, `test_richardson_apriori.py`,
`test_declaration_bound.py`), the solver surface (`test_idm_api.py`, `test_smoke.py`, `test_limits.py`,
`test_properties.py`, `test_positivity.py`, `test_hilbert.py`), the differential + adversarial harness
(`test_differential_harness.py`, `test_adversarial_harness.py`, driven by `harness.py`), Retained
Spectral (`test_retained_spectral.py`, `test_retained_mode.py`, `test_inertia_count.py`,
`test_resolved_inertia.py`, `test_kernel_eigen.py`, `test_mrrr.py`, `test_multidim_quadrature.py`),
RCP (`test_retained_contraction_protocol.py`, `test_retained_fold_tree.py`,
`test_retained_reverse_compiler.py`), physics demos (`test_physics_demos.py`), and benchmark
statistics (`test_benchmark_stats.py`). `golden/kind_outputs.json` is a golden-file snapshot compared
against in regression tests.

**The PUBLIC api.** `harness.py` is the one importable module meant for reuse: `DIFFERENTIAL_CASES`
(kind → independent-oracle differential test spec) and `adversarial_inputs(fixtures)` (yields hostile
`(kind, params, label)` probes for every registered kind's fixture). A new solver kind is meant to be
covered by adding one registry entry to `harness.py`, not by hand-writing a new adversarial test.

**What NOT to import directly.** Don't import individual `test_*.py` files from non-test code — they
are pytest collection targets, not a library. `conftest.py` at the repo root (not inside `tests/`) is
what makes `import idm` / `import retained_spectral` resolve under bare `pytest`; don't duplicate that
`sys.path` logic inside individual test files.

**How to test it.** `pytest -q` for the whole suite; `pytest -q tests/test_<name>.py` for one file
while iterating. Per the workspace-wide rule on repeated full-arc audits: during iteration, run just
the changed test file, not the whole suite, and save the full `pytest -q` run for once before commit.

**Limits.** This suite tests the *implementation* (does the code do what it claims, does it fail
closed on hostile input) — it is not itself the tier-honesty evidence for `Th_coqc` claims (that's
`formal/`) or the breadth/agreement evidence for `finite_diagnostic` claims (that's `validation/` and
`prove_it*.py`). The adversarial harness's "no exception, well-formed result, never inverts the fence"
check does not certify that a *positive* result on hostile input is itself correct — only the
differential harness (for kinds it covers) checks correctness against an independent oracle.
