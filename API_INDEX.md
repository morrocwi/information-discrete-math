# API_INDEX.md — searchable capability table

Every row below was confirmed against this checkout while writing this file: the Python API path
resolves to a real, importable callable, and the "Verification file" exists in the repo. Tiers
(`Th_coqc` / `exact` / `finite_diagnostic` / `Dr`) are the **actual runtime tier returned by
`idm.solve(...)["tier"]`** for each kind, confirmed by calling it — not the raw decorator tag in
`idm/solve.py`. This matters: `idm/solve.py`'s `solve()` runs a tier-honesty pass
(`_COQ_BACKED`) that **downgrades a kind's declared `Th_coqc` tag to `exact` at call time unless
that specific kind has a named Coq theorem behind it** — e.g. `gcd`, `bezout`, `catalan`,
`bipartite_matching`, `is_prime`, and `critical_path` are decorated `"Th_coqc"` in the source but
all actually return `tier: "exact"`; only `shortest_path`, `widest_path`, `minimax_path`,
`orient`, `convex_hull`, `point_in_polygon`, `segments_intersect`, `spanning_tree_count`, and
`geometric_series` are the kinds where `Th_coqc` is actually returned (see `_COQ_BACKED` in
`idm/solve.py`). Re-run `idm.solve({"kind": "<name>", ...})["tier"]` yourself if in doubt — the
static decorator tag alone is not reliable evidence of the returned tier. See `THEOREM.md` for
what each tier means. This table is a curated subset (the primary + spectral + certified
surfaces, plus ~14 representative `idm.solve` kinds) — read `AI_START_HERE.md` §"Discovery order"
for how to get the live, complete list (`idm.kinds()` returns all 263).

| Capability | Python API | Input | Output | Tier | Verification file |
|---|---|---|---|---|---|
| Unified solver dispatch | `idm.solve(problem)` | `dict` with `"kind"` + kind-specific fields | `dict`: `status`/`tier`/`value`/`bound`/`method` | varies per kind (see rows below) | `tests/test_idm_api.py` |
| List all registered kinds | `idm.kinds()` | — | `list[str]`, 263 names | n/a (registry introspection) | `tests/test_idm_api.py::test_registry_size`, `::test_lots_of_kinds` |
| Tridiagonal eigenvalues (native) | `retained_spectral.engine.native_eigvals_from_tridiagonal(diagonal, off_diagonal, k, energy_tolerance)` | symmetric tridiagonal diag/off-diag arrays, `k` requested modes, tolerance | lowest-`k` eigenvalues to declared tolerance | finite_diagnostic (Retained Spectral product) | `tests/test_retained_spectral.py`, `tests/test_mrrr.py` |
| Retained eigenvectors | `retained_spectral.retained_mode.modes(d, e, lams, rho, orth_tol, reltol, sweeps)` | tridiagonal `d`/`e`, target eigenvalues `lams` | eigenvectors resolved to tolerance | finite_diagnostic | `tests/test_retained_mode.py` |
| Banded inertia count (Sturm) | `retained_spectral.inertia.count_below_banded(kb, mb, sigma)` | banded stiffness `kb`, mass `mb`, shift `sigma` | integer count of eigenvalues below `sigma` | finite_diagnostic — a finite sign-count, cross-checked numerically; the module's own docstring states this is "not a machine-checked theorem" | `tests/test_inertia_count.py` |
| Resolved inertia count | `retained_spectral.inertia.resolved_count_below(kb, mb, sigma, ...)` | banded `kb`/`mb`, shift `sigma` | resolved (tolerance-aware) eigenvalue count below `sigma` | finite_diagnostic (same basis as above) | `tests/test_resolved_inertia.py` |
| Exact linear solve | `idm.solve({"kind": "matrix_solve", ...})` / `idm.kernel.poly.linsolve.linear_solve` | matrix + RHS over ℚ | exact rational solution (or rank-deficiency report) | exact | `tests/test_linsolve.py`, `tests/test_properties.py` |
| Gröbner basis | `idm.solve({"kind": "groebner_basis", ...})` / `idm.kernel.poly.groebner.reduced_groebner` | polynomial generators, ordering | reduced Gröbner basis | exact | `tests/test_groebner.py`, `tests/test_properties.py` |
| Rational-function limit | `idm.solve({"kind": "rational_limit", ...})` / `idm.kernel.poly.limits.rational_limit` | rational function, limit point | exact limit (finite/±∞/pole sign) | exact | `tests/test_limits.py`, `tests/test_properties.py` |
| Linear ODE (exact) | `idm.solve({"kind": "linear_ode", ...})` / `idm.kernel.poly.ode_linear.solve_linear_ode` | linear ODE with rational/constant coefficients | exact closed-form solution | exact | `tests/test_ode_linear.py`, `tests/test_properties.py` |
| Certified integral | `idm.certified.integral(f, a, b, eps)` (= `integral_stable_certified`) | function, bounds, tolerance | `Readout`: value + proven stability bound + `CERTIFIED`/`HOLD` | Th_coqc (`formal/IDM_Certified.v: abs_tailsum_le`, `refine_stable` — THEOREM.md §7) | `tests/test_idm_api.py::test_integral_certified` |
| Certified n-dimensional integral | `idm.certified.integral_nd(...)` (= `integral_nd_stable_certified`) | function over ℝⁿ region, tolerance | `Readout`: value + proven bound + `CERTIFIED`/`HOLD` | Th_coqc (reuses the same `refine_stable` theorem, dimension-agnostic — THEOREM.md §7) | `tests/test_multidim_quadrature.py` |
| Shortest path (min-plus) | `idm.solve({"kind": "shortest_path", "matrix": ...})` / `idm.shortest_path(W)` | weighted adjacency matrix | all-pairs shortest distances | Th_coqc (`IDM_Tropical.minplus_distrib`) | `tests/harness.py`, `tests/test_properties.py` |
| Critical path | `idm.solve({"kind": "critical_path", "matrix": ...})` / `idm.critical_path(W)` | weighted DAG adjacency | longest/critical path | exact (decorated `Th_coqc` in source but not in `_COQ_BACKED` — downgraded at call time; only `widest_path`/`minimax_path` keep `Th_coqc` among the path kinds) | `tests/harness.py`, `tests/test_properties.py` |
| Finite derivative | `idm.solve({"kind": "derivative", "f": ..., "x": ...})` / `idm.derivative(expr, x0)` | expression string, evaluation point | value via finite Dε + Richardson extrapolation | finite_diagnostic | `tests/test_idm_api.py`, `tests/harness.py` |
| Finite limit | `idm.solve({"kind": "limit", "seq": ...})` / `idm.limit(seq)` | sequence/expression | Richardson-extrapolated limit | finite_diagnostic | `tests/test_idm_api.py`, `tests/test_limits.py` |
| GCD (finite, exact) | `idm.solve({"kind": "gcd", "a": ..., "b": ...})` | two integers | exact gcd | exact (decorated `Th_coqc` in source, downgraded at call time — not in `_COQ_BACKED`) | `tests/test_idm_api.py`, `tests/harness.py` |
| Eigenvalues (general) | `idm.solve({"kind": "eigenvalues", "matrix": ...})` | matrix | eigenvalues to tolerance | finite_diagnostic | `tests/test_idm_api.py`, `tests/harness.py` |
| Bezout coefficients | `idm.solve({"kind": "bezout", "a": ..., "b": ...})` | two integers `a`,`b` | `{gcd, x, y}` exact extended-Euclid witness | exact (decorated `Th_coqc`, downgraded at call time) | `tests/test_idm_api.py::test_number_theory_extended` |
| Bipartite matching | `idm.solve({"kind": "bipartite_matching", "nL": ..., "nR": ..., "edges": ...})` | bipartite graph edges | maximum matching | exact (decorated `Th_coqc`, downgraded at call time) | `tests/test_idm_api.py`, `tests/harness.py` |
| Primality (deterministic) | `idm.solve({"kind": "is_prime", "n": ...})` | integer `n` | boolean, exact | exact (decorated `Th_coqc`, downgraded at call time) | `tests/test_idm_api.py`, `tests/harness.py` |
| Bessel J | `idm.solve({"kind": "bessel_J", "n": ..., "x": ...})` | order `n`, argument `x` | value to tolerance | finite_diagnostic | `tests/test_idm_api.py`, `tests/harness.py` |

## Notes on this table

- **"Tier" is the value returned by an actual call, not asserted from memory** — re-run
  `idm.solve({"kind": "<name>", ...})["tier"]` on your checkout if you need to confirm a tier
  hasn't changed (see the tier-honesty-pass caveat above — the raw `_REG` decorator tag can differ
  from the runtime tier for `Th_coqc`-decorated kinds).
- `tests/harness.py` is the differential + adversarial harness shared across many kinds (see
  `AI_START_HERE.md`) — it is listed as a verification file wherever a kind is covered by its
  data-driven `DIFFERENTIAL_CASES` / adversarial sweep rather than (or in addition to) a
  kind-specific unit test.
- `tests/test_properties.py` covers several `idm.kernel.poly` exact-CAS kinds via property-style
  checks in addition to their dedicated unit-test files.
- For the full 263-kind list grouped by area, read `API.md` (existing root doc) — this file adds
  the machine-searchable table format and per-row verification pointers that `API.md` does not
  have; it does not replace `API.md`'s narrative grouping.
