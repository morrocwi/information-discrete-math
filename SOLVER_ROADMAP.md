# Solver Roadmap — a STANDALONE world-class math solver that computes the continuum, finitely

**Goal.** A self-contained math engine (library + REST API + CLI) that takes *any* mathematical problem —
above all the ones that classically demand the continuum (integrals, ODEs, PDEs, limits, series, special
functions, transforms, complex analysis) — and returns the answer as a **certified finite-discrete
readout**, never forming the completed continuum. A standalone product in the class of SymPy / SciPy /
Wolfram, whose one unmatched claim is: *the continuum computed, not assumed* — with a certificate.

Current state: **104 problem kinds** (`idm.kinds()`), strong on exact/discrete; the continuum frontier is
proven at demonstration scale (`prove_it_full.py`, 1278 problems) but not yet exposed as on-demand
solver kinds with certificates. This roadmap closes that gap. Priority order = **continuum first**.

Legend — **FIT** = how well it plays to our readout-first edge (exact · finite · decidable · certified ·
RCP savings). Method column names the *finite* mechanism (there is always one).

---

## P0 — The continuum frontier, computed finitely  ← ✅ DONE (all six blocks shipped)

> **Status:** P0.1 Integration · P0.2 ODE/PDE · P0.3 Limits/Series · P0.4 Special functions · P0.5 Transforms/Complex · P0.6 Continuous optimization — all implemented as `idm` solver kinds, verified against references, 169 kinds total.

### P0.1 Integration (the flagship)
| kind | classical target | finite method | FIT |
|---|---|---|---|
| `improper_integral` | ∫₀^∞, ∫_{−∞}^∞ | cutoff + Euler–Maclaurin tail + `refine_stable` certificate | ★★★ |
| `singular_integral` | integrable singularities | variable substitution (t=x²…) to a finite derivative, then Simpson | ★★★ |
| `oscillatory_integral` | ∫ f·e^{iωx}, Fresnel | Filon / stationary-phase finite quadrature | ★★★ |
| `multidim_integral` | ∫_{ℝⁿ} | separable product or **retained-graph contraction (RCP)** for coupled | ★★★ |
| `principal_value` | Cauchy PV | symmetric finite limit + subtraction | ★★ |
| `contour_integral` | ∮, residues | finite residue sum (poles via `poly_roots`) | ★★ |
| `line/surface/volume_integral` | vector calculus | finite parametrized quadrature | ★★ |
| `gauss_quadrature` | high-accuracy ∫ | finite Gauss–Legendre nodes (already in `provefull`) | ★★★ |

All ship an **a-posteriori error bound + ACCEPT/HOLD** (extends `certified.integral`).

### P0.2 Differential equations
| kind | target | finite method | FIT |
|---|---|---|---|
| `ode_system` | y′=f(x,y), vector | finite RK4/RK45 (adaptive) | ★★★ |
| `ode_bvp` | boundary-value | finite shooting / finite-difference | ★★ |
| `stiff_ode` | stiff systems | finite implicit (backward Euler / BDF, exact-ℚ Newton) | ★★ |
| `sturm_liouville` | eigenvalue ODE | finite-difference matrix eigenvalues | ★★ |
| `pde_heat/wave/laplace/poisson` | u_t=Δu, □u, Δu=0/f | finite-difference stencil + `refine_stable` | ★★★ |
| `pde_schrodinger/advection_diffusion` | quantum / transport | finite-difference / spectral | ★★ |
| `delay_ode` | delayed argument | finite method-of-steps | ★ |

(Ties directly to the physics-solver goal and to RCP-Energy planning.)

### P0.3 Limits, series, summation
| kind | target | finite method | FIT |
|---|---|---|---|
| `limit_multivar` · `limit_oneside` · `limit_infinity` | lim | Richardson / path-wise finite readout | ★★★ |
| `lhopital` | 0/0, ∞/∞ | finite derivative ratio | ★★ |
| `series_expansion` | Taylor/Laurent/asymptotic | finite differences / recurrence | ★★★ |
| `fourier_series` | periodic expansion | finite DFT coefficients | ★★★ |
| `series_accelerate` | slow/divergent | Shanks · **Padé** · Levin · Euler–Maclaurin · Borel (have some) | ★★★ |
| `convergence_test` | Σ converges? | finite ratio/root/integral test with certificate → HOLD if undecided | ★★★ |
| `divergent_regularize` | ζ/Abel/Borel/Cesàro | finite smoothed sum + Richardson (have `regularized_sum`) | ★★★ |

### P0.4 Special functions — the continuum's alphabet, all finite series
`bessel_J/Y/I/K` · `legendre/hermite/laguerre/chebyshev` · `hypergeometric` (₂F₁, ₚFᵩ) ·
`elliptic_K/E/Pi` · `Ei/li/Si/Ci` (exp/log/sin/cos integrals) · `polylog` · `lambert_W` · `airy` ·
`dirichlet_L/eta/beta` · `theta` · `digamma/polygamma` · `zeta_hurwitz`. **FIT ★★★** — each is a finite
series/quadrature/continued-fraction (much is already computed in `provefull/`, needs exposing as kinds).

### P0.5 Transforms & complex analysis
`fourier_transform` (+ inverse, full FFT) · `laplace_transform` (+ inverse) · `z_transform` ·
`mellin_transform` · `wavelet` · `residues` · `laurent_series` · `conformal_map`. **FIT ★★** — finite
discrete transforms; the "continuous" transform is the readout of the finite one.

### P0.6 Continuous optimization
`gradient_descent` · `newton_multivar` · `constrained_lagrange/KKT` · `convex_min` · `least_squares`
(exact-ℚ normal equations). **FIT ★★** — finite iterations with convergence certificates.

---

## P0-support — Symbolic layer  ← ✅ DONE (exact CAS: idm/symbolic.py)

> **Status:** our own exact symbolic engine — parse · diff · simplify · expand · integrate (HOLD when no elementary antiderivative) · solve · Taylor series — shipped as solver kinds. SymPy used only as a test reference.

### original plan

A world-class engine must manipulate expressions, not only evaluate them. **FIT ★★** (an expression is a
finite tree = a finite readout; no continuum needed to transform it).

- `symbolic_diff` (exact) · `simplify` · `expand` · `factor` (polynomials/expressions)
- `symbolic_integrate` (elementary/rational antiderivatives; Risch-lite)
- `symbolic_solve` (polynomial exact radicals: quadratic/cubic/quartic; systems; some transcendental)
- `symbolic_limit` · `symbolic_series` · `partial_fractions` · `substitute` / `collect`
- `symbolic_ode_solve` (linear, separable, exact, integrating-factor)

> **Design decision to make:** build a small **exact symbolic tree engine** (most on-brand — exact,
> finite, no external authority) vs wrap SymPy as a reference comparator. Recommended: our own minimal
> engine for the core, with SymPy only in the *reference* column of tests (never producing `ours`).

---

## P1 — Exact / discrete backbone (our home turf; extends the 104)

- **Exact linear algebra:** `lu/qr/cholesky/svd` · `eigenvectors` · `null_space/column_space` ·
  `smith_normal_form` / `hermite_normal_form` (integer — pure discrete) · `matrix_exp` (finite series) ·
  `jordan_form` · `least_squares` · `condition_number`. **FIT ★★★**
- **Number theory (advanced):** `diophantine_linear` · `pell` · `modular_sqrt` (Tonelli–Shanks) ·
  `quadratic_residues` · `elliptic_curve` point arithmetic · `mobius/mertens/liouville/vonmangoldt` ·
  `dirichlet_convolution` · `p_adic_valuation`. **FIT ★★★** (most on-brand possible)
- **Combinatorics & generating functions:** `partitions_enumerate` · `gf_coefficient` ·
  `solve_recurrence` (closed form) · `sequence_guess` (OEIS-style) · `burnside/polya`. **FIT ★★★**
  (generating functions are already framed finite-discrete, textbook §9.5)
- **Graph (advanced):** `dijkstra/bellman_ford` with path reconstruction · `assignment` (Hungarian) ·
  `min_cost_max_flow` · `bipartite_matching` (Hopcroft–Karp) · `spanning_tree_count` (Kirchhoff — graph +
  exact linear algebra) · `eulerian/hamiltonian` · `chromatic_number` · `graph_isomorphism` (small). **FIT ★★★**
- **Optimization (discrete/exact):** `linear_program` (simplex, **exact-ℚ pivoting**) · `integer_program`
  (branch & bound) · `knapsack/subset_sum/lcs/edit_distance` (DP = retained-record elimination, **RCP-adjacent**). **FIT ★★★**
- **Logic / decision:** `sat` (DPLL) · `cnf/dnf` · `quine_mccluskey` minimization · `resolution` ·
  `finite_model_finder` (we already prove `finite_satisfaction_dec` in Coq). **FIT ★★★**

---

## P1 — Certification everywhere  ← ✅ DONE (interval arithmetic layer)

> **Status:** idm/interval.py — rigorous enclosures via validated interval arithmetic: verified_range, certified_root (proven by IVT), certified_min (branch-and-bound), gershgorin eigenvalue discs. Shipped as solver kinds.

### original

Make **every** continuum computation return `(value, proven error bound, ACCEPT/HOLD)`, not just the
current four. The world-class edge is not "it computes the integral" (SciPy does) but "it computes it
**with a guarantee, or honestly refuses**."

- interval arithmetic layer (rigorous enclosures over ℚ)
- a-posteriori error estimators per method (quadrature, ODE, root, eigenvalue via Gershgorin)
- certified root-finding (interval Newton / Krawczyk)
- promote the tier of a result to `Th_coqc` when a Coq witness backs the method (as geometric/exp/
  integral-stability already are). **FIT ★★★**

---

## P2 — Rounding out  ← ✅ DONE

> **Status:** idm/stats.py (exact-ℚ distributions/regression/Markov/Bayes + finite-readout tests), idm/geometry.py (exact rational predicates — hull, area, in/out, intersection, Delaunay in-circle), idm/crypto.py (deterministic primality certificate, RSA, discrete log, elliptic curve over F_p). Shipped as solver kinds.

### original

- **Statistics / probability:** discrete distributions (pmf/cdf: binomial/Poisson/normal/…) ·
  hypothesis tests · multiple/polynomial regression · Markov chain hitting/absorbing times · Bayesian update.
- **Computational geometry (exact ℚ predicates):** convex hull · Delaunay/Voronoi · segment intersection ·
  point-in-polygon · closest pair · polytope volume.
- **Special-domain packs:** signal processing, control systems, cryptographic number theory
  (RSA/ECC/primality certificates), physics constants.

---

## Cross-cutting (what actually makes it "world-class")

1. **Certificate + provenance + tier on every result** (extend the `Readout` contract everywhere).
2. **Correctness/benchmark suite** vs SymPy / SciPy / Wolfram — same shape as the RCP competitor
   benchmark: prove bit-identical answers *and* the finite/exact/savings advantage.
3. **Natural-language → structured problem** front end (LLM-assisted, translate-first), so a human can
   ask in words and the engine declares the `kind` before computing.
4. **FastAPI + OpenAPI/Swagger UI** and thin client libraries around the existing zero-dep server.
5. **Property-based testing / fuzzing** per solver; every `finite_diagnostic` states its tolerance.
6. **Symbolic ↔ numeric bridge** (a symbolic answer must be evaluable finitely, and vice-versa).

---

## Strategic principle

Chase the **continuum frontier first** (P0) — that is where readout-first is *uniquely* world-class:
everyone else assumes the continuum; we return its answers as certified finite readouts. Where SciPy/
Wolfram already dominate raw numerics, our wedge is **exactness + certification + no-continuum + RCP
savings**, not raw speed. Every new kind should either (a) conquer a continuum problem finitely, or
(b) do it exactly/decidably where others approximate — ideally both, with a certificate.
