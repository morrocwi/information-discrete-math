# BACKLOG — Information Discrete Mathematics (only work that strengthens the math)

Filtered pending work, newest-planning first. Each item states **why it strengthens the framework** and
its **tier target**. Housekeeping/cosmetic items that do not make the mathematics stronger are excluded
by design. Extensibility contract: see `INDEX.md`; every new chapter derives from `δ_R`/`L_R`/Part VII
operators, tier-tagged, with an executed `validation/*.py` block before prose.

## Tier 1 — full chapters (CLOSED 2026-07-26, v1.7–v1.8; validated 34/34, 4-agent reviewed)

- [x] **Part XVI — Measure theory & functional analysis.** Discrete measure `μ_λ=I_ε(indicator)`
      (§10.6) → σ-additivity as a retained count; `L_R` functional calculus / spectral theorem on the
      finite `ℚ`-space (§13.2); Hilbert-space completeness stays `+ℝ-Open`. *Strengthens:* gives analysis
      its measure-theoretic floor without a continuum σ-algebra. Tier: `Th_coqc-elig` + `+ℝ-Open` fence.
- [x] **Part XVII — Category theory in the readout vocabulary.** `G_λ` = idempotent reflector, `E=Ẽ∘G_λ`
      = Kan-extension/comma factorization, sets-as-fibers = Grothendieck fibration, `=_λ` = coequalizer,
      admissible descriptions = setoids (all sketched in §10.7). *Strengthens:* makes the substrate's
      universal properties explicit; topos completeness stays `+ℝ-Open`. Tier: `Th_coqc-elig`/`Dr`.
- [x] **Part XVIII — Statistics & inference.** Retained-frequency estimation; a hypothesis test **is** a
      `Verdict(ACCEPT/HOLD/BLOCK)` (ties to `idm_discipline`); Bayesian update = retained reweighting;
      confidence = declared-resolution interval. *Strengthens:* closes the gap above probability (§10.6)
      and unifies inference with the fail-closed verdict discipline. Tier: `finite_diagnostic`/`Dr`.
- [x] **Part XIX — Optimization.** Gradient = `D_ε`; convexity = a retained second-difference sign;
      Lagrange multipliers = constrained retained stationarity; linear programming exact over `ℚ`;
      root/optimum via obstruction-zeroing (`solve_obstruction`, `idm_discipline`). *Strengthens:* gives
      the framework its optimization chapter, grounded in tools it already ships. Tier: `Th_coqc-elig`.

## Capstone — the continuum-maya bridge (construct the continuum *as a readout*, then compute with it)

- [x] **Part XX — The continuum-maya bridge — DONE (v1.11).** Written as Part XX; `Λ` map + faithfulness
      (exact FTCC core `Th_coqc` `formal/IDM_Bridge.v`; numeric 100/100) + maya clause. Original scope: *Is it possible to build a formal
      bridge that CONSTRUCTS a continuum layer from the discrete — a continuum that is explicitly a
      readout/appearance (maya), not an ultimate object — and then compute continuum results with it,
      identically?* Yes; the pieces exist and this makes the two-truths a theorem, not a stance:
      - **The construction (discrete → continuum-maya):** the number ladder already does the object
        side (`ℝ` = regular Cauchy of `ℚ`, §III). The bridge adds the *operational* side: a map
        `Λ: (discrete finite-ε data) → (continuum-appearance value)` defined as the **A8-stable readout**
        of the finite-ε computation (`limit_eps`/Euler–Maclaurin/Richardson). `Λ` is total on
        A8-stable inputs and **refuses** (HOLD) where no plateau exists — so the continuum it builds is
        exactly the *computable appearance*, never a completed non-readout.
      - **Faithfulness (compute continuum identically):** prove `Λ` reproduces the classical continuum
        operation on every A8-stable case — derivative, integral, limit, ODE, special value — which is
        already *witnessed* at 100/100 (Appendix E). The bridge upgrades that empirical 100/100 into a
        stated **faithfulness theorem**: `Λ(discrete op) = classical continuum op` wherever the latter
        exists, with the divergence set = exactly the `+ℝ-Open` non-readouts.
      - **Maya clause (honesty):** the constructed continuum is labelled a **readout of the discrete**
        (conventional truth, §0.3), never the ultimate object; the bridge is one-way faithful
        (discrete → appearance) and *predicts* the readout on the Open frontier rather than closing it.
      *Strengthens:* turns the framework's central claim ("the continuum is a readout of the discrete")
      from a discipline/stance into a constructive, testable bridge with a faithfulness theorem — the
      natural capstone. Founder request 2026-07-26.

## Tier 2 — strengthen warrant (proof work; raises existing tiers, no new breadth)

- [x] **Prove the keystone Th 5.1 `B(Φ,Φ)=I(Φ)` in Coq.** DONE (v1.10): `formal/IDM_Keystone.v`,
      `keystone_B_eq_I` (edge assembly `ΦᵀL_RΦ = Σ w(Φi−Φj)²`) + `keystone_nonneg` (L_R PSD), both
      axiom-free. Single most-cited result upgraded in-progress → `Th_coqc` (§5.1/§10.8/§13.2/Roadmap).
- [~] **Machine-check the `Th_coqc-elig` claims → real `.v` witnesses.** DONE (v1.9): `formal/IDM_FiniteWitnesses.v`
      proves 5 axiom-free — Th 10.1 Kuratowski pair injectivity (§10.1), handshake (§15.2), pigeonhole
      (§15.3), finite-Yoneda (§17.2), semiring distributivity (§12.2). DONE too (v1.13): §10.2
      cardinality Th 10.3–10.5 + §12.3 Lagrange (cyclic) — `formal/IDM_FiniteWitnesses2.v`. DONE (v1.16-v1.19): §10.3 `⊨_λ`, §10.4 RDL non-explosion (`IDM_Logic.v`); §4.4/§16.2 Cauchy-Schwarz/
      §16.1/§12.1/§12.2 (`IDM_FiniteWitnesses3.v`); **discrete matrix library `IDM_Matrix.v`** (matrix
      algebra + Laplacian symmetric/rowsum/kernel §15.2 + twirl parameter-reduction §13.4). 26 Coq
      theorems total, all axiom-free (`bash formal/verify.sh`). RECLASSIFIED (frontier, not warrant
      work): real spectral theorem + DPI entropic-form + general Cauchy-Binet matrix-tree = `+ℝ-Open`
      / need heavy machinery — honestly declared, not left as false 'elig'. Nothing tractable remains. *Turns "elig" into `Th_coqc`.*
- [x] **v-proofs edition.** Convert the §10.1–10.6 results-first sketches to checked proofs (the
      edition-note promise). DONE — both tractable sketches now carry real witnesses: **Th 10.2**
      (function ≅ functional-relation coincidence, the "biggest not-standalone blocker") →
      `formal/IDM_SetsFunctions.v`; **Th 10.6 first-order `⊨_λ`** (quantifier-over-finite-domain
      Tarski recursion, `∀↦forallb`/`∃↦existsb`, sound+complete+decidable) → `formal/IDM_FirstOrder.v`.
      Both `Th_coqc`-elig → `Th_coqc`, axiom-free. What remains is genuinely `+ℝ-Open` (NOT convertible,
      correctly fenced not dressed as `Th_coqc`): §10.5 `ε→0` real-analysis quantifier, §10.6
      completed-measure limit — they quantify over a completed continuum.

## Tier 3 — frontier chapters (write as *declared* `+ℝ-Open`; honesty, not new closure)

Writing these as explicit "open by design" chapters strengthens completeness/honesty without claiming
closure — they need the completed continuum, which the philosophy treats as a readout, not a premise.

- [x] **Topology / manifolds / differential geometry** — DONE (v1.11): Part XXI decisive stance +
      paradox dissolution (Banach–Tarski, discrete Gauss–Bonnet), computed 16/16.
- [x] **PDE** — DONE (v1.11): Part XXI, Navier–Stokes/blow-up dissolved, finite-ε heat/wave well-posed.
- [x] **Named open problems** chapter — DONE (§10.14 "The named-Open-problems frontier, in depth"):
      Hauptvermutung, strong LLN, topos completeness, exact `π`/`φ` objects — each stated, our
      readout-first stance predicted, and honestly fenced (declared `+ℝ-Open`, no closure claimed).

## Tier 4 — discipline hardening (extracted-but-not-yet-ported from cpg_math MathSolver)

- [x] **Port `consumer_guard` into `idm_discipline.py`** — DONE (v1.13): `VerdictNotAccepted` + `unwrap`
      (payload read only after ACCEPT, else raises) + `resource_admissibility` (pre-tick OOM gate). Self-
      check extended.


## New extraction tasks (queued — translate to information language first, then formalize)

- [x] **Discrete Jacobian, sharper version — DONE (v1.23).** §8.8 + validation/discrete_jacobian.py (9/9): exact constant det J_F=−2, 3-to-1 readout collision, retention lift restores injectivity, told as retained-sensitivity D_ε. ORIGINAL: Extract the discrete Jacobian/retention math from
      `~/Downloads/jacobian_retention_clean_two_turns.m` (exact polynomial images in readout space
      `(P,Q,R)`; retention lift `(P,Q,ψ)`) and `~/Downloads/URR_C_MASTER_0_4_DETAILED.yaml` (URR-C:
      linear hidden-elimination / return-kernel exact algebra). Restate as the **retained sensitivity
      operator** `D_ε` of a readout to its source (§7.0 language first), fold the sharper exact-algebra
      form into Part VIII (discrete calculus), tier-honest. Goal: a Jacobian that does **not** rely on a
      conjecture — a finite exact-algebra readout, per the DGG-conjecture-is-false lesson (finite
      discrete counterexamples settle what continuum conjectures leave open).
- [x] **readout_genesis math harvest — DONE (v1.24).** Pure-math results extracted to formal/IDM_Harvest.v (axiom-free): repeated_event_zero (C=−C⇒C=0), odd_from_cyclic_closure (cyclic closure ⇒ k odd ⇒ 3), sym_skew_reconstruct + skew_diag_zero (operator = self-adjoint metric + load-free skew), folded §4.4/§13.2. Remaining SM-domain .v files are physics, not pure math. ORIGINAL: Scan `~/ANSE.ASIA/readout_genesis` for machine-checked / exact
      mathematical results not yet in the textbook; extract and fold in (info-language first, tier-honest).

## Housekeeping (tracked, low priority — consistency not math)

- [x] Part X: `§10.9` sat physically after §10.10–10.12; renumbered to `§10.13` and updated all 18
      internal `(§10.9)` pointers to `(§10.13)` (consistency review item — DONE). Also corrected a
      pre-existing stale "machine-checked" citation in §10.7 (`formal/InfoCausalPartialOrder_attempt.v`,
      not in-tree → downgraded to `Th_coqc`-eligible with an honesty note).


## CAS closure — the 14 work packages (founder audit 2026-07-29, refines the raw checklist)

**Framing correction.** The raw per-item audit (`docs/CAS_CLOSURE_CHECKLIST.md`) counts *public-CAS
reachability* — so it marks OPEN many things that already **exist in the kernel but aren't wired to the
public `symbolic_*` surface**. A founder pass over every `formal/verify.sh` Coq file + the kernel +
registry + `THEOREM.md` reclassified these. So the real remaining CAS work is **not ~150 things to build
from scratch** — it is **14 work packages** over **four root layers**.

**Already implemented in the kernel — do NOT rebuild, only wire/complete:** immutable expression tree,
basic canonical ordering, `Relation`, `Piecewise`, unevaluated `Derivative/Integral/Limit`, the assumption
object, guarded rewrite, exact polynomial arithmetic, factorization over ℚ, square-free factorization,
resultant, discriminant, Sturm root isolation, rational-function `cancel`/`apart`/`together`, reduced
Gröbner basis, exact linear-system solve, rational-function limits, **Gosper summation**, matrix minimal
polynomial, constant-coefficient homogeneous ODE.

**Four root layers (everything below rolls up to these):**
1. ▢ Move the public CAS onto one kernel.
2. ▢ Complete algebraic / complex exact arithmetic.
3. ▢ Add reasoning: assumptions + rewrites + conditions.
4. ▢ Connect that core to close solve / calculus / linear-algebra **with certificates**.

**Explicitly NOT in this list** (theory-open or numeric-engineering, not CAS blockers): P1 general-group
cardinality, P7/P8 approximate-counting bounds, Sylvester/Haynsworth analytic extensions, adaptive grids.

---

### WP1 — Retire the dual symbolic engine *(root 1)*
Public `symbolic_*` kinds still run on the legacy tuple tree while kernel-v2's typed `Expr` (calculus
nodes representable but not the wire format) sits unused; the legacy numeric evaluator isn't on the tiered
evaluator yet. → parser builds kernel-v2 `Expr` directly; migrate `simplify/expand/diff/integrate/solve/
series/evaluate` off the tuple tree; per-node serializer/round-trip; `idm.solve`/API/REST/CLI return one
typed result; delete legacy paths after migration.
**Close when:** no public CAS operation calls the legacy `idm.kernel.cas` tuple tree.
*(Includes the confirmed correctness bug: `cas.py:_from_ast` `Q(float)` makes `parse("0.1")` a binary-float
fraction, not `1/10` — fix to `Fraction(str(x))` for decimal literals during the parser migration.)*

### WP2 — Make `AlgebraicNumber` a genuinely computable number *(root 2, #1 gap)*
Type exists (`AlgebraicNumber`, `ComplexExact`) but arithmetic / precision-escalation / re-isolation /
field ops are deferred; coefficient tower is only ℤ/ℚ/GF(p). → construct from (min-poly, isolating
interval/box); exact equality + ordering of real algebraic numbers; `+ − × ÷`; re-isolation after ops;
conjugates + stable root index; exact complex algebraic arithmetic; fields ℚ(α), tower ℚ(α₁…αₙ),
rational-function field ℚ(x₁…xₙ); explicit coercion ℚ ↔ algebraic ↔ complex-exact ↔ certified ball.
**Close when:** every root of ℚ[x] is an exact object that adds/multiplies/divides/compares and
substitutes back to check the equation.

### WP3 — Wire root isolation → exact root objects *(root 2)*
Sturm chains + rational-interval real-root isolation exist but return `(l,h]` pairs, not usable objects;
complex roots aren't enumerated (no splitting field). → `RootOf(p,k)` node; interval → `AlgebraicNumber`;
multiplicity kept separate from distinct-root index; complex-root isolation via rational rectangles/disks;
all complex algebraic roots per degree; radical conversion when expressible, stay `RootOf` otherwise.
**Close when:** a degree-n polynomial returns all n roots with multiplicity — no reduction to
Durand–Kerner floats.

### WP4 — Assumption engine reasons over *expressions*, not just symbols *(root 3)*
Today it's closed-vocabulary forward chaining that under-infers to `UNKNOWN`; `domain_of_expr` handles only
named cases (`log(x)`, `sqrt(x)`, bare-symbol powers), compound args deferred. → infer sign/domain of a
compound expression; propagate through `+ − × ÷ Pow`; reason from polynomial/rational inequalities;
condition algebra (`And/Or/Not`, implication, simplification, equivalence/contradiction checks); combine
denominator/log/root/inverse conditions; emit `Piecewise` when a transform is only conditionally valid;
separate real/complex branch domains.
**Close when:** every transformation returns `EXACT` / `CONDITIONAL` / `HOLD` with checkable conditions —
no string-condition placeholders.

### WP5 — Make the rewrite engine the real simplification core *(root 3)*
Structural positional matching + loop budget + `PARTIAL` exist; commutative matching doesn't, and the only
ruleset is the one guarded nested-power collapse (constant-folding/like-term/distribution/antiderivative
still live in legacy). → associative, commutative, and AC matching; sequence wildcards for n-ary
`Add/Mul`; a shared normalization ruleset (poly/rational via kernel poly); trig/exp/log/radical rules;
condition- and `Piecewise`-producing rewrites; cost-directed simplification; a proof trace citing each rule
+ assumption; migrate legacy `simplify/expand` into the rule engine.

### WP6 — Close univariate equation solving *(root 4)*
`solution.py` does symbolic-linear, numeric-coefficient quadratic, and rational high-degree roots, but
HOLDs on symbolic quadratic/high-degree coefficients and returns only partial sets when roots are
irrational. → symbolic quadratic coefficients with discriminant case-split; all degrees via
`AlgebraicNumber`/`RootOf`; full multiplicity; exact verification of radical/algebraic roots; symbolic
leading-coefficient degeneration at every degree; parameterized solution sets; rational equations with
excluded points; supported transcendental classes (exp/log/trig); periodic solution families; completeness
proven per class-algorithm.
**Close when:** every univariate polynomial over ℚ gets `completeness="complete"`, and out-of-class
equations return an unevaluated/conditional object — never a lost root.

### WP7 — Multivariate algebra & system solving *(root 4)*
Reduced Gröbner basis + normal form + ideal membership exist, but nothing turns a basis into a solution
set; systems/inequalities are deferred. → multivariate factorization over ℚ; elimination API from a lex
Gröbner basis; zero-dimensional system solving; triangular decomposition or RUR; algebraic-coordinate
solution tuples; positive-dimensional parametric varieties; dimension + consistency detection; polynomial
and rational inequalities (with excluded sets); real decomposition/CAD or a finite-ℚ equivalent;
quantifier elimination; exact verification of each component.
**Close when:** a Gröbner basis produces a complete `SolutionSet` or a precise obstruction.

### WP8 — Close symbolic integration *(root 4)*
Public integrator does polynomial powers + `exp/sin/cos` of some linear arguments, HOLDs otherwise — even
though factorization + partial fractions already exist. → bridge expression rational functions to `apart`;
full rational-function integration (incl. repeated irreducible quadratics, log/arctan forms with domain
conditions); Hermite reduction; algebraic-function integration; substitution detection; integration-by-
parts strategy; exp-log elementary classes; definite symbolic integration with convergence/branch
conditions; return an `Integral` node for the unresolved part; verify by exact differentiation.
*(Not every integral must be elementary — but the unsolved part must remain an exact symbolic object.)*

### WP9 — Symbolic limits, formal series & asymptotics *(root 4)*
Exact rational-function limits exist but take coefficient lists; the public `limit_*`/`lhopital` are
numeric Richardson/finite-difference; Laurent series uses numeric FFT. → expression→rational-limit bridge;
algebraic-function limits; exact order-of-zero/pole; transcendental local limits; symbolic one-sided
conditions; multivariate/path-dependent limits; a formal power-series ring; exact Laurent; Puiseux; series
composition & reversion; asymptotic scales incl. log/exp; exact coefficient extraction; a remainder/order
object.
**Close when:** a symbolic limit/series needs no sampling when the expression is in a decidable class.

### WP10 — Wire & extend symbolic summation *(root 4)*
Gosper is real and returns an exact rational certificate for indefinite hypergeometric sums, but it's an
internal polynomial-ratio API (no definite sums / creative telescoping / multi-term recurrences). →
expression→hypergeometric-ratio translator; expose Gosper via the unified solver; definite-sum endpoints;
telescoping; rational/polynomial summation; Zeilberger creative telescoping; recurrence derivation +
solving; parameter conditions + singular-index exclusions; exact certificate check `R(n+1)r(n)−R(n)=1`.

### WP11 — Close symbolic ODEs *(root 4)*
Exact solver handles only linear constant-coefficient homogeneous ODEs and HOLDs at an irreducible
characteristic factor of degree ≥3 (blocked on WP2/WP3). → use algebraic roots at all degrees instead of
HOLD; inhomogeneous constant-coefficient; initial/boundary conditions; linear systems; first-order
separable / exact / Bernoulli / homogeneous / Riccati classes; variable-coefficient linear classes;
power-series / Frobenius; differential-operator factorization; unevaluated object out-of-class;
substitute-back verification. *(Numeric RK4/BVP/PDE already exist and do not close this gap.)*

### WP12 — Close symbolic transforms *(root 4)*
Laplace/Mellin/Fourier/inverse-Laplace exposed today are numeric quadrature / finite-window / Talbot
contour. → symbolic Laplace + inverse; Fourier + inverse; Mellin; Z-transform; rule tables (scaling,
shift, differentiation, convolution); regions of convergence; parameter/domain conditions; Heaviside /
delta / distribution nodes; an unevaluated transform object when not closed.

### WP13 — Exact symbolic linear algebra & spectral algebra *(root 4)*
Exact rational matrix ops + complete rational solve + exact minimal polynomial exist, but real eigenvalues
are isolating intervals, complex eigenvalues aren't built, and public `eigenvalues` uses Durand–Kerner. →
matrices over algebraic-number fields; symbolic-parameter matrices; exact eigenvalues as algebraic objects
(real + complex); exact eigenspaces over extensions; generalized eigenspaces; Jordan normal form; rational
canonical form; invariant factors; matrix functions reduced mod minimal polynomial; symbolic rank/nullspace
with parameter case-splits; spectral decomposition returning genuine exact/conditional objects.

### WP14 — Verification & theorem coverage of the CAS layer itself *(root 4)*
194 Coq theorems cover FOLD/DECISION, finite logic, discrete calculus, certificates, matrices, geometry,
readout laws — but not that each CAS transform is correct; the dispatcher grants `Th_coqc` only to kinds
pointing at a named theorem (others downgrade to `exact`). The goal is *not* proving every Python line, but:
a central certificate format for factorization; algebraic-root certificates; Gröbner verification via
S-polynomial reductions; a solution-completeness certificate; integration certificate (differentiate-back);
summation certificate (finite-difference-back); ODE certificate (substitute-back); matrix-decomposition
reconstruction certificate; formalized shared correctness lemmas for algebraic-number ops; map each exact
solver to a named theorem or a checkable certificate; a consistency gate between tier, implementation, and
claimed theorem.
**Close when:** every `exact` result carries a reconstruction/residual witness a small independent verifier
can check, and every `Th_coqc` points to a theorem that genuinely matches it.

---

*The raw per-item evidence base is `docs/CAS_CLOSURE_CHECKLIST.md`. The verification stack (§18 there) and
the EXACT/CONDITIONAL/HOLD discipline are already strong; these 14 packages are the path to a full CAS
without abandoning that discipline.*
