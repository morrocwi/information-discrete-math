# CAS Closure Checklist — honest status of the solver's exact symbolic engine

> **What this is.** A tier-honest audit of the solver's Computer-Algebra-System (CAS) surface against a
> full general-CAS closure checklist (19 sections, ~257 items). Produced by a read-only, evidence-based
> sweep of the real code (`idm/kernel/cas.py`, `idm/kernel/poly/*`, `idm/kernel/{assumptions,engine,
> nodes,numbers,simplify,solution,hashcons}.py`, `idm/{exact,special,series,transforms,diffeq,analysis,
> integrate,continuum,certified,hilbert}.py`, the `@kind` registry, and the test suite). Every CLOSED
> verdict cites a real `file:func` and, where present, a test. **No inflation.**
>
> **Legend:** `[x]` CLOSED (real exact/ℚ implementation, ideally tested) · `[~]` PARTIAL (exists but
> limited, or numeric-only where a *symbolic* result was asked) · `[ ]` OPEN (not implemented).

## Headline

| | count | share |
|---|---|---|
| `[x]` CLOSED | **40** | ~16% |
| `[~]` PARTIAL | **67** | ~26% |
| `[ ]` OPEN | **150** | ~58% |

**The honest verdict:** this is **not** a general CAS (SymPy/Mathematica-scale). It is a **narrow,
tier-honest exact-ℚ core** — polynomials, rational limits, real eigenvalues, constant-coefficient linear
ODEs, Gröbner bases — wrapped in **unusually strong verification infrastructure** (differential testing
vs SymPy as a *comparator only*, adversarial + property-based harnesses, pervasive real `HOLD`-not-fake
behavior). Its strengths are exactness and honesty, not breadth.

> **What the OPEN count does and does not mean.** This table counts **reachability from the *public*
> `symbolic_*` surface**. A founder pass over the kernel (2026-07-29) established that a substantial share
> of the OPEN/PARTIAL items are **already implemented inside the kernel and merely not wired to the public
> CAS** — e.g. Gosper summation, `Relation`/`Piecewise`/unevaluated `Derivative/Integral/Limit` nodes, the
> assumption object, the guarded rewrite, root isolation. So the remaining work is **not ~150 things to
> build from scratch**; it is **14 work packages over four root layers** (move the public CAS onto one
> kernel · complete algebraic/complex exact arithmetic · add expression-level reasoning · connect the core
> to close solve/calculus/linear-algebra with certificates). The prioritized plan lives in
> `BACKLOG.md` → *"CAS closure — the 14 work packages"*; read the per-item evidence below alongside it.

Two architectural facts shape the picture:
1. **Two parallel expression systems.** The live engine `idm/kernel/cas.py` is a tuple/`Fraction` tree
   with recursive `simplify`/`expand`/`diff`/`integrate` (no general rewrite engine). A newer, richer
   `idm/kernel/nodes.py` Expr-tree + `engine.py` pattern-rewrite engine exists but is **mostly unwired**
   ("not yet the wire format any kind speaks", `nodes.py:1-6`) and carries exactly one gated rule. Much
   of §1/§7's structural machinery lives only in that shadow layer.
2. **Exact core vs numeric periphery.** Polynomials / limits / eigenvalues / ODE-characteristic work is
   genuinely exact-ℚ. Special functions, transforms, and most integration/series are **finite-ε numeric**
   (`mpmath`, `finite_diagnostic`) — honest and extensive, but **not** symbolic-exact, so they score
   PARTIAL/OPEN against a *symbolic* checklist.

---

## §1 Expression structure — 2 / 6 / 1 (CLOSED/PARTIAL/OPEN of 9)
- [x] equivalent forms → one canonical form — `cas.py:simplify` (add/mul collect like-terms, sort by `tostr` key) + `nodes.py Add/Mul` sort by `_order`
- [x] deterministic term/factor ordering — `hashcons.py:canonical_order_key` (tested) — *but only wired into the unused `nodes.py` tree; live path uses `tostr` compare*
- [~] unevaluated `Integral`/`Derivative`/`Limit`/`Sum`/`Product`/`RootOf` — `nodes.py:220-267` has Derivative/Integral/Limit classes; **no** Sum/Product/RootOf, and `cas.integrate` raises `_Hold` instead of returning an `Integral(...)`
- [~] `Piecewise` — `nodes.py:203-217` class exists, "defined, unused by any rewrite path"; nothing constructs one
- [~] relations as objects (Eq/Ne/Lt/Le/Gt/Ge) — one generic `Relation(op,lhs,rhs)` node (`nodes.py:185-199`), no per-op constructors, unused elsewhere
- [~] symbolic set & interval — only `assumptions.py:Interval` (engine-internal domain bookkeeping), not a math-value object
- [x] expression DAG / hashconsing — `hashcons.py:InternTable.intern` (tested) — *request-scoped, only for the unused `nodes.py` tree*
- [~] central rewrite termination budget — `engine.py:LoopGuardConfig(max_passes=32)` guards the 1-rule engine only; `max_steps` field is dead; `cas.simplify` is unbounded structural recursion
- [~] proof trace — `engine.py:RewriteResult.fired` exists for the 1-rule engine path only; `cas.simplify` produces none

## §2 Assumptions & domain — 3 / 5 / 1 (of 9)
- [~] infer symbol domain (ℤ,ℚ,ℝ,ℂ) — `assumptions.py:PredKind.{INTEGER,RATIONAL,REAL}` + ℤ⊂ℚ⊂ℝ closure; **no ℂ predicate**
- [x] positive/negative/zero/nonzero — `assumptions.py:PredKind.{POSITIVE,NEGATIVE,NONNEG,NONPOS,NONZERO}` + interval closure (tested)
- [x] integer/even/odd/prime — `assumptions.py:PredKind.{EVEN,ODD,INTEGER,PRIME}` + closure rules
- [x] detect contradictory assumptions — `SymbolDomain.is_contradictory`, raises `DomainContradiction` (tested)
- [ ] propagate assumptions through +,×,^,funcs — only *requirement-collection* (`domain_of_expr`); no "positive×positive⇒positive" forward inference
- [~] every domain-dependent rewrite guarded — only `pow_pow_collapse` is routed through the guard; other domain-sensitive steps are ungated
- [ ] `sqrt(x²)=|x|` — no special case in `cas.simplify`; **no `Abs` node/function anywhere**
- [~] nested powers `(xᵃ)ᵇ` per domain — gated *only when assumptions passed*; default (`assumptions=None`) path still collapses unconditionally
- [~] track restrictions (denominator ≠ 0) — `domain_of_expr` emits NONZERO for negative-exponent bases; nothing carries it into a result

## §7 Simplification — 4 / 8 / 6 (of 18)
- [x] pattern matcher — `engine.py:match/substitute`, `Wildcard` (tested) — structural, small
- [x] wildcard patterns — `engine.py:Wildcard`
- [ ] associative matching — `engine.py:81-82` "positional match only" (deferred)
- [ ] commutative matching — same (documented not-yet-implemented)
- [~] conditional rewrite rules — `engine.py:Rule.guard` real+tested, but only ONE rule registered
- [~] rewrite priority — `Rule.priority` honored, but 1 rule → never meaningfully exercised
- [ ] cost function — absent
- [x] polynomial normalization — `cas.expand`+`simplify` + `poly/univariate.py` tower (exact ℚ)
- [x] rational normalization — `simplify.py:cancel_rational` → `poly.cancel` (tested) — univariate only
- [ ] radical simplification — `sqrt(4)` stays `4**(1/2)`, never reduces to `2`
- [ ] trig identities — only 4 hardcoded special values (sin0/cos0/exp0/log1); no sin²+cos²
- [ ] exp/log identities — none (`log(exp x)`, `exp(log x)`, `log(ab)` absent)
- [~] complex expansion — `numbers.py:ComplexExact` rung exists but not integrated into `cas.py`
- [~] controlled factor/expand — `expand` real (bounded deg≤12); `factor` exists only at poly level (`factorize.py`), not as `cas.factor(expr)`
- [x] special-value simplification — `cas.py:112-118` (4 hardcoded cases)
- [ ] identity checking — no `is_equal`/`equivalent` API
- [ ] bounded `full_simplify` — no such function
- [~] rewrite-loop prevention — guards the 1-rule engine only
- [~] simplify preserves domain — true only for the one gated rule

## §3 Rational-expression algebra — 3 / 4 / 3 (of 10)
- [~] `together` — `partial_fractions.py:together` recombines an `apart` decomposition only; not a general n-term combiner
- [x] `cancel` — `poly/univariate.py:cancel` / `simplify.py:cancel_rational`, gcd lowest-terms exact ℚ (tested)
- [x] `apart` — `partial_fractions.py:apart`, square-free variant (tested, 17) — *doc discloses it doesn't split square-free blocks per irreducible factor*
- [x] split numerator/denominator — same `UPoly` machinery
- [~] normalize rational function to one form — `cancel_rational` on a single num/den pair; no general canonicalization of an arbitrary rational subtree
- [~] exact comparison of rational expressions — derivable via `cancel_rational`, no dedicated API
- [ ] track undefined points hidden by cancellation — not tracked
- [ ] multivariate rational functions — all rational ops are univariate (`UPoly`) only
- [x] partial fractions over ℚ — same as `apart` (square-free)
- [ ] partial fractions over algebraic extensions — absent

## §4 Polynomials — 8 / 1 / 9 (of 18) — the exact-algebra strong point
- [x] square-free factorization — `univariate.py:square_free_factorization` (Yun) (tested)
- [x] univariate factorization over ℚ — `factorize.py:factor_over_Q` (rational-root + Kronecker, exact) (tested, 18)
- [ ] multivariate factorization — absent
- [~] factorization over finite fields — `GFRing` + root enumeration in GF(p); no Berlekamp/Cantor–Zassenhaus for deg>1 irreducibles
- [x] resultant — `univariate.py:resultant` (Sylvester) + `subresultant.py:resultant_prs` (tested)
- [x] subresultant sequence — `subresultant.py:subresultant_prs` (tested, 11)
- [x] discriminant — `univariate.py:discriminant` (tested)
- [ ] content & primitive part — no `content`/`primitive_part` function
- [x] exact root multiplicity — exposed by `square_free_factorization`
- [x] Sturm sequence (real root count) — `univariate.py:sturm_chain`/`count_real_roots` (tested)
- [x] real-root isolation via rational intervals — `univariate.py:isolate_real_roots` (Sturm-bisection, exact `Fraction`) (tested)
- [ ] complex-root isolation via rational boxes — only numeric `analysis.py:poly_roots` (Durand–Kerner, float) — not ℚ-exact
- [ ] polynomial composition — absent
- [ ] polynomial decomposition — absent
- [ ] cyclotomic polynomials — absent
- [ ] sparse representation — `UPoly` is dense by construction
- [ ] modular algorithms + rational reconstruction — **OPEN by design** (`factorize.py` docstring: "no modular arithmetic, no GF(p), no Hensel")
- [x] Gröbner basis (+ Buchberger blowup) — `groebner.py:buchberger`/`reduced_groebner` + `GroebnerBudgetExceeded` fail-closed guard (tested, 16)
- [ ] elimination/block monomial orders — only flat lex/grlex/grevlex; no block/elimination order

## §5 Algebraic numbers over ℚ — 0 / 1 / 14 (of 15) — **the #1 gap: a stub, no arithmetic**
- [ ] `RootOf(p,k)` — no `RootOf` anywhere
- [ ] minimal polynomial (from arithmetic) — `AlgebraicNumber` dataclass *shape* exists (`numbers.py:33`) but no constructor; `eval.py:17` states "field arithmetic deferred (out of Wave-3 scope)"
- [ ] exact equality / [ ] ordering / [ ] add / [ ] sub / [ ] mul / [ ] div / [ ] integer powers / [ ] compare-vs-rational — all absent (dataclass shell, no methods)
- [ ] algebraic conjugates / [ ] field norm / [ ] field trace / [ ] primitive element — absent
- [ ] number field ℚ(α) / [ ] tower field — absent
- [ ] radical→RootOf / [ ] RootOf→radical — absent (no RootOf)
- [~] root-separation bounds — internal Cauchy `_root_bound` (real, used by isolation); not exposed as a pairwise API

## §8 Equation solving — 3 / 6 / 7 (of 16)
- [~] polynomial equation any degree → RootOf — `solution.py:solve` deg≥3 gives rational roots + honest `completeness="partial"` on non-rational residual; **no RootOf object** (see §5). `cas.solve` weaker (linear/quadratic radicals + rational roots)
- [ ] polynomial systems — no multivariate-system solver (Gröbner computed but never consumed to extract a variety)
- [ ] Gröbner elimination for systems — no elimination order + no system-solve caller
- [ ] triangular decomposition — absent
- [ ] rational univariate representation — absent
- [~] separate real vs complex solutions — `Domain.R`/`Domain.C` for the quadratic case only
- [ ] univariate inequality solving — no inequality kind/code anywhere
- [ ] multivariate polynomial inequalities — absent
- [ ] rational inequalities — absent
- [x] transcendental equations with declared scope — honest `HOLD` with reason for non-polynomial (never silently wrong)
- [~] equations with parameters — symbolic *linear* leading coeff handled (`ExceptionalCase`); quadratic/high-degree symbolic coeffs → `HOLD`
- [x] conditional solution sets — `ExceptionalCase` / `SolutionKind.PARAMETRIC` (linear only)
- [~] extraneous-root checking — `verify`/`verify_set` exist; doesn't detect roots introduced by clearing denominators
- [~] complete solution set — honest `completeness` field (complete for deg≤2 / all-rational; else partial)
- [x] exact multiplicity — Vieta/residual division loop (`solution.py:234-245`) + `square_free_factorization`
- [ ] solving under assumptions — `solve` does not consult the assumption engine

## §9 Symbolic integration — 0 / 3 / 12 (of 15)
- [ ] rational-function integration (Hermite) — **absent, yet `apart`+rational-`limits` sit right beside it, unused** (highest-leverage close)
- [ ] Lazard–Rioboo–Trager / [ ] algebraic-function integration — absent
- [~] Risch (declared subset) — a tiny pattern table (poly powers + exp/sin/cos of *linear* arg), honest `_Hold` otherwise (`cas.py:236-264`)
- [ ] substitution detection — only linear-argument detection (`_lin_coeff`)
- [ ] integration by parts — absent
- [ ] trig rationalization — absent
- [~] exp-log forms — `exp`/`sin`/`cos` linear-arg only; no `log`/`tan`
- [ ] definite symbolic integration — indefinite only; definite is numeric (`integrate.py`, DE quadrature)
- [ ] parameter-dependent / [ ] contour (symbolic) — contour is numeric only (`transforms.py`, `residue_sum` via numeric roots)
- [ ] convergence conditions / [ ] branch conditions — absent
- [ ] non-elementary answer objects (`Integral(...)`) — raises `_Hold` instead
- [~] verification by differentiating back — `diff` is exact and *could* verify, but no path calls it to auto-verify an integral

## §10 Symbolic limits & series — 4 / 4 / 12 (of 20)
- [x] exact symbolic limits (rational) — `poly/limits.py:rational_limit` (exact ℚ, cancel+pole order) (tested, 19)
- [x] rational-function limits all directions — same (finite/one-sided/±∞, DNE detection)
- [ ] algebraic-function limits — absent
- [~] transcendental limits — numeric only (`series.py` Richardson extrapolation / L'Hôpital)
- [ ] multivariate / [ ] path-dependent limits — absent
- [ ] asymptotic comparison / [ ] orders of growth — absent
- [~] formal power series arithmetic — exact symbolic Taylor exists (`cas.taylor`, kind `symbolic_series`) but no general series *ring* (add/mul/compose)
- [ ] symbolic Laurent (only numeric DFT) / [ ] Puiseux / [ ] series composition / [ ] reversion / [ ] asymptotic / [ ] log-asymptotic / [ ] convergence radius — absent
- [x] exact coefficient extraction (Taylor) — `cas.taylor` exact ℚ (Laurent is numeric → open)
- [~] symbolic summation — **Gosper's algorithm fully implemented+tested (`poly/summation.py`, `tests/test_summation.py`) but NOT wired to any `@kind`** (near-zero-cost close); user-facing `summation` kind is numeric finite Σ
- [x] recurrence-based summation — Gosper (implemented, unexposed)
- [x] telescoping — Gosper certificate (implemented, unexposed)
- [~] divergent-series status separate from equality — `convergence_test` HOLDs on boundary; numeric, not symbolic-equality

## §11 Special functions — 0 / 1 / 11 (of 12) — entirely numeric vs a symbolic checklist
- [ ] special functions as symbolic nodes — `FUNCS={sin,cos,tan,exp,log,ln,sqrt}` is the whole symbolic vocabulary; gamma/Bessel/etc. exist only as numeric `idm/special.py` functions
- [ ] exact special values — `special.py` is 100% `mp.mpf` numeric; no Γ(½)=√π symbolic table
- [~] recurrence identities — three-term recurrences used *internally* for evaluation (Legendre/Hermite/…), not as manipulable identity objects
- [ ] each function's ODE / [ ] derivative rules / [ ] integral rules / [ ] transformation formulas / [ ] analytic continuation / [ ] branch conventions / [ ] symbolic parameter differentiation / [ ] hypergeometric simplification / [ ] Meijer-G / [ ] elementary↔hypergeometric↔Meijer-G — all absent (the numeric library is honest & extensive: Bessel, Airy, elliptic K/E via AGM, hyp2f1, Lambert W, polylog, Hurwitz ζ — but none symbolic)

## §12 Symbolic linear algebra — 2 / 2 / 12 (of 16)
- [ ] matrices with symbolic entries — every matrix kind coerces entries to `Q(x)`; **no free-symbol path** (core CAS territory, absent)
- [ ] symbolic determinant / [ ] symbolic RREF / [ ] symbolic rank / [ ] symbolic nullspace — numeric-ℚ only
- [~] symbolic inverse with det≠0 condition — numeric singular→HOLD honesty; no symbolic-parameter condition
- [ ] characteristic polynomial over symbolic rings — Faddeev–LeVerrier requires ℚ entries
- [x] exact eigenvalues as algebraic objects (real) — `eigen.py:real_eigenvalues` (exact char-poly + Sturm isolation + multiplicity) (tested) — *complex eigenvalues not enumerated ("needs a splitting field")*
- [ ] exact eigenvectors over algebraic extensions — no eigenvector routine at all
- [ ] Jordan normal form / [ ] rational canonical form — absent
- [x] matrix minimal polynomial — `matrix_minpoly.py:minimal_polynomial` (exact, Cayley–Hamilton-bounded, back-checked) (tested)
- [ ] matrix functions from minimal polynomial — absent
- [~] symbolic matrix exponential — `matrix_exp` is a numeric truncated series, not exact/symbolic
- [ ] LU/QR/Cholesky / [ ] sparse symbolic / [ ] tensor & index contraction — absent

## §13 Symbolic ODEs — 1 / 2 / 12 (of 15)
- [x] constant-coeff linear (homogeneous), repeated & algebraic char roots — `poly/ode_linear.py:solve_linear_ode` (factors char-poly over ℚ, exact basis incl. complex/irrational-radical roots + multiplicity; honest `partial` on irreducible deg≥3) (tested, 14)
- [ ] first-order separable / [ ] exact ODE / [ ] homogeneous first-order / [ ] Bernoulli / [ ] Riccati — absent
- [ ] linear ODE variable coefficients — constant-coefficient only
- [ ] constant-coeff *inhomogeneous* — no particular-solution / undetermined-coefficients / variation-of-parameters
- [~] systems of linear ODEs — numeric RK4 only (`diffeq.py:ode_system`)
- [~] symbolic initial/boundary conditions — numeric finite-difference BVP only
- [ ] power-series / [ ] Frobenius / [ ] recurrence solution / [ ] differential-operator factorization / [ ] unevaluated DSolve object — absent

## §14 Symbolic transforms — 0 / 5 / 7 (of 12) — numeric-only vs a symbolic checklist
- [~] Laplace / [~] inverse Laplace / [~] Fourier (fwd) / [~] Mellin / [~] Z — all numeric point-evaluation (`transforms.py`, DE-quadrature / Talbot / FFT); no closed-form pair table
- [ ] inverse Fourier — not even numeric (only discrete `ifft`)
- [ ] convolution theorem — discrete convolution exists but not tied to transform-domain multiplication
- [ ] transform tables / [ ] parameter conditions / [ ] regions of convergence — absent
- [ ] distributions (Dirac/Heaviside) — zero hits anywhere
- [ ] principal-value transforms — absent

## §6 Complex numbers & branch — 0 / 3 / 10 (of 13)
- [~] build i from x²+1 / [~] exact complex algebraic numbers — `numbers.py:ComplexExact(re,im)` type exists; no construction-from-root path and no arithmetic body evidenced
- [~] re/im/conjugate — only in the Hilbert ℚ[i] module (`hilbert.py:QC`), not a general kernel operator
- [ ] symbolic abs / [ ] symbolic arg — absent
- [ ] principal branch / [ ] branch-aware log / [ ] branch-aware sqrt / [ ] branch-aware powers — `functions.py` log/sqrt are single-valued real readouts
- [ ] directed infinity — undirected `Infinity`/`ComplexInfinity` leaves only
- [~] complex infinity — `ComplexInfinity` node exists; no arithmetic uses it
- [ ] branch-cut metadata / [ ] analytic continuation — zero hits

## §15 Logical & piecewise reasoning — 0 / 3 / 7 (of 10)
- [ ] Boolean simplification — no propositional simplifier (there IS a `sat`/`truth_table` kind, but not Boolean-*expression* simplification)
- [ ] quantifier objects / [ ] quantifier elimination / [ ] CAD — zero hits
- [~] piecewise simplification — `Piecewise` bare data node; no logic operating on it
- [ ] piecewise integration / [ ] piecewise differentiation — absent
- [~] condition combination — `assumptions.py` predicate/interval reasoner (real, tested); not general propositional condition algebra
- [~] solution sets with logical conditions — `solution.py` per-branch conditions (real, tested); univariate-poly-scoped only
- [ ] exact interval arithmetic with symbolic endpoints — `interval.py` is rigorous but numeric-endpoint only

## §16 Exact constants from ℚ readouts — 1 / 3 / 3 (of 7)
- [ ] separate formal constant from numeric approximation — `pi()`/`e()` return fixed-precision numeric readouts; no distinct "Pi"/"E" symbolic leaf
- [ ] π,e,γ,ζ(3) each a distinct identity — same; all numeric
- [~] rational interval enclosure at every resolution — `Continuum.at(N)`/`.readout(ε)` is a general machine-checked resolution-enclosure machine, but not wired to π/e/γ/ζ(3) specifically
- [~] equality NOT decided by decimals — holds for the exact rungs; inapplicable to transcendental constants (they aren't formal objects yet)
- [ ] constant-relation detection → UNKNOWN/HOLD — no detector to attach it to
- [x] never promote an approximation to exact by guessing — `numbers.py:coerce_up/down` never silently promote (HOLD unless exactly representable); `Continuum.readout` HOLDs rather than fabricate — a real, enforced discipline
- [ ] integer-relation search with certificate/tier — no PSLQ/integer-relation search anywhere

## §18 Result-correctness — 6 / 3 / 3 (of 12) — the strongest section
- [~] every symbolic transform has an invariant test — `test_properties.py` enforces cross-cutting invariants over all kinds (broad, not literally every transform)
- [ ] differentiate-integral round trip — no such test (number-theory round-trips exist, not diff/integral)
- [x] substitute-solution-back — `solution.py:verify`/`verify_set` (exact substitution) (tested)
- [~] factor-expand round trip — integer-factorization round trip exists, not polynomial
- [~] cancel preserves excluded points — `rational_limit` cancels removable singularities exactly; no dedicated excluded-point regression test
- [ ] matrix-inverse verification — no `A·A⁻¹==I` self-check in the handler
- [x] Gröbner membership verification — `member_in_ideal` via `normal_form` (tested)
- [ ] algebraic-number op verification — nothing to verify (no algebraic-number arithmetic, §5)
- [ ] branch-sensitive regression — nothing to regress (no branch logic, §6)
- [x] assumptions regression suite — `tests/test_kernel_p3.py`
- [x] property-based testing — `tests/test_properties.py` (Hypothesis vs SymPy oracle)
- [x] differential testing vs external CAS as comparator only — `tests/test_differential_harness.py` (every kind cross-checked vs SymPy, disagreement=bug) + `test_adversarial_harness.py`
- [x] negative controls returning HOLD — pervasive & tested (inconsistent linear systems, singular inverse, Gröbner budget, no-plateau) — **strongest-evidenced item in the audit**

## §19 Resource control — 2 / 2 / 9 (of 13)
- [ ] expression swell / [ ] coefficient explosion — no cap outside Gröbner
- [x] Gröbner explosion — `groebner.py:GroebnerBudgetExceeded` (real cap → HOLD)
- [ ] factorization budget / [ ] simplification loop guard / [ ] recursion depth / [ ] memory budget — absent
- [~] deterministic timeout/budget — only Gröbner (step-count, not wall-clock)
- [ ] resumable computations — only `Continuum` is resolution-resumable in spirit; no general checkpoint/resume
- [ ] modular computation — no modular/Hensel path
- [~] caching — `InternTable` is deliberately request-scoped, NOT a cross-call cache
- [ ] memoization — no `lru_cache`/memoization anywhere
- [x] common-subexpression sharing — `hashcons.py` `struct_hash`+`InternTable` (request-scoped CSE)

---

## The 8 core axes (from the checklist's own summary)

| axis | status | one-line |
|---|---|---|
| 1. Canonical symbolic expression | `[~]` PARTIAL | live path canonicalizes by `tostr`; the O(1) hashcons canonicalizer exists but is wired only to the unused `nodes.py` tree |
| 2. Assumptions & domain guards | `[~]` PARTIAL | real predicate/interval reasoner; but no forward propagation and only one rewrite is actually gated |
| 3. Rational-function normalization | `[~]` PARTIAL | univariate `cancel`/`apart` exact; multivariate & excluded-point tracking absent |
| 4. Polynomial factorization & exact root isolation | `[x]` CLOSED (univariate ℚ) | factor/resultant/discriminant/Sturm/real-root isolation all exact & tested; multivariate & complex-exact roots open |
| 5. Algebraic numbers over ℚ | `[ ]` OPEN | `AlgebraicNumber` is a data-shell with no arithmetic — the single biggest gap |
| 6. Complete symbolic solving/integration/limits | `[~]` PARTIAL | rational limits & constant-coeff ODE closed; integration ~ Risch-subset only; inequalities & systems open |
| 7. Branch-aware complex algebra | `[ ]` OPEN | no branch cuts, no branch-aware log/sqrt/pow |
| 8. Verification & resource-bounded rewriting | `[~]` PARTIAL | verification infra is a genuine strength; resource control is Gröbner-only |

## What the solver systematically returns

Where a kind is implemented, the output discipline holds and is the project's real guarantee:

- **EXACT** — an exact ℚ / algebraic / `Th_coqc` result (polynomials, rational limits, real eigenvalues,
  constant-coeff ODE bases, Gröbner bases, geometric predicates).
- **CONDITIONAL** — a result plus honest scope: `completeness="partial"` with the residual stated, a
  proven error bound (`certified` readouts), or a `finite_diagnostic` numeric value with its tolerance.
- **HOLD** — an explicit refusal with a reason, never a fabricated answer (non-polynomial solve, singular
  inverse, inconsistent system, no-plateau limit, Gröbner budget exceeded).

The audit's clearest finding: the **breadth** of a general CAS is largely OPEN, but the **discipline** —
exactness where claimed, honest CONDITIONAL/HOLD everywhere else — is real, tested, and pervasive.

See [`SOLVER.md`](../SOLVER.md) for the human/AI-facing scope map, and `BACKLOG.md` (CAS-closure section)
for the prioritized todolist derived from the OPEN items above.
