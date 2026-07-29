# Changelog

All notable changes to Information Discrete Mathematics. Tiers are honest: `Th_coqc` = machine-checked
axiom-free (Coq 8.20, `Print Assumptions` = *Closed under the global context*); `finite_diagnostic` =
finite procedure cross-checked numerically; `exact` = exact over ℚ; `Open`/`+ℝ-Open` = declared open,
never dressed as a theorem.

## [Unreleased]

### WP11 (Increment 1) — linear ODEs resolve real algebraic characteristic roots at any degree
`linear_ode` previously **HELD** on an irreducible degree-≥3 characteristic factor ("roots not in
radicals"). It now resolves that factor's **real** roots exactly as algebraic numbers (WP2/WP3 `AlgReal`):
each real root ρ contributes the basis `e^{ρx}, x e^{ρx}, …` with ρ described by its exact minimal
polynomial + isolating interval. So `y‴ − 3y′ + y = 0` (char `r³−3r+1`, three real irrational roots, casus
irreducibilis) is now **fully solved** — a solution space that was entirely out of reach before. When a
degree-≥3 factor also has complex roots (e.g. char `r³−2`: real `∛2` + a complex pair), the real part is
resolved exactly and only the complex conjugate roots are left `partial` (complex-algebraic basis is a
declared later WP11 increment). Degree-1/2 factors are unchanged (golden snapshot byte-identical).


### WP13 (Increment 1) — exact eigenvalues as algebraic objects
New kind **`exact_eigenvalues`** (`exact`, → **267** kinds): the real eigenvalues of a rational matrix as
**exact algebraic objects with multiplicity** — no Durand–Kerner. The characteristic polynomial is exact
(Faddeev–LeVerrier over ℚ, existing `eigen.characteristic_polynomial`); its real roots are isolated as
`AlgReal` (WP2/WP3). Reports `num_complex` and `completeness` (`complete` iff all eigenvalues real, else
`real_complete`). E.g. `[[2,1],[1,2]]` → 1, 3 exact; `[[0,1],[1,1]]` → the golden pair `(1±√5)/2` (min-poly
`x²−x−1`); a rotation `[[0,-1],[1,0]]` → 0 real, 2 complex; `diag(2,2,3)` → eigenvalue 2 (mult 2), 3.
Hard char-poly factorization fails closed (HOLD), never hangs. The existing numeric `eigenvalues` kind is
unchanged. Exact complex eigenvalues are a later increment.
### WP6 (Increment 1) — `symbolic_solve` returns the complete exact real solution set
For a univariate ℚ-polynomial equation, `symbolic_solve` (via `idm.kernel.cas.solve`) previously returned
**only rational roots** at degree ≥3 and told you to "use poly_roots" — silently **losing every irrational
real root**. It now returns the **complete exact real solution set** through WP2/WP3's `AlgReal`: each real
root as an exact algebraic object (minimal polynomial + isolating interval) with its multiplicity, plus an
honest `num_complex` and `completeness` (`complete` iff all roots real, else `real_complete`). E.g.
`x³−2` now returns `∛2` exactly (min-poly `x³−2`) with 2 complex; `(x−1)(x−2)(x−3)` returns 1, 2, 3 complete.
Degrees 1–2 keep their exact radical forms; a hard high-degree factorization fails closed (`partial` + note),
never hangs. No lost roots. (Existing behavior for degree ≤2 is byte-identical — golden snapshot unchanged.)


### WP3 (Increment 1) — exact real root objects, no Durand–Kerner
Builds on WP2's `AlgReal`. New kind **`all_real_roots`** (`exact`, → **266** kinds): given a ℚ-polynomial,
it returns **every real root as an exact algebraic object with its multiplicity** (irreducible
factorization over ℚ + Sturm isolation), sorted, verified by substitute-back — **no reduction to
Durand–Kerner floats**. It also reports `num_complex = deg − Σ(real multiplicities)` and a `completeness`
of `complete` (all roots real) or `real_complete` (all real roots found exactly; the remaining complex
conjugate pairs are a declared later WP3 increment). `AlgReal.real_roots_with_multiplicity` exposes the
same at the kernel level. This meets the WP3 real-part closure criterion: a degree-n polynomial yields all
its real roots with multiplicity, exactly. Registry 265 → 266, counts synced across all docs + gates.


### WP2 — exact real algebraic-number arithmetic (the #1 CAS gap, now open)
The `AlgebraicNumber` type was a data-shell with no arithmetic. **`idm/kernel/poly/algebraic.py`** makes a
root of a ℚ-polynomial a genuinely computable exact object — `AlgReal(min_poly, isolating_interval)`:
- construct from a ℚ-polynomial + real-root index (Sturm isolation); `+ − × ÷`, integer powers; exact
  ordering / equality / sign — **all exact over ℚ, never a float**. The minimal polynomial of `α∘β` comes
  from a power-basis dependency in ℚ(α,β) (linear algebra over ℚ), then the correct root is re-isolated by
  Sturm bisection. Division by zero and out-of-range roots **HOLD**, never guess.
- **WP2 closure criterion met:** every result **substitutes back** to satisfy its own minimal polynomial
  exactly (e.g. `(2^{1/3})³ = 2`, `√2+√3` → `x⁴−10x²+1`, `√2·√3` → `x²−6`, `1/√2` → `x²−½`). Verified in
  `tests/test_algebraic.py`, including a **differential cross-check against SymPy's `minimal_polynomial`**
  (comparator only).
- New solver kinds (**265** total): `real_root` (k-th exact real root of a ℚ-polynomial) and
  `algebraic_arith` (exact `add/sub/mul/div` of two algebraic reals) — both `exact`, returning the
  minimal polynomial + isolating interval + substitute-back certificate.
- This is the root of Track A that unblocks WP3 (`RootOf`), WP6 (complete univariate solving), WP11
  (degree-≥3 ODE roots), WP13 (exact eigenvalues). *Increment 1 is **real** algebraic numbers; complex,
  number fields ℚ(α), towers, and ℚ(x) are declared later WP2 increments.*
- Registry count 263 → **265**; all kind-count references synced across README / SOLVER.md / API.md /
  capabilities.json / the manifest gate (the founder's "one continuous system" — a stale 259 in a few
  docs was corrected in the same pass).

### The continuum as a first-class ℚ PRIMITIVE — `idm.continuum.Continuum`
Founder question (2026-07-29): *can we build a ℚ-primitive function that behaves like the ℝ-rung
continuum?* Yes — the operational form of "the continuum is a readout of the discrete" (Part XX /
machine-checked FTCC bridge). A `Continuum` is a resolution-indexed **exact-ℚ** readout `g : N → ℚ`,
never an ℝ object:
- `.at(N)` — the exact ℚ readout at declared resolution N (the primitive operation).
- `.readout(ε)` — tier-honest: `CERTIFIED` **only** on a PROVEN tail bound (`geometric`'s exact
  rᴺ⁺¹/(1−r), or a bound propagated through `+`/`−` by the triangle law); a bare observed plateau is
  `finite_diagnostic` (measured, not proven beyond N — a flat-then-diverge sequence lands here, never
  falsely CERTIFIED); `HOLD` where no plateau exists. It never emits a completed limit.
- a **ℚ-algebra** closed and exact pointwise (`+ − ×`, scalar, `compose`): `(a+b).at(N) == a.at(N)+b.at(N)`,
  so continuum-readouts are a commutative ℚ-algebra you compute with directly, ℝ never a primitive.
- **Formal core → 194** (from 189): **`IDM_Continuum.v`** machine-checks the algebra's soundness
  axiom-free over ℚ — pointwise homomorphism (`radd_at`/`rmul_at`), commutativity, a constant's zero gap,
  and the key **`gap_subadditive`** (|Δ(g+h)| ≤ |Δg|+|Δh|, so summing two plateauing continua still
  plateaus — the algebra can't silently break `.readout`'s honesty).
- `idm/continuum.py` + `tests/test_continuum.py` (11 tests) + discovery pointer in `idm/README.md`.
- **Anti-ℝ-slide guard** `tests/test_continuum_no_R_slide.py` — enforces (in CI, not just intent) that no
  doc/code surface positively claims ℝ was constructed / is a primitive / that the completed limit is
  emitted as a value. Negation-aware, so the honest fenced phrasings pass ("ℝ is never a primitive", "the
  completed real stays +ℝ-Open"); it also pins the module's fence markers and asserts every non-HOLD
  readout keeps the `+ℝ-Open` fence and returns only exact ℚ. Closes the "language drift" vigilance point.

### The ℚ-computability law — the +ℝ-Open Hilbert frontier now splits its two truths
Founder principle (2026-07-29): *if an ℝ-rung quantity is actually COMPUTED, it is computed on ℚ — so
it must carry a ℚ tier, not a blanket `+ℝ-Open`.* Audit of the 5 frontier kinds found 4 of them do
compute an exact ℚ readout (partial energy `Σ|xₖ|²`, the Cauchy tail `x_N`, the finite ONB) that was
buried under one uniform `+ℝ-Open` tag — an under-claim. Fixed with a **two-tier readout** (the
continuum-maya split, Part XX), without weakening the anti-overclaim fence:
- `idm/hilbert_open.py` now returns `computed_core` (the exact ℚ quantity, with its OWN honest tier:
  `Th_coqc` for the ℓ²/L² partial energy, `exact` for the Cauchy/ONB readouts) **and** `open_tail` (the
  completed limit / whole-space object, staying `+ℝ-Open`). The fence is unchanged: still
  `status:+R_OPEN`, still no top-level `value`, kind-level tier never `Th_coqc`. `infinite_spectral`
  honestly reports `computed_core: None` — it is the one kind that computes nothing on ℚ.
- **Formal core → 189** (from 184): **`IDM_HilbertReadout.v`** machine-checks the ℚ core the
  `Th_coqc` claim rests on — the unweighted `partial_energy` (`nonneg` · exact-`app`-additive ·
  `monotone` in N) and the **weighted** quadrature `weighted_energy` (`nonneg` under measure weights
  wᵢ≥0 · exact-`app`-additive), all axiom-free over ℚ. This *is* "computable on ℚ" made machine-checked.
- **Honest L² tier (reviewer-caught).** `L2_readout` computes a *weighted* quadrature `Σ wᵢ|f(xᵢ)|²`; its
  `computed_core` is `Th_coqc` **only when the weights form a measure (wᵢ ≥ 0)** — the hypothesis of
  `weighted_energy_nonneg`. With a signed weight (not a measure, value can go negative) it honestly drops
  to `exact` and cites no witness, instead of claiming a nonneg witness whose premise fails.
- Guard test `tests/test_hilbert.py::test_two_tier_readout_gives_the_q_core_its_honest_tier` — every
  computing kind's `computed_core` carries an `exact`/`Th_coqc` tier, any `Th_coqc` cites a real in-tree
  witness, and `open_tail` stays `+ℝ-Open`. Golden snapshot regenerated (additive; 5 kinds).

## [1.4.1]

Quality + integrity release: acts on a world-class multi-discipline review, pays down architectural
debt, and adds the algebraic atom of the inertia boundary-readout — all backward-compatible.

### Formal core → 184 machine-checked axiom-free theorems (from 177)
- **`IDM_Schur.v`** — the exact Schur/boundary congruence over ℚ (`A = Mᵀ·diag(a, c−b²/a)·M` for a 2×2
  block, the `b²/a` cancellation), the algebraic atom of Haynsworth inertia-additivity — machine-checks,
  in this framework's own semantics, that eliminating a boundary node produces exactly the Schur
  complement. Fenced: Sylvester's sign-count invariance stays `+ℝ-Open`.

### P5 (inertia lower bound) — recast in the information language
- `docs/P46_P5_lower_bound_analysis.md` rewritten **purely readout-first** (removing a borrowed
  classical-complexity frame): P5 = "does a BOUNDARY readout require producing the VOLUME?"; the READOUT
  rule predicts against `Ω(fill*)`; info-P5 is a boundary-retention (Declaration-Bound-on-the-separator)
  question, still `+ℝ-Open`. No conjecture formalized.

### World-class review — acted on
- Fixed 4 verified defects: package `__version__` drift (was 1.3.0), stale "127 theorems" docs
  (→ live count), CLI `describe`/`list` now report the **honest runtime tier** (mirroring solve()'s
  downgrade), and `retained_spectral/README` now points to the discovery layer ("do not infer scope").
- New **CI drift gates**: version single-sourced (idm == pyproject == manifest) and documented theorem
  counts (README / formal-README / **SKILL.md**) gated against `formal/verify.sh`.

### Debt paid down
- `idm/solve.py` split from a 924-line monolith into `idm/_solve_core.py` + **30 per-domain modules** +
  a 44-line dispatch facade — verified **byte-identical** for all 263 kinds (golden snapshot).

## [1.4.0]

### Discovery layer — the repository now describes itself (humans + AI)
- **`capabilities.json`** — a machine-readable manifest **generated** from the live `idm.solve` registry
  by `tools/gen_capabilities.py` (all 263 problem kinds classified into 11 domains, none dropped/duplicated).
- **CI gate** `tests/test_capabilities_manifest.py` — fails if `total_problem_kinds != len(idm.kinds())`,
  if any kind is unclassified, or if the manifest is not byte-identical to a fresh regeneration. Adding or
  removing an API without regenerating now breaks CI.
- **CLI discovery** — `python -m idm list | kinds | describe <kind> | example <kind>` (new `idm` console
  script), grounded in the registry; `example` returns a real test fixture or honestly reports none.
- **AI-first docs** — `AI_START_HERE.md` ("do not infer capability from a single module" + a discovery
  order), `llms.txt`, `API_INDEX.md`, a README capability-map + 5-level-platform, and per-folder READMEs.
- **Reproducibility** — `Makefile` (`install`/`discover`/`test`/`prove`/`formal`/`benchmark`/`verify-all`),
  a build-verified core `Dockerfile`, `docker/{spectral,hpc,formal}` profiles + `docker-compose.yml`
  (the PETSc/SLEPc HPC image is authored, honestly marked not-build-verified).
- **Benchmark honesty** — `docs/BENCHMARK_CLAIMS.md` (each claim: scope · native API · peer · run file ·
  committed result artifact · correctness gate · **excluded** claims) and `docs/knowledge_graph.json`
  (claim → API → implementation → tests → benchmark → theory).

### Formal core — grew from 107 to 177 machine-checked, axiom-free theorems
- **`IDM_ReadoutMinimality.v`** — the minimal value-set of a signed readout (Theorem 1: ≥3 values forced,
  the third a neutral) and the four-valued algebra `{+,−,0,⊥}` with `0` (determinate) distinct from `⊥`
  (unresolved) on both the involution and the information-order axes.
- **`IDM_ResolvedCount.v`** — the resolved (four-valued) inertia readout: `⊥` arises **only** from a
  positive declared resolution (a fact about the instrument), `0` **only** at exact resolution on a true
  balance (a fact about the object). Shipped API `retained_spectral/inertia.py: resolved_count_below`
  closes the silent-failure gap (a floored pivot is now reported `⊥`, not folded into `n₀`).
- **`IDM_EquivariantReadout.v`** — the necessary condition behind P1 (general-group minimal readout):
  `Stab_X(x) ⊆ Stab_V(r x)`, equality under faithfulness. The cardinality formula stays **Conjecture P1**.
- **`IDM_Apriori.v`** — the Richardson **a-priori** stability certificate: an order-`p` method has
  contraction ratio `ρ = 2⁻ᵖ` known up front (feeds `refine_stable`), no gap monitoring.
- **`IDM_SetsFunctions.v`** (Th 10.2) and **`IDM_FirstOrder.v`** (finite first-order `⊨_λ` decidable) —
  the v-proofs edition: two `Th_coqc`-eligible sketches converted to real witnesses.
- **`IDM_ApproxCount.v`** — an honest `Ω(log(n/r))` lower bound for approximate deferred counting;
  **P7 (`Θ(n/r)`) and P8 (randomized) stay Open**, not formalized.

### Certified computation
- **Multi-dimensional quadrature** — `idm.certified.integral_nd` (tensor-trapezoid, reuses the
  dimension-agnostic `refine_stable` theorem); certifies with bound `0` when the readout is exact.
- **Richardson a-priori** — `idm.certified.richardson_apriori_{ratio,bound,certified}`.

### Documentation / honesty
- New textbook §10.14 "named-Open-problems frontier" (Hauptvermutung, strong LLN, topos completeness,
  exact π/φ) — each stated, predicted, fenced; no closure claimed.
- Corrected a pre-existing overclaim: a §10.7 "machine-checked witness `formal/InfoCausalPartialOrder_attempt.v`"
  citing a file not in-tree — downgraded to `Th_coqc`-eligible with an honesty note.
- §10.9 renumbered to §10.13 (consistency).

## [1.3.0]
- Genuinely installable self-contained wheel (`pip install .` works from outside the source tree);
  P2 CAS-grade kernel ops (matrix_solve, rational_limit, linear_ode, groebner_basis); the Five Core
  Theorems written into `THEOREM.md` at referee grade with local self-proving witnesses.
