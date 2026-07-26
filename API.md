# `idm` — the library & solver API

Information Discrete Mathematics as a callable library and a REST service. Everything returns a
**finite-discrete readout**, tier-tagged (`Th_coqc` / `finite_diagnostic`), and — where a bound is
proven — a certificate with an `ACCEPT` / `HOLD` verdict. No continuum library call ever produces an
answer. The package is a clean facade over the repository's CI-verified modules.

## Install

```bash
pip install -e .          # from the repo root (brings in mpmath, sympy)
```

## Library

```python
import idm

idm.pi()                                  # π as a finite readout (Machin series)
idm.exp(0.7); idm.log(10); idm.sin(3)     # finite elementary functions
idm.derivative("exp(x)", 1)               # finite D_ε + Richardson
idm.integral(lambda x: x*x, 0, 3)         # finite I_ε quadrature
idm.limit(lambda n: (1+1/n)**n)           # Richardson on h=1/n

# certified computation — value + proven bound + ACCEPT/HOLD
r = idm.certified.geom_series(1/3, 1e-12) # Readout(q, bound, CERTIFIED)  — Th_coqc
r = idm.certified.exp(0.4, 1e-20)         # CERTIFIED for |x|≤½, else HOLD
r = idm.certified.integral(f, a, b, 1e-8) # finite-stability; HOLD if it doesn't stabilize

# optimization as semiring linear algebra (laws machine-checked in IDM_Tropical.v)
idm.shortest_path(W)                      # min-plus all-pairs
idm.widest_path(W); idm.critical_path(W); idm.reachability(W); idm.path_count(A)

# engineering readouts
idm.dashboard(data)                       # MIN/MAX/AVG/MEDIAN/PEAK/RMS/σ/… at once
```

## The solver — `idm.solve(problem)`

Give it a **structured** problem (the caller declares the `kind` — the framework's translate-first
rule: a world-language request becomes an information-language declaration before any math runs). It
dispatches to the right finite method and returns a normalized result.

```python
idm.solve({"kind": "integral", "f": "exp(-x**2)", "a": "-6", "b": "6", "eps": 1e-8})
# → {"kind":"integral","status":"CERTIFIED","tier":"finite_diagnostic",
#    "value":{"digits":"1.7724538509055159891…","float":1.772453…},
#    "bound":{…},"method":"trapezoid refinement stability (refine_stable)"}
```

**230 problem kinds** (`GET /kinds` lists them live; `idm.kinds()` in Python), grouped by area:

**Symbolic (exact CAS)** — `symbolic_diff` (`expr`,`var`) · `simplify` · `expand` · `symbolic_integrate` (polynomial + elementary, HOLD when no elementary antiderivative) · `symbolic_solve` (linear/quadratic radicals, rational roots) · `symbolic_series` (exact Taylor)

**Certified computation** (ships a proven bound + ACCEPT/HOLD)
`geometric_series` (`r`,`eps`) · `exp` (`x`,`eps`) · `integral` (`f`,`a`,`b`,`eps`) · `certified_limit` (`seq`,`eps`)

**Transforms & complex analysis** — `laplace_transform` (`f`,`s`) · `inverse_laplace` (`F`,`t` — fixed Talbot) · `mellin_transform` · `fourier_transform` (`f`,`omega`) · `fft` / `ifft` (`x`) · `z_transform` (`x`,`z`) · `contour_integral` (`f`,`center`,`radius`) · `argument_principle` (#zeros−#poles) · `residue_integral`

**Special functions** (finite series / recurrences / AGM / continued fractions) — `gamma` · `beta` · `digamma` · `bessel_J`/`bessel_I` · `legendre_P` · `hermite_H` · `laguerre_L` · `chebyshev_T`/`_U` · `erf`/`erfc` · `Ei`/`E1`/`li` · `Si`/`Ci` · `fresnel_S`/`_C` · `elliptic_K`/`elliptic_E` (AGM) · `hyp2f1`/`hyp1f1` · `airy_Ai` · `lambert_W` · `polylog` · `dirichlet_eta`/`dirichlet_beta` · `hurwitz_zeta`

**Limits & series** — `taylor_series` (`f`,`x0`,`n`) · `laurent_series` · `fourier_series` (`f`,`n`) · `pade` (`coeffs`,`m`,`n`) · `series_accelerate` (`term` — Wynn ε) · `convergence_test` (`term` → CONVERGES/DIVERGES/**HOLD** on the harmonic/Bertrand boundary) · `limit_oneside` · `limit_infinity` · `lhopital`

**Differential equations** (finite-difference readouts) — `ode_system` (`f` list, `vars`, `x0`, `y0` vector, `xT`) · `ode_bvp` (`q`,`r`,`a`,`b`,`alpha`,`beta`) · `pde_heat` (Crank–Nicolson) · `pde_wave` (leapfrog) · `pde_poisson` / `pde_laplace` (Gauss–Seidel, 2-D) · `sturm_liouville` (eigenvalues by Sturm bisection). Each takes an optional `at` to read the solution at a point.

**Integration flagship** (double-exponential DE quadrature — absorbs endpoint singularities and infinite ranges, a-posteriori certified) — `integral` (auto: finite/singular/infinite, `a`/`b` may be `inf`/`-inf`) · `improper_integral` · `singular_integral` · `oscillatory_integral` · `gauss_quadrature` (`n`) · `residue_integral` (`num`,`den`) · `multidim_integral` (`f`,`vars`,`bounds`)

**Constants & functions** — `constant` (`name`) · `function` (`name`,`x`) · `evaluate` (`expr`,`vars`)

**Discrete calculus** — `derivative` (`f`,`x`) · `limit` (`seq`) · `ode` (`f`,`x0`,`y0`,`xT`) ·
`double_integral` (`f`,`ax`,`bx`,`ay`,`by`) · `series_sum` (`term`,`N`) · `zeta` (`s`) ·
`regularized_sum` (`power`) · `root_find` (`f`,`a`/`b`/`x0`) · `minimize` (`f`,`a`,`b`) · `interpolate` (`points`,`x`)

**Continuous optimization** — `gradient_descent` (`f`,`vars`,`x0`) · `newton_min` · `newton_system` (`F` list) · `least_squares` (`A`,`b` — exact ℚ) · `lagrange_min` (`f`,`constraints`,`vars`,`x0` — KKT)

**Number theory** (exact, `Th_coqc`-tier) — `gcd` · `lcm` · `factorial` · `binomial` · `is_prime` ·
`factorize` · `divisors` · `totient` · `primes` (`N`) · `modpow` · `mod_inverse` · `crt` · `fibonacci` ·
`bernoulli` · `partition` · `catalan` · `stirling2` · `bell` · `continued_fraction`

**Exact linear algebra** — `matrix_multiply` · `matrix_determinant` · `matrix_inverse` · `solve_linear`
(`A`,`b`) · `char_poly` · `eigenvalues` (exact-ℚ char poly + Durand–Kerner)

**Polynomials** — `poly_eval` · `rational_roots` (exact) · `poly_roots` (all complex)

**Optimization / paths** (tropical semirings, `Th_coqc` laws) — `shortest_path` · `critical_path` ·
`widest_path` · `minimax_path` · `reachability` · `path_count` (`matrix`, opt. `source`/`target`)

**P2 · statistics & probability** (exact ℚ where possible) — `binomial` · `poisson` · `hypergeometric` · `geometric` · `normal` · `describe` · `z_test` · `t_test` · `chi_square_test` · `regression` (exact ℚ polynomial least-squares) · `multiple_regression` · `markov_absorbing` · `stationary` · `bayes_update`

**P2 · computational geometry** (EXACT rational predicates — no epsilon) — `orient` · `convex_hull` · `point_in_polygon` · `segments_intersect` · `closest_pair` · `in_circle` (Delaunay)

**P2 · cryptographic number theory** (exact, certificate-bearing) — `primality_certificate` (deterministic Miller–Rabin + checkable base-set certificate) · `modinv` · `rsa_keygen` · `rsa_encrypt` · `rsa_decrypt` · `ec_add` · `ec_mul` (elliptic curve over F_p)

**P1 · rigorous certification** (interval arithmetic — guaranteed enclosures) — `interval_enclose` · `verified_range` (rigorous [min,max]) · `certified_root` (root proven by IVT, else HOLD) · `certified_min` (global-minimum bracket) · `gershgorin` (eigenvalue discs)

**P1 · number theory (advanced)** — `diophantine_linear` · `pell` · `modular_sqrt` (Tonelli–Shanks) · `mobius` · `mertens` · `liouville` · `von_mangoldt`

**P1 · linear algebra (advanced)** — `matrix_exp` · `null_space` · `hermite_normal_form` · `smith_normal_form`

**P1 · combinatorial optimization** — `knapsack` · `subset_sum` · `lcs` · `edit_distance` · `coin_change` · `dijkstra` · `bellman_ford` · `bipartite_matching` · `assignment` (Hungarian) · `spanning_tree_count` (Kirchhoff) · `chromatic_number` · `linear_program` (exact-ℚ simplex) · `sat` (DPLL)

**Number theory (extended)** — `num_divisors` · `sigma` · `next_prime` · `prime_pi` · `integer_sqrt` ·
`is_perfect_square` · `integer_root` · `digital_root` · `base_convert` · `bezout` · `legendre_symbol` ·
`jacobi_symbol` · `discrete_log` · `primitive_root` · `lucas` · `derangements` · `perm_count` ·
`comb_with_rep` · `multinomial` · `faulhaber`

**Polynomial algebra** — `poly_add` · `poly_mul` · `poly_divmod` · `poly_gcd` · `poly_derivative` ·
`poly_integral` · `poly_from_roots`

**Matrix (extended)** — `matrix_transpose` · `matrix_trace` · `matrix_add` · `matrix_power` ·
`matrix_rank` · `rref`

**Geometry (exact ℚ)** — `dot` · `cross` · `polygon_area` · `triangle_area` · `distance` · `vector_norm`

**Analysis (extended)** — `gradient` · `convolution` · `arc_length` · `fixed_point` · `summation`

**Discrete structures** — `mst` · `connected_components` · `topological_sort` · `is_bipartite` ·
`max_flow` · `set_operation` · `powerset` · `truth_table`

String `f`/`seq` are evaluated in a **locked finite namespace** — `exp`/`log`/`sin`/`cos`/`erf`/`sqrt`/`pi`
resolve to the framework's finite functions, no Python builtins, so even a user's `exp(-x**2)` is
computed finitely.

## REST API (zero dependencies)

```bash
python3 -m idm.server            # or:  idm-serve  (or)  python3 -c "import idm; idm.serve()"
# idm solver API on http://127.0.0.1:8737
```

| method / route | purpose |
|---|---|
| `GET /health` | liveness + version + theorem count |
| `GET /` | endpoint catalogue + example bodies |
| `GET /openapi.json` | minimal OpenAPI 3 description |
| `POST /solve` | body = a structured problem; returns the certified result |

```bash
curl -s -X POST http://127.0.0.1:8737/solve \
  -H 'Content-Type: application/json' \
  -d '{"kind":"integral","f":"exp(-x**2)","a":"-6","b":"6","eps":"1e-8"}'
```

A solver error is returned as a `HOLD` result, never a crash — the API refuses rather than fabricates.

---

## Cross-cutting (world-class UX)

- **Natural-language front-end** — `idm.parse(text)` translates a world-language request into a structured `{kind,…}` (echoing the source so it's checkable), or returns HOLD with candidate kinds; `idm.parse_and_solve(text)` translates then solves. It never mis-routes: an unrecognized request HOLDs.
- **OpenAPI 3 / Swagger UI** — `python3 -m idm.server` serves `POST /solve` (structured *or* `{text:…}`), `POST /parse`, `GET /kinds`, `GET /openapi.json`, and an interactive **Swagger UI at `/docs`** — the same surface as a FastAPI app, with zero web-framework dependency (stdlib `http.server`).
- **Coq end-to-end for the exact geometry predicate** — `formal/IDM_Geometry.v` machine-checks (axiom-free) the algebraic soundness of the orientation determinant the geometry solver branches on: antisymmetry, cyclic invariance, translation invariance, positive-scale sign preservation, and exact-zero-on-boundary (why `point_in_polygon` detects the boundary with no epsilon). 65 theorems total in `formal/`.
