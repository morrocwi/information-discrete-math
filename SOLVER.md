# The Solver — what it solves, and how far (scope at a glance)

> One entry point — `idm.solve({"kind": ..., ...})` — over **268 registered problem kinds across 11
> domains**. Every answer is **tier-tagged** and is one of three honest verdicts: **EXACT**,
> **CONDITIONAL** (result + declared scope/bound), or **HOLD** (explicit refusal, never a fabricated
> number). This page tells a human or an AI, in one read, *what the solver can and cannot do* — grounded
> in the live registry (`capabilities.json`) and the knowledge graph (`docs/knowledge_graph.json`), not
> in prose.

```python
import idm
idm.solve({"kind": "eigenvalues",  "M": [[2, 1], [1, 2]]})     # EXACT   → 1, 3 (exact ℚ)
idm.solve({"kind": "integral", "f": "exp(-x**2)", "a": "-inf", "b": "inf"})  # CONDITIONAL → √π, proven bound
idm.solve({"kind": "symbolic_solve", "equation": "sin(x)=x/2", "var": "x"})  # HOLD → "non-polynomial" (with reason)
idm.kinds()          # the full list of 268 kind names
idm.parse_and_solve("factor x^2 - 5x + 6")     # plain language → structured kind → solve
```

Discover from the shell: `python -m idm list` · `python -m idm describe <kind>` · `python -m idm example <kind>`.

## Scope at a glance — 11 domains, 266 kinds

| domain | kinds | what it solves (from real kind names) | typical verdict |
|---|---:|---|---|
| **calculus** | 76 | derivatives, integrals, limits, series; special functions (Bessel, Airy, Ei/Si/Ci, beta, Chebyshev, elliptic, hypergeometric), contour integral, convergence tests | EXACT (poly/rational) · CONDITIONAL (numeric, declared tolerance) |
| **number_theory** | 50 | CRT, discrete log, linear Diophantine, elliptic-curve add/mul, Bernoulli/Catalan/Bell, binomial, divisors, base conversion | EXACT |
| **other** | 37 | graphs (Dijkstra, Bellman–Ford, matching, chromatic, components), DP (coin change, edit distance), statistics (Bayes, χ²), critical path | EXACT |
| **hilbert** | 25 | inner product, Gram–Schmidt, adjoint / self-adjoint / unitary, Choi / CP maps; the +ℝ-Open readouts (ℓ²/L²/completeness) with a ℚ `computed_core` | EXACT · +ℝ-Open (fenced) |
| **exact_algebra** | 21 | polynomial ops (gcd, divmod, expand, factor), Gröbner basis, Bézout, Padé, continued fraction, integer root | EXACT |
| **linear_algebra** | 17 | determinant, inverse, rank, RREF, nullspace, solve; matrix exponential, Hermite normal form, least squares | EXACT · CONDITIONAL |
| **geometry** | 11 | convex hull, closest pair, exact orientation / in-circle predicates, polygon area, segment intersection | EXACT |
| **certified** | 8 | a value **plus a proven error bound**, or an honest HOLD (limit, root, min, positivity, interval enclosure) | CONDITIONAL (proven bound) |
| **pde** | 8 | ODE / systems / BVP, heat / wave / Laplace / Poisson (finite-ε) | CONDITIONAL (numeric) |
| **spectral** | 6 | eigenvalues, characteristic polynomial, spectral decomposition, Gershgorin bounds | EXACT (real) · CONDITIONAL (complex, numeric) |
| **logic** | 4 | SAT, truth table, set operations, assignment | EXACT |

*(counts are generated from the live registry into `capabilities.json`; a CI gate fails if they drift
from `len(idm.kinds())`.)*

## The three verdicts (the real guarantee)

The solver's warrant is not breadth — it is that **every answer states its own standing**:

- **EXACT** — exact over ℤ/ℚ / algebraic / machine-checked (`Th_coqc`). No float in the result.
- **CONDITIONAL** — a result **with** its declared scope: a proven error bound (`certified` domain), a
  `finite_diagnostic` numeric value with its tolerance, or a `completeness="partial"` solution set with
  the unresolved residual stated.
- **HOLD** — an explicit refusal with a reason (non-polynomial equation, singular matrix, inconsistent
  system, a limit that does not plateau, a resource budget exceeded). **Never a guessed number.**

Read the tier tag on any result before trusting it — see the README's
[Evidence ladder + honesty tiers](README.md#evidence-ladder--honesty-tiers).

## The exact symbolic (CAS) layer — honest boundary

The solver contains a real, our-own exact symbolic engine (`idm.kernel.cas` + `idm.kernel.poly.*`), but
it is **not** a general CAS. Its audited closure status against a full 19-section CAS checklist is:
**40 CLOSED / 67 PARTIAL / 150 OPEN** — see **[`docs/CAS_CLOSURE_CHECKLIST.md`](docs/CAS_CLOSURE_CHECKLIST.md)**
for the per-item evidence. In short:

- **Strong (EXACT, tested):** univariate polynomial factorization / resultant / discriminant / Sturm /
  real-root isolation, Gröbner bases (with a fail-closed budget), rational-function limits, exact real
  eigenvalues + matrix minimal polynomial, constant-coefficient linear ODEs, and an **unusually strong
  verification stack** (differential testing vs SymPy *as comparator only*, adversarial + property-based
  harnesses, pervasive real HOLD-not-fake).
- **Open (declared, not hidden):** algebraic-number field arithmetic (`RootOf`), symbolic integration
  (Hermite/Risch), branch-aware complex algebra, parametric/symbolic linear algebra, special-function
  and transform *symbolic* layers, inequality solving, CAD/quantifier elimination.

Do **not** infer a capability from this page alone: check `python -m idm describe <kind>` or the checklist.

## Connected to the Knowledge Graph

Each capability is traceable end-to-end in **[`docs/knowledge_graph.json`](docs/knowledge_graph.json)**,
which links every claim through the chain:

```
claim → API (idm kind) → implementation file(s) → tests → benchmark → theory (formal/*.v or the textbook)
```

so a reader (human or AI) can go from "the solver claims X" to the exact code, the test that guards it,
and the machine-checked theorem or textbook section that grounds it — without trusting the prose. The
registry (`capabilities.json`), the CLI (`python -m idm`), and this scope map are all generated from or
gated against the same live `idm.solve` registry, so they cannot silently disagree.

## For AI agents (how to establish scope before answering)

1. **List, don't guess:** `idm.kinds()` or `python -m idm list` — the authoritative capability set.
2. **Describe before using:** `python -m idm describe <kind>` — its arguments and effective tier.
3. **Read the boundary:** this file's scope table + `docs/CAS_CLOSURE_CHECKLIST.md` for what is *not* closed.
4. **Trust the verdict, not the prose:** a result is EXACT / CONDITIONAL / HOLD — report it as such;
   if the kind you need is OPEN, say so plainly rather than inferring an answer.

Full API reference: [`API.md`](API.md) · roadmap: [`SOLVER_ROADMAP.md`](SOLVER_ROADMAP.md) · discovery
order for AI: [`AI_START_HERE.md`](AI_START_HERE.md).
